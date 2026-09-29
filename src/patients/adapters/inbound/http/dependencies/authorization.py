from collections.abc import Callable

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from patients.adapters.outbound.users.user_http_client import UserHttpClient
from patients.infrastructure.config.settings import settings

security = HTTPBearer()


def require_permission(permission_name: str) -> Callable[..., None]:
    def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> None:
        user_client = UserHttpClient(settings.users_service_url)

        try:
            user = user_client.get_authorization_user(
                credentials.credentials,
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ):
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail="Invalid or unauthorized user credentials",
                ) from exc
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Users service is currently unavailable",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Error connecting to users service",
            ) from exc

        if not user.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        role_id = user.get("role_id")

        if role_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned role",
            )

        try:
            response = httpx.get(
                f"{settings.roles_service_url}/roles/"
                f"{role_id}/permissions/{permission_name}",
                timeout=5.0,
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )

            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Roles service returned an error",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Error connecting to roles service",
            ) from exc

        if not data.get("has_permission", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    return dependency

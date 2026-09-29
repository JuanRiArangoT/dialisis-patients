from collections.abc import Callable

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from patients.adapters.outbound.users.user_http_client import UserHttpClient
from patients.infrastructure.config.settings import settings

security = HTTPBearer()


def require_permission(permission_name: str) -> Callable:
    def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> None:
        user_client = UserHttpClient(settings.users_service_url)

        user = user_client.get_authorization_user(
            credentials.credentials,
        )

        if not user["is_active"]:
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

        if not response.json()["has_permission"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    return dependency   
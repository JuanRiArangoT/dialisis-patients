from functools import lru_cache
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from patients.infrastructure.config.settings import settings

security = HTTPBearer()


@lru_cache
def get_jwks_client() -> PyJWKClient:
    domain = settings.auth0_domain.strip().rstrip("/")
    return PyJWKClient(f"https://{domain}/.well-known/jwks.json")


def verify_token(token: str) -> dict[str, Any]:
    domain = settings.auth0_domain.strip().rstrip("/")

    try:
        signing_key = get_jwks_client().get_signing_key_from_jwt(token)

        payload: dict[str, Any] = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.auth0_api_audience,
            issuer=f"https://{domain}/",
        )

        return payload

    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    return verify_token(credentials.credentials)


CurrentUser = Annotated[dict[str, Any], Depends(get_current_user)]

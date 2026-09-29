from typing import Any

import httpx


class UserHttpClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def get_authorization_user(
        self,
        token: str,
    ) -> dict[str, Any]:
        response = httpx.get(
            f"{self._base_url}/users/authorization/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5.0,
        )

        response.raise_for_status()

        return response.json()

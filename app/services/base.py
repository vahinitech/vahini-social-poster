from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from typing import Any

import requests
from authlib.integrations.requests_client import OAuth2Session


@dataclass(slots=True)
class AuthResult:
    connected: bool
    message: str
    authorization_url: str | None = None
    token_payload: dict[str, str] | None = None


@dataclass(slots=True)
class ServiceResult:
    platform: str
    success: bool
    response: dict[str, Any]


class BaseSocialService:
    platform = "platform"
    display_name = "Platform"
    scope = ""
    default_authorize_url = ""
    default_token_url = ""
    default_api_base_url = "https://api.example.com"

    def __init__(self) -> None:
        prefix = self.platform.upper()
        self.client_id = getenv(f"{prefix}_CLIENT_ID", "")
        self.client_secret = getenv(f"{prefix}_CLIENT_SECRET", "")
        self.authorize_url = getenv(f"{prefix}_AUTHORIZE_URL", self.default_authorize_url)
        self.token_url = getenv(f"{prefix}_TOKEN_URL", self.default_token_url)
        self.api_base_url = getenv(f"{prefix}_API_BASE_URL", self.default_api_base_url)
        self.session = requests.Session()

    def authenticate(self, redirect_uri: str, session_store: dict[str, str]) -> AuthResult:
        if self.client_id and self.client_secret and self.authorize_url:
            client = OAuth2Session(
                self.client_id,
                self.client_secret,
                redirect_uri=redirect_uri,
                scope=self.scope,
            )
            authorization_url, state = client.create_authorization_url(self.authorize_url)
            session_store[f"{self.platform}_oauth_state"] = state
            return AuthResult(
                connected=False,
                message=f"Redirecting to {self.display_name} for OAuth approval.",
                authorization_url=authorization_url,
            )

        return AuthResult(
            connected=True,
            message=(
                f"{self.display_name} credentials are not configured yet, so a local placeholder "
                "connection was saved instead."
            ),
            token_payload=self._placeholder_token(),
        )

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict[str, str]:
        if not (self.client_id and self.client_secret and self.token_url):
            return self._placeholder_token(code)

        client = OAuth2Session(
            self.client_id,
            self.client_secret,
            redirect_uri=redirect_uri,
            scope=self.scope,
        )
        token = client.fetch_token(self.token_url, code=code)
        return {
            "access_token": token.get("access_token", ""),
            "refresh_token": token.get("refresh_token", ""),
        }

    def refresh_token(self, refresh_token: str) -> dict[str, str]:
        if not refresh_token:
            return self._placeholder_token("refresh")
        return {
            "access_token": f"{self.platform}-refreshed-access-token",
            "refresh_token": refresh_token,
        }

    def create_post(self, content: str, image_path: str | None, access_token: str) -> ServiceResult:
        payload = {
            "content": content,
            "image_path": image_path,
            "has_access_token": bool(access_token),
        }
        prepared_request = self.session.prepare_request(
            requests.Request("POST", self.api_base_url, json=payload)
        )
        return ServiceResult(
            platform=self.platform,
            success=True,
            response={
                "message": f"Placeholder {self.display_name} post prepared successfully.",
                "request_method": prepared_request.method,
                "request_url": prepared_request.url,
                "payload": payload,
            },
        )

    def _placeholder_token(self, seed: str | None = None) -> dict[str, str]:
        suffix = seed or "local"
        return {
            "access_token": f"{self.platform}-{suffix}-access-token",
            "refresh_token": f"{self.platform}-{suffix}-refresh-token",
        }

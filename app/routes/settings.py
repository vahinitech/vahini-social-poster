from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, session, url_for

from app.models.repository import delete_account, list_accounts, upsert_account
from app.services import PLATFORM_LABELS, get_service_map


settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.get("/")
def settings_page():
    return render_template(
        "settings.html",
        accounts=list_accounts(),
        platform_labels=PLATFORM_LABELS,
    )


@settings_bp.post("/connect/<platform>")
def connect_account(platform: str):
    service = get_service_map().get(platform)
    if service is None:
        return render_template(
            "components/settings_response.html",
            accounts=list_accounts(),
            platform_labels=PLATFORM_LABELS,
            notification_message="Unknown platform.",
            notification_tone="danger",
        ), 404

    callback_url = url_for("settings.oauth_callback", platform=platform, _external=True)
    result = service.authenticate(callback_url, session)
    if result.authorization_url:
        return redirect(result.authorization_url)

    assert result.token_payload is not None
    upsert_account(platform, result.token_payload["access_token"], result.token_payload["refresh_token"])
    return render_template(
        "components/settings_response.html",
        accounts=list_accounts(),
        platform_labels=PLATFORM_LABELS,
        notification_message=result.message,
        notification_tone="success",
    )


@settings_bp.get("/oauth/<platform>/callback")
def oauth_callback(platform: str):
    service = get_service_map().get(platform)
    if service is None:
        return redirect(url_for("settings.settings_page"))

    code = request.args.get("code", "local-callback")
    token = service.exchange_code_for_token(code, url_for("settings.oauth_callback", platform=platform, _external=True))
    upsert_account(platform, token.get("access_token", ""), token.get("refresh_token", ""))
    return redirect(url_for("settings.settings_page"))


@settings_bp.post("/disconnect/<platform>")
def disconnect_account(platform: str):
    delete_account(platform)
    return render_template(
        "components/settings_response.html",
        accounts=list_accounts(),
        platform_labels=PLATFORM_LABELS,
        notification_message=f"Disconnected {PLATFORM_LABELS.get(platform, platform)}.",
        notification_tone="muted",
    )

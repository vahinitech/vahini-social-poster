from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from flask import Blueprint, Response, current_app, render_template, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.models.repository import (
    count_drafts,
    create_post_log,
    get_account,
    list_accounts,
    list_recent_posts,
    save_post,
)
from app.services import PLATFORM_LABELS, get_service_map


compose_bp = Blueprint("compose", __name__, url_prefix="/compose")


def _save_uploaded_image(upload: FileStorage | None) -> str | None:
    if upload is None or not upload.filename:
        return None

    filename = secure_filename(upload.filename)
    if not filename:
        return None

    uploads_directory = Path(current_app.config["UPLOAD_FOLDER"])
    uploads_directory.mkdir(parents=True, exist_ok=True)
    saved_name = f"{uuid4().hex}-{filename}"
    upload.save(uploads_directory / saved_name)
    return f"uploads/{saved_name}"


@compose_bp.get("/")
def compose_page():
    return render_template(
        "compose.html",
        platform_labels=PLATFORM_LABELS,
        accounts=list_accounts(),
    )


@compose_bp.post("/draft")
def save_draft():
    content = request.form.get("content", "").strip()
    draft_id = request.form.get("draft_id", type=int)
    image_path = _save_uploaded_image(request.files.get("image"))

    if not content and image_path is None and draft_id is None:
        return render_template(
            "components/compose_response.html",
            notification_message="Start typing to create a draft.",
            notification_tone="muted",
            draft_id=None,
            accounts=list_accounts(),
            recent_posts=list_recent_posts(),
            draft_count=count_drafts(),
        )

    draft = save_post(content=content, image_path=image_path, status="draft", post_id=draft_id)
    return render_template(
        "components/compose_response.html",
        notification_message="Draft saved locally.",
        notification_tone="success",
        draft_id=draft.id,
        accounts=list_accounts(),
        recent_posts=list_recent_posts(),
        draft_count=count_drafts(),
    )


@compose_bp.post("/autosave")
def autosave_draft():
    content = request.form.get("content", "").strip()
    draft_id = request.form.get("draft_id", type=int)
    if not content and draft_id is None:
        return ("", 204)

    draft = save_post(content=content, image_path=None, status="draft", post_id=draft_id)
    return render_template(
        "components/compose_response.html",
        notification_message="Draft autosaved.",
        notification_tone="muted",
        draft_id=draft.id,
        accounts=list_accounts(),
        recent_posts=list_recent_posts(),
        draft_count=count_drafts(),
    )


@compose_bp.post("/publish")
def publish_post() -> str | Response:
    content = request.form.get("content", "").strip()
    selected_platforms = request.form.getlist("platforms")
    draft_id = request.form.get("draft_id", type=int)
    image_path = _save_uploaded_image(request.files.get("image"))

    if not content:
        return render_template(
            "components/compose_response.html",
            notification_message="Post content is required before publishing.",
            notification_tone="danger",
            draft_id=draft_id,
            accounts=list_accounts(),
            recent_posts=list_recent_posts(),
            draft_count=count_drafts(),
        )

    if not selected_platforms:
        return render_template(
            "components/compose_response.html",
            notification_message="Select at least one platform.",
            notification_tone="danger",
            draft_id=draft_id,
            accounts=list_accounts(),
            recent_posts=list_recent_posts(),
            draft_count=count_drafts(),
        )

    services = get_service_map()
    missing_accounts = [platform for platform in selected_platforms if get_account(platform) is None]
    if missing_accounts:
        labels = ", ".join(PLATFORM_LABELS[platform] for platform in missing_accounts)
        return render_template(
            "components/compose_response.html",
            notification_message=f"Connect these accounts first: {labels}.",
            notification_tone="danger",
            draft_id=draft_id,
            accounts=list_accounts(),
            recent_posts=list_recent_posts(),
            draft_count=count_drafts(),
        )

    successful_posts = 0
    for platform in selected_platforms:
        account = get_account(platform)
        service = services[platform]
        result = service.create_post(content=content, image_path=image_path, access_token=account.access_token)
        create_post_log(platform=platform, response=result.response, success=result.success)
        successful_posts += int(result.success)

    final_status = "published" if successful_posts == len(selected_platforms) else "failed"
    save_post(content=content, image_path=image_path, status=final_status, post_id=draft_id)

    return render_template(
        "components/compose_response.html",
        notification_message=f"Published to {successful_posts} platform(s).",
        notification_tone="success" if successful_posts else "danger",
        draft_id=None,
        accounts=list_accounts(),
        recent_posts=list_recent_posts(),
        draft_count=count_drafts(),
    )

from __future__ import annotations

from flask import Blueprint, render_template

from app.models.repository import count_drafts, list_accounts, list_recent_posts


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
def home():
    accounts = list_accounts()
    recent_posts = list_recent_posts()
    return render_template(
        "dashboard.html",
        accounts=accounts,
        recent_posts=recent_posts,
        draft_count=count_drafts(),
    )


@dashboard_bp.get("/partials/recent-posts")
def recent_posts_partial():
    return render_template("components/recent_posts.html", recent_posts=list_recent_posts())

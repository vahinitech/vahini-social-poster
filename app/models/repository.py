from __future__ import annotations

import json
import sqlite3
from typing import Iterable

from flask import current_app

from app.database.db import get_db
from app.models.entities import Account, Post, PostLog
from app.security import TokenCipher


def _account_from_row(row: sqlite3.Row) -> Account:
    cipher = TokenCipher(current_app.config["SECRET_KEY"])
    return Account(
        id=row["id"],
        platform=row["platform"],
        access_token=cipher.decrypt(row["access_token"]),
        refresh_token=cipher.decrypt(row["refresh_token"]),
        created_at=row["created_at"],
    )


def _post_from_row(row: sqlite3.Row) -> Post:
    return Post(
        id=row["id"],
        content=row["content"],
        image_path=row["image_path"],
        status=row["status"],
        created_at=row["created_at"],
    )


def _log_from_row(row: sqlite3.Row) -> PostLog:
    return PostLog(
        id=row["id"],
        platform=row["platform"],
        response=row["response"],
        success=bool(row["success"]),
        created_at=row["created_at"],
    )


def list_accounts() -> list[Account]:
    rows = get_db().execute("SELECT * FROM accounts ORDER BY platform ASC").fetchall()
    return [_account_from_row(row) for row in rows]


def get_account(platform: str) -> Account | None:
    row = get_db().execute("SELECT * FROM accounts WHERE platform = ?", (platform,)).fetchone()
    return _account_from_row(row) if row else None


def upsert_account(platform: str, access_token: str, refresh_token: str | None) -> None:
    cipher = TokenCipher(current_app.config["SECRET_KEY"])
    get_db().execute(
        """
        INSERT INTO accounts (platform, access_token, refresh_token)
        VALUES (?, ?, ?)
        ON CONFLICT(platform) DO UPDATE SET
            access_token = excluded.access_token,
            refresh_token = excluded.refresh_token,
            created_at = CURRENT_TIMESTAMP
        """,
        (platform, cipher.encrypt(access_token), cipher.encrypt(refresh_token)),
    )
    get_db().commit()


def delete_account(platform: str) -> None:
    get_db().execute("DELETE FROM accounts WHERE platform = ?", (platform,))
    get_db().commit()


def list_recent_posts(limit: int = 5) -> list[Post]:
    rows = get_db().execute(
        "SELECT * FROM posts ORDER BY datetime(created_at) DESC, id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [_post_from_row(row) for row in rows]


def count_drafts() -> int:
    row = get_db().execute("SELECT COUNT(*) AS draft_count FROM posts WHERE status = 'draft'").fetchone()
    return int(row["draft_count"])


def save_post(content: str, image_path: str | None, status: str, post_id: int | None = None) -> Post:
    database = get_db()
    if post_id is None:
        cursor = database.execute(
            "INSERT INTO posts (content, image_path, status) VALUES (?, ?, ?)",
            (content, image_path, status),
        )
        database.commit()
        return get_post(int(cursor.lastrowid))

    existing = get_post(post_id)
    if existing is None:
        raise ValueError(f"Unknown post id: {post_id}")

    final_image_path = image_path if image_path is not None else existing.image_path
    database.execute(
        "UPDATE posts SET content = ?, image_path = ?, status = ? WHERE id = ?",
        (content, final_image_path, status, post_id),
    )
    database.commit()
    return get_post(post_id)


def get_post(post_id: int) -> Post | None:
    row = get_db().execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    return _post_from_row(row) if row else None


def create_post_log(platform: str, response: dict[str, object], success: bool) -> PostLog:
    database = get_db()
    cursor = database.execute(
        "INSERT INTO post_logs (platform, response, success) VALUES (?, ?, ?)",
        (platform, json.dumps(response, sort_keys=True), int(success)),
    )
    database.commit()
    row = database.execute("SELECT * FROM post_logs WHERE id = ?", (int(cursor.lastrowid),)).fetchone()
    return _log_from_row(row)


def list_post_logs() -> list[PostLog]:
    rows = get_db().execute("SELECT * FROM post_logs ORDER BY datetime(created_at) DESC, id DESC").fetchall()
    return [_log_from_row(row) for row in rows]


def has_connected_accounts(platforms: Iterable[str]) -> bool:
    placeholders = ",".join("?" for _ in platforms)
    selected = tuple(platforms)
    if not selected:
        return False
    row = get_db().execute(
        f"SELECT COUNT(*) AS total FROM accounts WHERE platform IN ({placeholders})",
        selected,
    ).fetchone()
    return int(row["total"]) == len(selected)

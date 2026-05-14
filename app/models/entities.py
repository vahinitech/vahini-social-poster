from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Account:
    id: int
    platform: str
    access_token: str
    refresh_token: str
    created_at: str


@dataclass(slots=True)
class Post:
    id: int
    content: str
    image_path: str | None
    status: str
    created_at: str


@dataclass(slots=True)
class PostLog:
    id: int
    platform: str
    response: str
    success: bool
    created_at: str

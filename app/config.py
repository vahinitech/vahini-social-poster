from __future__ import annotations

import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent
    DATABASE_PATH = Path(os.getenv("VAHINI_DATABASE_PATH", BASE_DIR / "database" / "social_poster.db"))
    UPLOAD_FOLDER = Path(os.getenv("VAHINI_UPLOAD_FOLDER", BASE_DIR / "static" / "uploads"))
    SECRET_KEY = os.getenv("VAHINI_SECRET_KEY", "development-secret-change-me")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    AUTO_OPEN_BROWSER = os.getenv("VAHINI_AUTO_OPEN_BROWSER", "true").lower() == "true"
    HOST = os.getenv("VAHINI_HOST", "127.0.0.1")
    PORT = int(os.getenv("VAHINI_PORT", "5000"))

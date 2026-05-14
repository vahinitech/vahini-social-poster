from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def create_app(test_config: Mapping[str, Any] | None = None):
    from app.app import create_app as flask_create_app

    return flask_create_app(dict(test_config) if test_config is not None else None)


__all__ = ["create_app"]

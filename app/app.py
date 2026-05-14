from __future__ import annotations

import logging
import threading
import webbrowser
from pathlib import Path

from flask import Flask

from app.config import Config
from app.database.db import init_app as init_db_app
from app.extensions import oauth
from app.routes import compose_bp, dashboard_bp, settings_bp
from app.services import PLATFORM_LABELS


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    Path(app.config["DATABASE_PATH"]).parent.mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    oauth.init_app(app)
    init_db_app(app)

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(compose_bp)
    app.register_blueprint(settings_bp)
    app.jinja_env.globals["platform_labels"] = PLATFORM_LABELS

    return app


app = create_app()


def _open_browser(host: str, port: int) -> None:
    webbrowser.open(f"http://{host}:{port}")


if __name__ == "__main__":
    host = app.config["HOST"]
    port = app.config["PORT"]
    if app.config.get("AUTO_OPEN_BROWSER", False):
        threading.Timer(1.0, _open_browser, args=(host, port)).start()
    app.run(host=host, port=port, debug=False)

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.app import create_app


class SocialPosterAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        self.upload_folder = Path(self.temp_dir.name) / "uploads"
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE_PATH": self.database_path,
                "UPLOAD_FOLDER": self.upload_folder,
                "SECRET_KEY": "test-secret-key",
                "AUTO_OPEN_BROWSER": False,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _connect_platform(self, platform: str) -> None:
        response = self.client.post(f"/settings/connect/{platform}")
        self.assertEqual(response.status_code, 200)

    def test_pages_render(self) -> None:
        for path in ("/", "/compose/", "/settings/"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Vahini Social Poster", response.data)

    def test_save_draft_updates_dashboard(self) -> None:
        response = self.client.post("/compose/draft", data={"content": "Draft from test"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Draft saved locally", response.data)

        dashboard = self.client.get("/")
        self.assertIn(b"Draft from test", dashboard.data)
        self.assertIn(b">1<", dashboard.data)

    def test_publish_creates_post_logs(self) -> None:
        self._connect_platform("linkedin")
        self._connect_platform("twitter")

        response = self.client.post(
            "/compose/publish",
            data={"content": "Launch update", "platforms": ["linkedin", "twitter"]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Published to 2 platform", response.data)

        with sqlite3.connect(self.database_path) as connection:
            post_count = connection.execute("SELECT COUNT(*) FROM posts WHERE status = 'published'").fetchone()[0]
            log_count = connection.execute("SELECT COUNT(*) FROM post_logs").fetchone()[0]

        self.assertEqual(post_count, 1)
        self.assertEqual(log_count, 2)

    def test_disconnect_removes_account(self) -> None:
        self._connect_platform("facebook")
        response = self.client.post("/settings/disconnect/facebook")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Disconnected Facebook Pages", response.data)


if __name__ == "__main__":
    unittest.main()

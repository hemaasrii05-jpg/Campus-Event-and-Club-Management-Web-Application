import unittest
from pathlib import Path

from app import app


class DatabaseConfigTests(unittest.TestCase):
    def test_database_uri_uses_instance_folder(self):
        expected_db = (Path(__file__).resolve().parents[1] / "instance" / "database.db").as_posix()
        self.assertIn(expected_db, app.config["SQLALCHEMY_DATABASE_URI"])


if __name__ == "__main__":
    unittest.main()

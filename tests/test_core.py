import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import db
import scripts


class TestCoreLogic(unittest.TestCase):
    def test_resource_path_uses_module_directory(self):
        expected_base = os.path.dirname(os.path.abspath(scripts.__file__))
        expected = os.path.join(expected_base, "data/icon.ico")
        self.assertEqual(scripts.resource_path("data/icon.ico"), expected)

    def test_populate_flags_database_syncs_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            flags_root = os.path.join(tmpdir, "data", "flags")
            for continent in ["africa", "america", "asia", "europe", "oceania"]:
                os.makedirs(os.path.join(flags_root, continent), exist_ok=True)

            open(os.path.join(flags_root, "europe", "italy.png"), "wb").close()
            open(os.path.join(flags_root, "asia", "japan.png"), "wb").close()

            db_path = os.path.join(tmpdir, "flags.db")

            with patch("db.resource_path", side_effect=lambda rel: os.path.join(tmpdir, rel)):
                db.populate_flags_database(db_path)

            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT country, continent FROM flags ORDER BY country")
            rows = cur.fetchall()
            conn.close()
            self.assertEqual(rows, [("italy", "europe"), ("japan", "asia")])

            os.remove(os.path.join(flags_root, "asia", "japan.png"))
            open(os.path.join(flags_root, "europe", "france.png"), "wb").close()

            with patch("db.resource_path", side_effect=lambda rel: os.path.join(tmpdir, rel)):
                db.populate_flags_database(db_path)

            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT country, continent FROM flags ORDER BY country")
            rows = cur.fetchall()
            conn.close()

            self.assertEqual(rows, [("france", "europe"), ("italy", "europe")])

    def test_scores_insert_and_filter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "scores.db")
            db.create_scores_table(db_path)

            db.insert_score(
                db_path,
                12,
                ["italy", "france"],
                ["spain"],
                "europe",
                "normal",
                0,
                2,
                {"completion": True},
            )
            db.insert_score(
                db_path,
                5,
                ["japan", "india"],
                ["china", "china"],
                "europe",
                "endless",
                0,
                8,
                {},
            )

            all_scores = db.get_top_scores(db_path, "europe", "all", limit=10)
            self.assertEqual(len(all_scores), 2)
            self.assertEqual(all_scores[0][0], 12)

            normal_scores = db.get_top_scores(db_path, "europe", "normal", limit=10)
            self.assertEqual(len(normal_scores), 1)
            self.assertEqual(normal_scores[0][5], "normal")


if __name__ == "__main__":
    unittest.main()

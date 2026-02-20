import unittest

from flagguessr.application.use_cases import GameService
from flagguessr.domain.models import GameConfig, GuessStatus


class FakeScoreRepository:
    def __init__(self):
        self.saved = []

    def initialize(self):
        return None

    def save_score(self, session, time_taken, flags_shown, mode_data):
        self.saved.append(
            {
                "score": session.score,
                "mode": session.mode.value,
                "map": session.map_name,
                "time_taken": time_taken,
                "flags_shown": flags_shown,
                "mode_data": mode_data,
            }
        )

    def get_top_scores(self, gamemode, filter_mode="all", limit=10):
        return []


class FakeFlagCatalog:
    def __init__(self, countries_map):
        self.countries_map = countries_map

    def initialize(self):
        return None

    def load_countries(self, map_name):
        return self.countries_map

    def load_flag_images(self, countries, size):
        return {name: object() for name in countries.keys()}


class TestGameService(unittest.TestCase):
    def test_start_game_normal_initializes_session(self):
        score_repo = FakeScoreRepository()
        flags = FakeFlagCatalog({"italy": "europe", "france": "europe"})
        service = GameService(score_repo, flags, GameConfig())

        result = service.start_game("normal", "europe", (100, 60), now_ms=1234)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.running_game)
        self.assertEqual(result.running_game.session.mode.value, "normal")
        self.assertEqual(result.running_game.session.lives, 3)
        self.assertEqual(len(result.running_game.session.countries_sequence), 1)

    def test_submit_guess_can_finish_normal_mode(self):
        score_repo = FakeScoreRepository()
        flags = FakeFlagCatalog({"italy": "europe"})
        service = GameService(score_repo, flags, GameConfig())

        start = service.start_game("normal", "europe", (100, 60), now_ms=1000)
        self.assertTrue(start.success)
        running_game = start.running_game

        result = service.submit_guess(running_game, "italy", now_ms=1100)

        self.assertEqual(result.status, GuessStatus.VICTORY)
        self.assertEqual(len(score_repo.saved), 1)
        self.assertTrue(score_repo.saved[0]["mode_data"].get("completion"))

    def test_submit_guess_wrong_can_end_game(self):
        score_repo = FakeScoreRepository()
        flags = FakeFlagCatalog({"italy": "europe"})
        service = GameService(score_repo, flags, GameConfig(max_lives=1))

        start = service.start_game("endless", "europe", (100, 60), now_ms=1000)
        self.assertTrue(start.success)
        running_game = start.running_game

        result = service.submit_guess(running_game, "spain", now_ms=1200)

        self.assertEqual(result.status, GuessStatus.GAME_OVER)
        self.assertEqual(len(score_repo.saved), 1)


if __name__ == "__main__":
    unittest.main()

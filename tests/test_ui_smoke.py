import os
import unittest

# Use headless video backend for CI/local smoke tests without opening windows.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

try:
    import pygame
except ModuleNotFoundError:
    pygame = None

if pygame is not None:
    from flagguessr.presentation.gui import GUI


class TestUISmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if pygame is None:
            raise unittest.SkipTest("pygame is not installed in this environment")
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        if pygame is not None:
            pygame.quit()

    def setUp(self):
        try:
            self.ui = GUI()
        except pygame.error as exc:
            self.skipTest(f"Pygame display unavailable for smoke test: {exc}")

    def test_render_main_screens_without_crashing(self):
        sample_flags = {"italy": pygame.Surface(self.ui.getFlagSize())}
        sample_scores = [
            (
                10,
                "2026-02-20 10:00:00",
                "europe",
                "italy,france",
                "spain",
                "normal",
                0,
                2,
                '{"completion": true}',
            )
        ]

        self.ui.showSplashScreen()
        self.ui.showModeSelection(["global", "europe", "oceania", "africa", "asia", "america"])
        self.ui.showModeSelectionScreen()
        self.ui.showGame("italy", 5, sample_flags, 3, "normal", 0, 60, 1)
        self.ui.showRankings(sample_scores, "europe")
        self.ui.showGameOver(5, ["spain", "france"], "europe")
        self.ui.showVictory(10, "europe")

        # Ensure event queue stays healthy after multiple renders.
        pygame.event.pump()


if __name__ == "__main__":
    unittest.main()

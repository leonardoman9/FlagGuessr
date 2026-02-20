from __future__ import annotations

import pygame

from flagguessr.infrastructure import audio
from flagguessr.application.use_cases import GameService
from flagguessr.domain.models import GameConfig
from flagguessr.infrastructure.flag_catalog import SQLiteFlagCatalog
from flagguessr.infrastructure.repositories import SQLiteScoreRepository
from flagguessr.presentation.controller import GameController
from flagguessr.presentation.gui import GUI
from flagguessr.shared.paths import get_user_data_path, resource_path


def create_game_controller() -> GameController:
    pygame.init()
    try:
        icon = pygame.image.load(resource_path("data/icon.ico"))
        pygame.display.set_icon(icon)
    except Exception:
        pass

    scores_db_path = get_user_data_path("scores.db")
    flags_db_path = get_user_data_path("flags.db")

    score_repository = SQLiteScoreRepository(scores_db_path)
    flag_catalog = SQLiteFlagCatalog(flags_db_path)
    config = GameConfig()

    game_service = GameService(
        score_repository=score_repository,
        flag_catalog=flag_catalog,
        config=config,
    )
    game_service.initialize()

    if not audio.init_mixer():
        print("Warning: Audio mixer failed to initialize. Music will not work.")
    audio.play_music(random_song=True)

    game_gui = GUI()
    return GameController(
        gui=game_gui,
        game_service=game_service,
        config=config,
        gamemodes=["global", "europe", "oceania", "africa", "asia", "america"],
    )

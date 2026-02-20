from __future__ import annotations

from typing import Type

import pygame

from flagguessr.application.use_cases import GameService
from flagguessr.domain.models import GameConfig, RunningGame
from flagguessr.presentation.states import BaseState, SplashState


class GameController:
    def __init__(
        self,
        gui,
        game_service: GameService,
        config: GameConfig,
        gamemodes: list[str],
    ):
        self.gui = gui
        self.game_service = game_service
        self.config = config
        self.gamemodes = gamemodes

        self.running = True
        self.active_game: RunningGame | None = None
        self.previous_screen_for_rankings: str | None = None

        self.clock = pygame.time.Clock()
        self.state: BaseState = SplashState(self)
        self.state.enter()

    def change_state(self, state_cls: Type[BaseState]) -> None:
        self.state = state_cls(self)
        self.state.enter()

    def run(self) -> None:
        while self.running:
            self.state.update()
            self.state.render()

            for event in pygame.event.get():
                self.state.handle_event(event)

            self.clock.tick(60)

        pygame.quit()

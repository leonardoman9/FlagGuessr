from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from flagguessr.domain.models import GameMode, GuessStatus

if TYPE_CHECKING:
    from flagguessr.presentation.controller import GameController


class BaseState:
    name = "base"

    def __init__(self, controller: "GameController"):
        self.controller = controller

    def enter(self) -> None:
        return None

    def update(self) -> None:
        return None

    def render(self) -> None:
        return None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.controller.running = False


class SplashState(BaseState):
    name = "splash"

    def render(self) -> None:
        self.controller.gui.showSplashScreen()

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        mouse_pos = pygame.mouse.get_pos()
        gui = self.controller.gui
        gui.set_mouse_x_y(mouse_pos)

        if gui.handle_music_controls_click(mouse_pos):
            return

        if gui.play_button_rect.collidepoint(gui.get_mouse_x(), gui.get_mouse_y()):
            self.controller.change_state(ModeSelectionState)
            return

        if gui.splash_rankings_button_rect.collidepoint(gui.get_mouse_x(), gui.get_mouse_y()):
            self.controller.previous_screen_for_rankings = "splash"
            self.controller.change_state(RankingsMapSelectionState)
            return

        if gui.splash_quit_button_rect.collidepoint(gui.get_mouse_x(), gui.get_mouse_y()):
            self.controller.running = False


class ModeSelectionState(BaseState):
    name = "mode_selection"

    def enter(self) -> None:
        self.controller.gui.clear_error_message()

    def render(self) -> None:
        self.controller.gui.showModeSelection(self.controller.gamemodes)

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        if event.type not in [
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
            pygame.MOUSEWHEEL,
        ]:
            return

        mouse_pos = pygame.mouse.get_pos()
        gui = self.controller.gui
        gui.set_mouse_x_y(mouse_pos)

        result = gui.handle_mode_selection_click(event, mouse_pos)
        if not result:
            return

        if result == "back":
            self.controller.change_state(SplashState)
            return

        mode_value, map_name = result
        gui.set_input_text("")
        gui.clear_error_message()

        start_result = self.controller.game_service.start_game(
            mode_value=mode_value,
            map_name=map_name,
            flag_size=gui.getFlagSize(),
            now_ms=pygame.time.get_ticks(),
        )
        if not start_result.success:
            gui.show_error_message(start_result.error)
            return

        self.controller.active_game = start_result.running_game
        self.controller.change_state(GamePlayState)


class GamePlayState(BaseState):
    name = "game"

    def update(self) -> None:
        running_game = self.controller.active_game
        if not running_game:
            self.controller.gui.show_error_message("No game loaded. Returning to mode selection.")
            self.controller.change_state(ModeSelectionState)
            return

        timed_out = self.controller.game_service.tick_game(running_game, pygame.time.get_ticks())
        if timed_out:
            self.controller.change_state(GameOverState)

    def render(self) -> None:
        running_game = self.controller.active_game
        if not running_game:
            return

        session = running_game.session
        self.controller.gui.showGame(
            running_game.current_country,
            session.score,
            running_game.flag_images,
            session.lives,
            session.mode.value,
            session.start_time_ms,
            self.controller.config.blitz_time_limit_seconds,
            session.flags_shown_count,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        running_game = self.controller.active_game
        if not running_game:
            return

        gui = self.controller.gui

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            gui.set_mouse_x_y(mouse_pos)
            if gui.get_game_exit_button_rect().collidepoint(mouse_pos):
                self.controller.change_state(SplashState)
                return
            gui.handle_game_music_click(mouse_pos)
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_RETURN:
            result = self.controller.game_service.submit_guess(
                running_game,
                gui.get_input_text(),
                pygame.time.get_ticks(),
            )

            if result.clear_input:
                gui.set_input_text("")

            if result.clear_error:
                gui.clear_error_message()
            elif result.message:
                gui.show_error_message(result.message)

            if result.status == GuessStatus.VICTORY:
                self.controller.change_state(VictoryState)
            elif result.status == GuessStatus.GAME_OVER:
                self.controller.change_state(GameOverState)
            return

        if event.key == pygame.K_BACKSPACE:
            gui.set_input_text(gui.get_input_text()[:-1])
            return

        if event.unicode:
            gui.set_input_text(gui.get_input_text() + event.unicode)


class GameOverState(BaseState):
    name = "game_over"

    def render(self) -> None:
        running_game = self.controller.active_game
        if not running_game:
            self.controller.change_state(SplashState)
            return

        session = running_game.session
        self.controller.gui.showGameOver(session.score, session.wrong_countries, session.map_name)

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        running_game = self.controller.active_game
        if not running_game:
            self.controller.change_state(SplashState)
            return

        gui = self.controller.gui
        gui.set_mouse_x_y(pygame.mouse.get_pos())

        if gui.get_quit_button_rect().collidepoint(gui.get_x_y()):
            self.controller.running = False
            return

        if gui.get_rankings_button_rect().collidepoint(gui.get_x_y()):
            self.controller.previous_screen_for_rankings = "game_over"
            gui.set_rankings_gamemode(running_game.session.map_name)
            self.controller.change_state(RankingsState)
            return

        if gui.main_menu_button_rect.collidepoint(gui.get_x_y()):
            self.controller.change_state(SplashState)


class VictoryState(BaseState):
    name = "victory"

    def render(self) -> None:
        running_game = self.controller.active_game
        if not running_game:
            self.controller.change_state(SplashState)
            return

        session = running_game.session
        self.controller.gui.showVictory(session.score, session.map_name)

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        running_game = self.controller.active_game
        if not running_game:
            self.controller.change_state(SplashState)
            return

        gui = self.controller.gui
        gui.set_mouse_x_y(pygame.mouse.get_pos())

        if gui.get_quit_button_rect().collidepoint(gui.get_x_y()):
            self.controller.running = False
            return

        if gui.get_rankings_button_rect().collidepoint(gui.get_x_y()):
            self.controller.previous_screen_for_rankings = "victory"
            gui.set_rankings_gamemode(running_game.session.map_name)
            self.controller.change_state(RankingsState)
            return

        if gui.main_menu_button_rect.collidepoint(gui.get_x_y()):
            self.controller.change_state(SplashState)


class RankingsState(BaseState):
    name = "rankings"

    def render(self) -> None:
        gui = self.controller.gui
        rankings_mode = gui.get_rankings_gamemode()
        rankings_filter = gui.selected_rankings_filter
        top_scores = self.controller.game_service.get_rankings(rankings_mode, rankings_filter, limit=10)
        gui.showRankings(top_scores, rankings_mode)

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        if event.type not in [
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
            pygame.MOUSEWHEEL,
        ]:
            return

        gui = self.controller.gui
        mouse_pos = pygame.mouse.get_pos()
        gui.set_mouse_x_y(mouse_pos)

        if gui.handle_scroll(event, mouse_pos):
            return

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if gui.handle_ranking_filter_click(mouse_pos):
            return

        if gui.rankings_back_button_rect.collidepoint(gui.get_mouse_x(), gui.get_mouse_y()):
            if self.controller.previous_screen_for_rankings == "victory":
                self.controller.change_state(VictoryState)
            elif self.controller.previous_screen_for_rankings == "game_over":
                self.controller.change_state(GameOverState)
            else:
                self.controller.change_state(RankingsMapSelectionState)
            return

        if gui.rank_sel_main_menu_button_rect.collidepoint(gui.get_mouse_x(), gui.get_mouse_y()):
            self.controller.change_state(SplashState)


class RankingsMapSelectionState(BaseState):
    name = "rankings_map_selection"

    def render(self) -> None:
        self.controller.gui.showModeSelectionScreen()

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        mouse_pos = pygame.mouse.get_pos()
        result = self.controller.gui.handle_rankings_mode_click(mouse_pos)
        if not result:
            return

        if result == "back":
            self.controller.change_state(SplashState)
            return

        self.controller.change_state(RankingsState)

from __future__ import annotations

from dataclasses import dataclass

from flagguessr.application.ports import FlagCatalog, ScoreRepository
from flagguessr.domain.models import (
    GameConfig,
    GameMode,
    GameSession,
    GuessResult,
    GuessStatus,
    RunningGame,
    StartGameResult,
)
from flagguessr.domain.strategies import build_mode_strategy


@dataclass
class GameService:
    score_repository: ScoreRepository
    flag_catalog: FlagCatalog
    config: GameConfig

    def initialize(self) -> None:
        self.score_repository.initialize()
        self.flag_catalog.initialize()

    def start_game(
        self,
        mode_value: str,
        map_name: str,
        flag_size: tuple[int, int],
        now_ms: int,
    ) -> StartGameResult:
        try:
            mode = GameMode.from_value(mode_value)
        except ValueError:
            return StartGameResult(success=False, error=f"Unsupported mode: {mode_value}")

        countries = self.flag_catalog.load_countries(map_name)
        if not countries:
            return StartGameResult(success=False, error="No countries found for the selected map.")

        flag_images = self.flag_catalog.load_flag_images(countries, flag_size)
        if not flag_images:
            return StartGameResult(success=False, error="No flag images available for the selected map.")

        all_countries = list(flag_images.keys())
        strategy = build_mode_strategy(mode)
        first_country = strategy.next_country(all_countries, [])
        if not first_country:
            return StartGameResult(success=False, error="Unable to select an initial country.")

        session = GameSession(
            mode=mode,
            map_name=map_name,
            score=self.config.initial_score,
            lives=self.config.max_lives,
            start_time_ms=now_ms if strategy.is_timed else 0,
        )
        session.countries_sequence.append(first_country)
        session.flags_shown_count = strategy.initial_flags_shown()

        running_game = RunningGame(
            session=session,
            countries=countries,
            flag_images=flag_images,
            current_country=first_country,
        )
        return StartGameResult(success=True, running_game=running_game)

    def tick_game(self, running_game: RunningGame, now_ms: int) -> bool:
        session = running_game.session
        if session.mode != GameMode.BLITZ or session.start_time_ms <= 0:
            return False

        elapsed = (now_ms - session.start_time_ms) / 1000
        if elapsed >= self.config.blitz_time_limit_seconds:
            self.score_repository.save_score(
                session=session,
                time_taken=self.config.blitz_time_limit_seconds,
                flags_shown=max(1, session.flags_shown_count),
                mode_data={},
            )
            return True
        return False

    def submit_guess(self, running_game: RunningGame, raw_guess: str, now_ms: int) -> GuessResult:
        session = running_game.session
        strategy = build_mode_strategy(session.mode)

        current_country = running_game.current_country
        guess = raw_guess.strip().lower()

        all_countries = list(running_game.flag_images.keys())
        if not all_countries:
            return GuessResult(status=GuessStatus.GAME_OVER, message="No flags loaded.")

        if guess == current_country.lower():
            session.score += 1
            next_country = strategy.next_country(all_countries, session.countries_sequence)
            if next_country is None:
                self.score_repository.save_score(
                    session=session,
                    time_taken=0,
                    flags_shown=len(session.countries_sequence),
                    mode_data={"completion": True},
                )
                return GuessResult(status=GuessStatus.VICTORY, clear_error=True)

            running_game.current_country = next_country
            session.countries_sequence.append(next_country)
            if session.mode != GameMode.NORMAL:
                session.flags_shown_count += 1

            return GuessResult(status=GuessStatus.CORRECT, clear_error=True)

        session.lives -= 1
        session.wrong_countries.append(current_country)
        message = f"Wrong! It was: {current_country}"

        if session.lives <= 0:
            time_taken = 0
            if session.mode == GameMode.BLITZ and session.start_time_ms > 0:
                time_taken = int((now_ms - session.start_time_ms) / 1000)

            flags_shown = session.flags_shown_count
            if flags_shown <= 0:
                flags_shown = len(session.countries_sequence)

            self.score_repository.save_score(
                session=session,
                time_taken=time_taken,
                flags_shown=flags_shown,
                mode_data={},
            )
            return GuessResult(status=GuessStatus.GAME_OVER, message=message)

        next_country = strategy.next_country(all_countries, session.countries_sequence)
        if next_country is None:
            self.score_repository.save_score(
                session=session,
                time_taken=0,
                flags_shown=len(session.countries_sequence),
                mode_data={"completion": True},
            )
            return GuessResult(status=GuessStatus.VICTORY, message=message)

        running_game.current_country = next_country
        session.countries_sequence.append(next_country)
        if session.mode != GameMode.NORMAL:
            session.flags_shown_count += 1

        return GuessResult(status=GuessStatus.WRONG, message=message)

    def get_rankings(self, map_name: str, filter_mode: str, limit: int = 10):
        return self.score_repository.get_top_scores(map_name, filter_mode, limit=limit)

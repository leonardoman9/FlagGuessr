from __future__ import annotations

import random
from abc import ABC, abstractmethod

from .models import GameMode


class ModeStrategy(ABC):
    mode: GameMode

    @property
    def is_timed(self) -> bool:
        return False

    @property
    def uses_unique_countries(self) -> bool:
        return False

    def initial_flags_shown(self) -> int:
        return 0

    @abstractmethod
    def next_country(self, all_countries: list[str], shown_sequence: list[str]) -> str | None:
        """Return next country or None when mode completes."""


class NormalModeStrategy(ModeStrategy):
    mode = GameMode.NORMAL

    @property
    def uses_unique_countries(self) -> bool:
        return True

    def next_country(self, all_countries: list[str], shown_sequence: list[str]) -> str | None:
        remaining = [country for country in all_countries if country not in shown_sequence]
        if not remaining:
            return None
        return random.choice(remaining)


class EndlessModeStrategy(ModeStrategy):
    mode = GameMode.ENDLESS

    def initial_flags_shown(self) -> int:
        return 1

    def next_country(self, all_countries: list[str], shown_sequence: list[str]) -> str | None:
        if not all_countries:
            return None
        return random.choice(all_countries)


class BlitzModeStrategy(ModeStrategy):
    mode = GameMode.BLITZ

    @property
    def is_timed(self) -> bool:
        return True

    def initial_flags_shown(self) -> int:
        return 1

    def next_country(self, all_countries: list[str], shown_sequence: list[str]) -> str | None:
        if not all_countries:
            return None
        return random.choice(all_countries)


def build_mode_strategy(mode: GameMode) -> ModeStrategy:
    if mode == GameMode.NORMAL:
        return NormalModeStrategy()
    if mode == GameMode.ENDLESS:
        return EndlessModeStrategy()
    if mode == GameMode.BLITZ:
        return BlitzModeStrategy()
    raise ValueError(f"Unsupported mode: {mode}")

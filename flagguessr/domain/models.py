from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GameMode(str, Enum):
    NORMAL = "normal"
    ENDLESS = "endless"
    BLITZ = "blitz"

    @classmethod
    def from_value(cls, value: str) -> "GameMode":
        return cls(value.lower())


@dataclass(frozen=True)
class GameConfig:
    max_lives: int = 3
    initial_score: int = 0
    blitz_time_limit_seconds: int = 60


@dataclass
class GameSession:
    mode: GameMode
    map_name: str
    score: int
    lives: int
    wrong_countries: list[str] = field(default_factory=list)
    countries_sequence: list[str] = field(default_factory=list)
    flags_shown_count: int = 0
    start_time_ms: int = 0


@dataclass
class RunningGame:
    session: GameSession
    countries: dict[str, str]
    flag_images: dict[str, Any]
    current_country: str


class GuessStatus(str, Enum):
    CORRECT = "correct"
    WRONG = "wrong"
    VICTORY = "victory"
    GAME_OVER = "game_over"


@dataclass
class GuessResult:
    status: GuessStatus
    message: str = ""
    clear_input: bool = True
    clear_error: bool = False


@dataclass
class StartGameResult:
    success: bool
    running_game: RunningGame | None = None
    error: str = ""

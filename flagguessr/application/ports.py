from __future__ import annotations

from typing import Any, Protocol

from flagguessr.domain.models import GameSession


class ScoreRepository(Protocol):
    def initialize(self) -> None:
        ...

    def save_score(
        self,
        session: GameSession,
        time_taken: int,
        flags_shown: int,
        mode_data: dict[str, Any],
    ) -> None:
        ...

    def get_top_scores(self, gamemode: str, filter_mode: str = "all", limit: int = 10) -> list[tuple[Any, ...]]:
        ...


class FlagCatalog(Protocol):
    def initialize(self) -> None:
        ...

    def load_countries(self, map_name: str) -> dict[str, str]:
        ...

    def load_flag_images(self, countries: dict[str, str], size: tuple[int, int]) -> dict[str, Any]:
        ...

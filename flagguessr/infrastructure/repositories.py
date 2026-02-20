from __future__ import annotations

from typing import Any

from flagguessr.infrastructure import db
from flagguessr.domain.models import GameSession


class SQLiteScoreRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def initialize(self) -> None:
        db.create_scores_table(self.db_path)

    def save_score(
        self,
        session: GameSession,
        time_taken: int,
        flags_shown: int,
        mode_data: dict[str, Any],
    ) -> None:
        db.insert_score(
            self.db_path,
            session.score,
            session.countries_sequence,
            session.wrong_countries,
            session.map_name,
            session.mode.value,
            time_taken,
            flags_shown,
            mode_data,
        )

    def get_top_scores(self, gamemode: str, filter_mode: str = "all", limit: int = 10):
        return db.get_top_scores(self.db_path, gamemode, filter_mode, limit)

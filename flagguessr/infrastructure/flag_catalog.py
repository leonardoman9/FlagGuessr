from __future__ import annotations

from flagguessr.infrastructure import db
from flagguessr.infrastructure.countries import CountryLoader


class SQLiteFlagCatalog:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.loader = CountryLoader()

    def initialize(self) -> None:
        db.populate_flags_database(self.db_path)

    def load_countries(self, map_name: str) -> dict[str, str]:
        return self.loader.load_countries(self.db_path, map_name.lower())

    def load_flag_images(self, countries_map: dict[str, str], size: tuple[int, int]):
        return self.loader.load_flag_images(countries_map, size)

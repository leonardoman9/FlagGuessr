import os
import sqlite3

import pygame

from flagguessr.shared.paths import resource_path


class CountryLoader:
    def __init__(self):
        self.base_flags_path = resource_path("data/flags")

    def load_flag_images(self, countries, size):
        flags_images = {}
        for country, continent in countries.items():
            continent_path = os.path.join(self.base_flags_path, continent)
            # Ensure the path separator is correct for the OS
            continent_path = os.path.normpath(continent_path)
            
            flag_path = os.path.join(continent_path, f"{country}.png")
            flag_path = os.path.normpath(flag_path)
            
            try:
                # The resource_path function is not needed here anymore if base_flags_path is already absolute
                flag_image = pygame.image.load(flag_path)
                flags_images[country] = pygame.transform.scale(flag_image, size)
            except pygame.error as e:
                print(f"Error loading flag for {country} at {flag_path}: {e}")
        return flags_images

    def load_countries(self, db_path, gamemode="global"):
        """Load countries from the database based on the selected gamemode"""
        conn = sqlite3.connect(db_path)
        if not conn:
            return {}
            
        cursor = conn.cursor()
        
        if gamemode == "global":
            cursor.execute("SELECT country, continent FROM flags")
        else:
            cursor.execute("SELECT country, continent FROM flags WHERE continent = ?", (gamemode,))
            
        countries_data = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return countries_data


# Backward-compatible alias kept for legacy references.
countries = CountryLoader

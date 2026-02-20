from __future__ import annotations

import pygame

from flagguessr.shared.paths import resource_path


def build_color_palette() -> dict[str, tuple[int, int, int]]:
    return {
        "bg_top": (14, 20, 28),
        "bg_bottom": (9, 13, 20),
        "panel": (20, 31, 43),
        "panel_alt": (26, 38, 52),
        "panel_soft": (33, 47, 63),
        "border": (64, 90, 113),
        "text": (237, 246, 255),
        "muted": (190, 210, 228),
        "primary": (55, 177, 169),
        "primary_dark": (41, 130, 124),
        "accent": (255, 166, 77),
        "danger": (231, 76, 60),
        "success": (76, 201, 139),
        "shadow": (0, 0, 0),
    }


def build_fonts() -> dict[str, pygame.font.Font]:
    def from_file(filename: str, size: int) -> pygame.font.Font | None:
        path = resource_path(f"data/fonts/{filename}")
        try:
            return pygame.font.Font(path, size)
        except Exception:
            return None

    def from_system(size: int, bold: bool = False) -> pygame.font.Font:
        # Robust fallback for platforms without bundled fonts.
        return pygame.font.SysFont("DejaVu Sans", size, bold=bold)

    title = from_file("americancaptain.ttf", 64) or from_system(58, bold=True)
    heading = from_file("americancaptain.ttf", 44) or from_system(40, bold=True)
    body = from_system(30, bold=False)
    small = from_system(24, bold=True)
    tiny = from_system(20, bold=True)

    return {
        "title": title,
        "heading": heading,
        "body": body,
        "small": small,
        "tiny": tiny,
    }

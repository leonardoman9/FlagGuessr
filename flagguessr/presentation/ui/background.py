from __future__ import annotations

import pygame


def build_static_background(
    width: int,
    height: int,
    colors: dict[str, tuple[int, int, int]],
) -> pygame.Surface:
    surface = pygame.Surface((width, height))

    top = colors["bg_top"]
    bottom = colors["bg_bottom"]
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    glow = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.circle(glow, (55, 177, 169, 42), (180, 120), 220)
    pygame.draw.circle(glow, (255, 166, 77, 30), (width - 150, height - 120), 260)
    pygame.draw.circle(glow, (70, 130, 180, 18), (width // 2, height // 2), 300)
    surface.blit(glow, (0, 0))

    for x in range(0, width, 64):
        pygame.draw.line(surface, (24, 34, 48), (x, 0), (x, height), 1)
    for y in range(0, height, 64):
        pygame.draw.line(surface, (24, 34, 48), (0, y), (width, y), 1)

    return surface

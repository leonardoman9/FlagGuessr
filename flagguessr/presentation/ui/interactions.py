from __future__ import annotations

import pygame


class InteractionMixin:
    """Input handlers for mode selection, rankings and scrolling widgets."""

    _MAP_OPTIONS = ("GLOBAL", "EUROPE", "OCEANIA", "AFRICA", "ASIA", "AMERICA")

    def _mode_map_panel_rect(self) -> pygame.Rect:
        option_count = len(self._MAP_OPTIONS)
        return pygame.Rect(
            self.mode_map_dropdown_rect.x,
            self.mode_map_dropdown_rect.bottom + 4,
            self.mode_map_dropdown_rect.width,
            option_count * 36 + 8,
        )

    def handle_mode_selection_click(self, event, mouse_pos):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        if self.mode_map_dropdown_rect.collidepoint(mouse_pos):
            self.mode_map_dropdown_open = not self.mode_map_dropdown_open
            return None

        if self.mode_map_dropdown_open:
            for mode, rect in getattr(self, "mode_map_option_rects", []):
                if rect.collidepoint(mouse_pos):
                    self.selected_mode_map = mode
                    self.mode_map_dropdown_open = False
                    return None

            if not self._mode_map_panel_rect().collidepoint(mouse_pos):
                self.mode_map_dropdown_open = False
            return None

        mode_buttons = [
            (self.mode_normal_button_rect, "normal"),
            (self.mode_endless_button_rect, "endless"),
            (self.mode_blitz_button_rect, "blitz"),
        ]
        for rect, mode in mode_buttons:
            if rect.collidepoint(mouse_pos):
                self.selected_mode = mode
                return self.selected_mode, self.selected_mode_map

        if self.mode_back_button_rect.collidepoint(mouse_pos):
            return "back"

        return None

    def handle_ranking_filter_click(self, mouse_pos):
        tabs = [
            (self.rank_filter_all_rect, "all"),
            (self.rank_filter_normal_rect, "normal"),
            (self.rank_filter_endless_rect, "endless"),
            (self.rank_filter_blitz_rect, "blitz"),
        ]
        for rect, filter_name in tabs:
            if rect.collidepoint(mouse_pos):
                self.selected_rankings_filter = filter_name
                self.scroll_y = 0
                return True
        return False

    def handle_rankings_mode_click(self, mouse_pos):
        mode_buttons = {
            "global": self.rank_mode_global_button_rect,
            "europe": self.rank_mode_europe_button_rect,
            "america": self.rank_mode_america_button_rect,
            "asia": self.rank_mode_asia_button_rect,
            "oceania": self.rank_mode_oceania_button_rect,
            "africa": self.rank_mode_africa_button_rect,
        }

        for mode, rect in mode_buttons.items():
            if rect.collidepoint(mouse_pos):
                self.set_rankings_gamemode(mode)
                return mode

        if self.rank_mode_main_menu_button_rect.collidepoint(mouse_pos):
            return "back"

        return None

    def handle_scroll(self, event, mouse_pos):
        if not self.rankings_content_rect:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.scroll_handle_rect and self.scroll_handle_rect.collidepoint(mouse_pos):
                self.is_scrolling = True
                self.scroll_offset_y = mouse_pos[1] - self.scroll_handle_rect.y
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_scrolling:
                self.is_scrolling = False
                return True

        if event.type == pygame.MOUSEMOTION and self.is_scrolling:
            max_track = self.scroll_bar_rect.height - self.scroll_handle_rect.height
            new_y = mouse_pos[1] - self.scroll_offset_y
            self.scroll_handle_rect.y = max(self.scroll_bar_rect.y, min(new_y, self.scroll_bar_rect.y + max_track))
            ratio = (self.scroll_handle_rect.y - self.scroll_bar_rect.y) / max(max_track, 1)
            self.scroll_y = ratio * self.max_scroll_y
            return True

        if event.type == pygame.MOUSEWHEEL and self.rankings_content_rect.collidepoint(mouse_pos):
            self.scroll_y -= event.y * 28
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll_y))
            return True

        return False

    def draw_scrollbar(self, content_rect, view_height):
        self.scroll_bar_rect = pygame.Rect(content_rect.right + 10, content_rect.y + 6, 12, view_height)
        pygame.draw.rect(self.screen, self.colors["panel_alt"], self.scroll_bar_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.colors["border"], self.scroll_bar_rect, 1, border_radius=8)

        total_h = self.max_scroll_y + view_height
        handle_h = max(30, int((view_height / max(total_h, 1)) * view_height))
        max_track = self.scroll_bar_rect.height - handle_h
        ratio = self.scroll_y / max(self.max_scroll_y, 1)
        handle_y = self.scroll_bar_rect.y + ratio * max_track
        self.scroll_handle_rect = pygame.Rect(self.scroll_bar_rect.x, handle_y, self.scroll_bar_rect.width, handle_h)

        pygame.draw.rect(self.screen, self.colors["primary"], self.scroll_handle_rect, border_radius=8)

from __future__ import annotations

import json
from datetime import datetime

import pygame


class ScreenMixin:
    """Rendering methods for all game screens."""

    _RANKING_COL_X = [24, 112, 230, 410, 610]

    def _draw_screen_header(self, title: str, subtitle: str, top: int = 26) -> None:
        panel = pygame.Rect(self.width // 2 - 360, top, 720, 106)
        self._draw_panel(panel, tone="panel")
        pygame.draw.rect(self.screen, self.colors["primary_dark"], panel, 2, border_radius=14)

        title_shadow = self.fonts["heading"].render(title, True, (0, 0, 0))
        title_surface = self.fonts["heading"].render(title, True, self.colors["text"])
        subtitle_surface = self.fonts["small"].render(subtitle, True, self.colors["muted"])

        self.screen.blit(title_shadow, title_shadow.get_rect(center=(panel.centerx + 2, panel.y + 34)))
        self.screen.blit(title_surface, title_surface.get_rect(center=(panel.centerx, panel.y + 32)))
        self.screen.blit(subtitle_surface, subtitle_surface.get_rect(center=(panel.centerx, panel.y + 74)))

    def _draw_result_screen(self, title, title_color, subtitle, body_lines):
        self.draw_gradient_background()

        panel = pygame.Rect(self.width // 2 - 430, 92, 860, 470)
        self._draw_panel(panel, tone="panel")

        title_surface = self.fonts["title"].render(title, True, title_color)
        self.screen.blit(title_surface, title_surface.get_rect(center=(panel.centerx, panel.y + 74)))

        subtitle_surface = self.fonts["body"].render(subtitle, True, self.colors["text"])
        self.screen.blit(subtitle_surface, subtitle_surface.get_rect(center=(panel.centerx, panel.y + 132)))

        for text, color, x, y, font_key in body_lines:
            rendered = self.fonts[font_key].render(text, True, color)
            self.screen.blit(rendered, (x, y))

    def showSplashScreen(self):
        self.draw_gradient_background()

        hero = pygame.Rect(self.width // 2 - 360, 70, 720, 190)
        self._draw_panel(hero, tone="panel")

        title = self.fonts["title"].render("FLAG GUESSR", True, self.colors["text"])
        subtitle = self.fonts["small"].render("Guess the country from the flag", True, self.colors["muted"])
        self.screen.blit(title, title.get_rect(center=(hero.centerx, hero.y + 76)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(hero.centerx, hero.y + 136)))

        info = pygame.Rect(70, 300, 360, 210)
        self._draw_panel(info, tone="panel_alt")
        hints = [
            "3 lives per match",
            "Normal: complete all flags",
            "Endless: survive as long as possible",
            "Blitz: 60s speed challenge",
        ]
        info_title = self.fonts["small"].render("How it works", True, self.colors["accent"])
        self.screen.blit(info_title, (info.x + 18, info.y + 16))
        for i, line in enumerate(hints):
            line_s = self.fonts["tiny"].render(f"- {line}", True, self.colors["text"])
            self.screen.blit(line_s, (info.x + 18, info.y + 50 + i * 34))

        mouse_pos = pygame.mouse.get_pos()
        self.draw_modern_button(self.play_button_rect, "PLAY", "primary", self.play_button_rect.collidepoint(mouse_pos))
        self.draw_modern_button(
            self.splash_rankings_button_rect,
            "RANKINGS",
            "secondary",
            self.splash_rankings_button_rect.collidepoint(mouse_pos),
        )
        self.draw_modern_button(self.splash_quit_button_rect, "QUIT", "danger", self.splash_quit_button_rect.collidepoint(mouse_pos))

        self.draw_music_controls()
        self.update_error_message()
        self.draw_error_message_overlay()

        pygame.display.flip()

    def showGame(self, current_country, score, game_flags_images, lives,
                 selected_game_mode="normal", game_start_time=0, blitz_time_limit=60, flags_shown_count=0):
        self.draw_gradient_background()

        self.draw_game_hud(score, lives)
        self.draw_mode_info(selected_game_mode, game_start_time, blitz_time_limit, flags_shown_count)

        flag_panel = pygame.Rect(self.width // 2 - 330, 118, 660, 400)
        self._draw_panel(flag_panel, tone="panel")

        if current_country in game_flags_images:
            flag = game_flags_images[current_country]
            self.screen.blit(flag, flag.get_rect(center=flag_panel.center))
        else:
            missing = self.fonts["small"].render("Flag image not available", True, self.colors["danger"])
            self.screen.blit(missing, missing.get_rect(center=flag_panel.center))

        prompt = self.fonts["small"].render("Type country name and press ENTER", True, self.colors["muted"])
        self.screen.blit(prompt, prompt.get_rect(center=(self.width // 2, self.input_rect.y - 22)))

        self.draw_modern_input_box()
        self.draw_modern_button(
            self.game_exit_button_rect,
            "EXIT",
            "danger",
            self.game_exit_button_rect.collidepoint((self.mouse_x, self.mouse_y)),
        )

        self.draw_game_music_controls()
        self.update_error_message()
        self.draw_error_message_overlay()

        pygame.display.flip()

    def draw_mode_info(self, selected_game_mode, game_start_time, blitz_time_limit, flags_shown_count):
        info = pygame.Rect(28, self.height - 156, 240, 120)
        self._draw_panel(info, tone="panel_alt")

        mode_text = self.fonts["small"].render(f"Mode: {selected_game_mode.upper()}", True, self.colors["accent"])
        self.screen.blit(mode_text, (info.x + 14, info.y + 12))

        if selected_game_mode == "blitz":
            elapsed = (pygame.time.get_ticks() - game_start_time) / 1000 if game_start_time > 0 else 0
            remaining = max(0.0, blitz_time_limit - elapsed)
            col = self.colors["success"] if remaining > 20 else self.colors["accent"] if remaining > 10 else self.colors["danger"]
            timer = self.fonts["heading"].render(f"{remaining:04.1f}s", True, col)
            self.screen.blit(timer, (info.x + 14, info.y + 46))
        elif selected_game_mode == "endless":
            row = self.fonts["body"].render(f"Flags shown: {flags_shown_count}", True, self.colors["text"])
            self.screen.blit(row, (info.x + 14, info.y + 52))
        else:
            row = self.fonts["small"].render("Complete all flags", True, self.colors["text"])
            self.screen.blit(row, (info.x + 14, info.y + 56))

    def draw_game_hud(self, score, lives):
        score_card = pygame.Rect(28, 20, 190, 84)
        life_card = pygame.Rect(232, 20, 220, 84)
        self._draw_panel(score_card, tone="panel_alt")
        self._draw_panel(life_card, tone="panel_alt")

        s_label = self.fonts["tiny"].render("SCORE", True, self.colors["muted"])
        s_value = self.fonts["heading"].render(str(score), True, self.colors["text"])
        self.screen.blit(s_label, (score_card.x + 14, score_card.y + 10))
        self.screen.blit(s_value, (score_card.x + 14, score_card.y + 32))

        l_label = self.fonts["tiny"].render("LIVES", True, self.colors["muted"])
        self.screen.blit(l_label, (life_card.x + 14, life_card.y + 10))
        for i in range(3):
            heart_rect = pygame.Rect(life_card.x + 14 + i * 62, life_card.y + 38, 46, 30)
            col = self.colors["danger"] if i < lives else (90, 100, 110)
            pygame.draw.rect(self.screen, col, heart_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.colors["border"], heart_rect, 2, border_radius=8)

    def draw_modern_input_box(self):
        pygame.draw.rect(self.screen, self.colors["panel_alt"], self.input_border, border_radius=14)
        pygame.draw.rect(self.screen, self.colors["primary"], self.input_border, 2, border_radius=14)
        pygame.draw.rect(self.screen, (14, 19, 27), self.input_rect, border_radius=12)

        text_surface = self.fonts["body"].render(self.input_text if self.input_text else "", True, self.colors["text"])
        self.screen.blit(text_surface, (self.input_rect.x + 14, self.input_rect.y + 14))

    def showGameOver(self, score, wrong_countries, gamemode):
        body_lines = [
            ("Mistakes", self.colors["accent"], self.width // 2 - 390, 276, "small"),
        ]
        if wrong_countries:
            for i, country in enumerate(wrong_countries[:8]):
                body_lines.append((f"{i + 1}. {country}", self.colors["muted"], self.width // 2 - 390, 308 + i * 28, "tiny"))
        else:
            body_lines.append(("No wrong answers recorded.", self.colors["muted"], self.width // 2 - 390, 308, "tiny"))

        self._draw_result_screen(
            "GAME OVER",
            self.colors["danger"],
            f"Map: {gamemode.upper()}    Score: {score}",
            body_lines,
        )

        mouse_pos = pygame.mouse.get_pos()
        self.draw_modern_button(self.quit_button_rect, "QUIT", "danger", self.quit_button_rect.collidepoint(mouse_pos))
        self.draw_modern_button(self.rankings_button_rect, "SEE RANKINGS", "secondary", self.rankings_button_rect.collidepoint(mouse_pos))
        self.draw_modern_button(self.main_menu_button_rect, "MAIN MENU", "primary", self.main_menu_button_rect.collidepoint(mouse_pos))
        pygame.display.flip()

    def showVictory(self, score, gamemode):
        body_lines = [
            (
                "Great run. Try endless or blitz for a new challenge.",
                self.colors["muted"],
                self.width // 2 - 285,
                322,
                "small",
            ),
        ]
        self._draw_result_screen(
            "VICTORY",
            self.colors["success"],
            f"Completed {gamemode.upper()} with score {score}",
            body_lines,
        )

        mouse_pos = pygame.mouse.get_pos()
        self.draw_modern_button(self.quit_button_rect, "QUIT", "danger", self.quit_button_rect.collidepoint(mouse_pos))
        self.draw_modern_button(self.rankings_button_rect, "SEE RANKINGS", "secondary", self.rankings_button_rect.collidepoint(mouse_pos))
        self.draw_modern_button(self.main_menu_button_rect, "MAIN MENU", "primary", self.main_menu_button_rect.collidepoint(mouse_pos))
        pygame.display.flip()

    def showModeSelection(self, gamemodes):
        self.draw_gradient_background()

        self._draw_screen_header("SELECT MODE", "Choose rules and map before starting")

        map_label = self.fonts["tiny"].render("MAP", True, self.colors["accent"])
        self.screen.blit(map_label, (self.mode_map_dropdown_rect.x, self.mode_map_dropdown_rect.y - 20))
        self.draw_map_dropdown(gamemodes)

        cards = [
            (self.mode_normal_button_rect, "NORMAL", "Complete all flags"),
            (self.mode_endless_button_rect, "ENDLESS", "No finish line, 3 lives"),
            (self.mode_blitz_button_rect, "BLITZ", "60 seconds speed run"),
        ]

        mouse_pos = pygame.mouse.get_pos()
        for rect, name, desc in cards:
            selected = self.selected_mode == name.lower()
            hover = rect.collidepoint(mouse_pos)
            self._draw_panel(rect, tone="panel_alt" if selected or hover else "panel")
            pygame.draw.rect(
                self.screen,
                self.colors["accent"] if selected else self.colors["primary"] if hover else self.colors["border"],
                rect,
                3,
                border_radius=14,
            )

            top = self.fonts["heading"].render(name, True, self.colors["text"])
            desc_s = self.fonts["small"].render(desc, True, self.colors["muted"])
            self.screen.blit(top, top.get_rect(center=(rect.centerx, rect.y + 86)))
            self.screen.blit(desc_s, desc_s.get_rect(center=(rect.centerx, rect.y + 150)))

        self.draw_modern_button(
            self.mode_back_button_rect,
            "BACK TO MENU",
            "secondary",
            self.mode_back_button_rect.collidepoint(mouse_pos),
        )

        self.update_error_message()
        self.draw_error_message_overlay()
        pygame.display.flip()

    def draw_map_dropdown(self, gamemodes):
        options = [g.upper() for g in gamemodes]
        self.draw_modern_dropdown(self.mode_map_dropdown_rect, self.selected_mode_map.upper(), options, self.mode_map_dropdown_open)

        if self.mode_map_dropdown_open:
            panel = pygame.Rect(
                self.mode_map_dropdown_rect.x,
                self.mode_map_dropdown_rect.bottom + 4,
                self.mode_map_dropdown_rect.width,
                len(options) * 36 + 8,
            )
            self._draw_panel(panel, tone="panel")
            self.mode_map_option_rects = []

            for i, opt in enumerate(options):
                row = pygame.Rect(panel.x + 4, panel.y + 4 + i * 36, panel.width - 8, 32)
                hover = row.collidepoint((self.mouse_x, self.mouse_y))
                selected = opt.lower() == self.selected_mode_map.lower()
                if selected:
                    bg = self.colors["primary_dark"]
                elif hover:
                    bg = self.colors["panel_soft"]
                else:
                    bg = self.colors["panel"]

                pygame.draw.rect(self.screen, bg, row, border_radius=8)
                txt = self.fonts["tiny"].render(opt, True, self.colors["text"])
                self.screen.blit(txt, (row.x + 10, row.y + 7))
                self.mode_map_option_rects.append((opt.lower(), row))

    def showModeSelectionScreen(self):
        self.draw_gradient_background()

        self._draw_screen_header("RANKINGS MAP", "Choose a map to view top scores", top=56)

        buttons = [
            ("GLOBAL", self.rank_mode_global_button_rect),
            ("EUROPE", self.rank_mode_europe_button_rect),
            ("AMERICA", self.rank_mode_america_button_rect),
            ("ASIA", self.rank_mode_asia_button_rect),
            ("OCEANIA", self.rank_mode_oceania_button_rect),
            ("AFRICA", self.rank_mode_africa_button_rect),
        ]

        mouse_pos = pygame.mouse.get_pos()
        for name, rect in buttons:
            self.draw_modern_button(rect, name, "secondary", rect.collidepoint(mouse_pos))

        self.draw_modern_button(
            self.rank_mode_main_menu_button_rect,
            "BACK",
            "primary",
            self.rank_mode_main_menu_button_rect.collidepoint(mouse_pos),
        )

        pygame.display.flip()

    def showRankings(self, scores, gamemode):
        self.draw_gradient_background()

        self._draw_screen_header("TOP RANKINGS", gamemode.upper(), top=18)

        mouse_pos = pygame.mouse.get_pos()
        self.draw_ranking_filter_tabs(mouse_pos)

        content_rect = pygame.Rect(self.width // 2 - 470, 218, 940, 430)
        self.rankings_content_rect = content_rect
        self._draw_panel(content_rect, tone="panel")

        row_height = 46
        header_height = 40
        total_content = header_height + len(scores) * row_height
        view_h = content_rect.height - 12
        self.max_scroll_y = max(0, total_content - view_h)
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll_y))

        table_surface = pygame.Surface((content_rect.width - 12, max(view_h, total_content)), pygame.SRCALPHA)
        self.draw_mode_specific_headers(8, table_surface)

        for i, row in enumerate(scores):
            y = header_height + i * row_height
            row_rect = pygame.Rect(0, y, table_surface.get_width(), row_height - 6)
            fill = self.colors["panel_alt"] if i % 2 == 0 else self.colors["panel"]
            pygame.draw.rect(table_surface, fill, row_rect, border_radius=10)
            pygame.draw.rect(table_surface, self.colors["border"], row_rect, 1, border_radius=10)
            self.draw_mode_specific_data(row_rect, row, i + 1, table_surface)

        if not scores:
            empty = self.fonts["small"].render("No scores yet for this filter.", True, self.colors["muted"])
            table_surface.blit(empty, empty.get_rect(center=(table_surface.get_width() // 2, 130)))

        self.screen.blit(
            table_surface,
            (content_rect.x + 6, content_rect.y + 6),
            pygame.Rect(0, int(self.scroll_y), table_surface.get_width(), view_h),
        )

        if self.max_scroll_y > 0:
            self.draw_scrollbar(content_rect, view_h)

        self.draw_modern_button(
            self.rankings_back_button_rect,
            "BACK",
            "secondary",
            self.rankings_back_button_rect.collidepoint(mouse_pos),
        )
        self.draw_modern_button(
            self.rank_sel_main_menu_button_rect,
            "MAIN MENU",
            "primary",
            self.rank_sel_main_menu_button_rect.collidepoint(mouse_pos),
        )

        pygame.display.flip()

    def draw_mode_specific_headers(self, y_offset, surface):
        headers = ["RANK", "SCORE"]
        if self.selected_rankings_filter == "normal":
            headers += ["COMPLETION", "ACCURACY", "DATE"]
        elif self.selected_rankings_filter == "endless":
            headers += ["FLAGS", "AVG/LIFE", "DATE"]
        elif self.selected_rankings_filter == "blitz":
            headers += ["TIME", "FLAGS/SEC", "DATE"]
        else:
            headers += ["MODE", "STAT", "DATE"]

        for header, x in zip(headers, self._RANKING_COL_X):
            text = self.fonts["tiny"].render(header, True, self.colors["muted"])
            surface.blit(text, (x, y_offset))

    def draw_mode_specific_data(self, card_rect, row, rank, surface):
        if len(row) >= 9:
            score, timestamp, _, _, mistakes, game_mode, time_taken, flags_shown, mode_data = row
        else:
            score, timestamp, _, _, mistakes = row
            game_mode, time_taken, flags_shown, mode_data = "normal", 0, 0, "{}"

        try:
            formatted_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%y")
        except Exception:
            formatted_date = "N/A"

        mistakes_count = len([m for m in (mistakes or "").split(",") if m.strip()])
        total_attempts = score + mistakes_count

        try:
            mode_dict = json.loads(mode_data) if mode_data else {}
        except Exception:
            mode_dict = {}

        base = [f"#{rank}", str(score)]
        if self.selected_rankings_filter == "normal":
            completion = "YES" if mode_dict.get("completion") else f"{score}/{max(total_attempts, 1)}"
            accuracy = f"{(score / max(total_attempts, 1) * 100):.0f}%"
            extra = [completion, accuracy, formatted_date]
        elif self.selected_rankings_filter == "endless":
            extra = [str(flags_shown or 0), f"{(flags_shown or 0) / 3:.1f}", formatted_date]
        elif self.selected_rankings_filter == "blitz":
            extra = [f"{int(time_taken or 0)}s", f"{score / max(float(time_taken or 1), 1.0):.2f}", formatted_date]
        else:
            stat = ""
            if game_mode == "normal":
                stat = f"Acc {score / max(total_attempts, 1) * 100:.0f}%"
            elif game_mode == "endless":
                stat = f"{flags_shown or 0} flags"
            elif game_mode == "blitz":
                stat = f"{score / max(float(time_taken or 1), 1.0):.2f}/s"
            extra = [game_mode.upper() if game_mode else "N/A", stat, formatted_date]

        values = base + extra
        for i, value in enumerate(values):
            font = self.fonts["small"] if i < 2 else self.fonts["tiny"]
            color = self.colors["text"] if i < 2 else self.colors["muted"]
            txt = font.render(str(value), True, color)
            surface.blit(txt, txt.get_rect(centery=card_rect.centery, x=self._RANKING_COL_X[i]))

    def draw_ranking_filter_tabs(self, mouse_pos):
        tabs = [
            ("ALL", "all", self.rank_filter_all_rect),
            ("NORMAL", "normal", self.rank_filter_normal_rect),
            ("ENDLESS", "endless", self.rank_filter_endless_rect),
            ("BLITZ", "blitz", self.rank_filter_blitz_rect),
        ]

        for name, key, rect in tabs:
            selected = self.selected_rankings_filter == key
            hover = rect.collidepoint(mouse_pos)
            style = "primary" if selected else "secondary"
            self.draw_modern_button(rect, name, style, hover)

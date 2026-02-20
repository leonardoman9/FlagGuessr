import json
import math
from datetime import datetime

import pygame

import audio
from scripts import resource_path


class gui:
    def __init__(self):
        self.width, self.height = 1280, 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("FlagGuessr")

        self.colors = {
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

        # Readable typography set for all UI text.
        # The previous decorative fonts made several strings hard to read.
        self.fonts = {
            "title": pygame.font.SysFont("Helvetica Neue", 60, bold=True),
            "heading": pygame.font.SysFont("Helvetica Neue", 40, bold=True),
            "body": pygame.font.SysFont("Helvetica Neue", 28),
            "small": pygame.font.SysFont("Helvetica Neue", 22, bold=True),
            "tiny": pygame.font.SysFont("Helvetica Neue", 18),
        }

        self.font = self.fonts["body"]
        self.flag_size = (560, 360)
        self.text_vertical_spacing = 30
        self.flags = {}

        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        self.input_text = ""
        self.input_active = True

        self.selected_mode = "normal"
        self.selected_mode_map = "europe"
        self.mode_map_dropdown_open = False

        self.selected_gamemode = "europe"
        self.rankings_gamemode = "europe"
        self.selected_rankings_filter = "all"

        self.music_dropdown_open = False
        self.selected_song = "Random"

        self.scroll_y = 0
        self.max_scroll_y = 0
        self.scroll_bar_rect = None
        self.scroll_handle_rect = None
        self.is_scrolling = False
        self.scroll_offset_y = 0
        self.rankings_content_rect = None

        self.error_message = {
            "active": False,
            "text": "",
            "start_time": 0,
            "duration": 2600,
            "style": "danger",
        }

        self._build_static_background()
        self._init_layout()

    def _init_layout(self):
        cx = self.width // 2
        cy = self.height // 2

        self.play_button_rect = pygame.Rect(cx - 140, cy - 20, 280, 64)
        self.splash_rankings_button_rect = pygame.Rect(cx - 140, cy + 62, 280, 64)
        self.splash_quit_button_rect = pygame.Rect(cx - 140, cy + 144, 280, 64)

        self.music_panel_rect = pygame.Rect(self.width - 338, 20, 310, 176)
        self.music_play_button_rect = pygame.Rect(self.music_panel_rect.x + 14, self.music_panel_rect.y + 46, 86, 34)
        self.music_pause_button_rect = pygame.Rect(self.music_panel_rect.x + 112, self.music_panel_rect.y + 46, 86, 34)
        self.music_stop_button_rect = pygame.Rect(self.music_panel_rect.x + 210, self.music_panel_rect.y + 46, 86, 34)
        self.music_dropdown_rect = pygame.Rect(self.music_panel_rect.x + 14, self.music_panel_rect.y + 96, 282, 34)

        self.input_rect = pygame.Rect(cx - 250, self.height - 94, 500, 54)
        self.input_border = self.input_rect.inflate(4, 4)
        self.game_exit_button_rect = pygame.Rect(self.width - 170, self.height - 78, 140, 48)

        self.mode_map_dropdown_rect = pygame.Rect(self.width - 300, 92, 248, 44)
        mode_w, mode_h, mode_gap = 330, 232, 24
        total_w = mode_w * 3 + mode_gap * 2
        start_x = cx - total_w // 2
        mode_y = 198
        self.mode_normal_button_rect = pygame.Rect(start_x, mode_y, mode_w, mode_h)
        self.mode_endless_button_rect = pygame.Rect(start_x + mode_w + mode_gap, mode_y, mode_w, mode_h)
        self.mode_blitz_button_rect = pygame.Rect(start_x + (mode_w + mode_gap) * 2, mode_y, mode_w, mode_h)
        self.mode_back_button_rect = pygame.Rect(cx - 130, self.height - 82, 260, 50)

        self.quit_button_rect = pygame.Rect(cx - 290, self.height - 96, 180, 58)
        self.rankings_button_rect = pygame.Rect(cx - 90, self.height - 96, 220, 58)
        self.main_menu_button_rect = pygame.Rect(cx + 150, self.height - 96, 220, 58)

        self.rankings_back_button_rect = pygame.Rect(cx - 310, self.height - 82, 250, 50)
        self.rank_sel_main_menu_button_rect = pygame.Rect(cx + 60, self.height - 82, 250, 50)

        self.rank_mode_main_menu_button_rect = pygame.Rect(cx - 130, self.height - 82, 260, 50)

        btn_w, btn_h, col_gap, row_gap = 190, 80, 20, 16
        grid_w = btn_w * 3 + col_gap * 2
        gx = cx - grid_w // 2
        gy = 238
        self.rank_mode_global_button_rect = pygame.Rect(gx, gy, btn_w, btn_h)
        self.rank_mode_europe_button_rect = pygame.Rect(gx + btn_w + col_gap, gy, btn_w, btn_h)
        self.rank_mode_america_button_rect = pygame.Rect(gx + (btn_w + col_gap) * 2, gy, btn_w, btn_h)
        self.rank_mode_asia_button_rect = pygame.Rect(gx, gy + btn_h + row_gap, btn_w, btn_h)
        self.rank_mode_oceania_button_rect = pygame.Rect(gx + btn_w + col_gap, gy + btn_h + row_gap, btn_w, btn_h)
        self.rank_mode_africa_button_rect = pygame.Rect(gx + (btn_w + col_gap) * 2, gy + btn_h + row_gap, btn_w, btn_h)

        tab_y = 152
        tab_h = 46
        tab_w = 150
        tab_gap = 16
        tabs_total = tab_w * 4 + tab_gap * 3
        tx = cx - tabs_total // 2
        self.rank_filter_all_rect = pygame.Rect(tx, tab_y, tab_w, tab_h)
        self.rank_filter_normal_rect = pygame.Rect(tx + tab_w + tab_gap, tab_y, tab_w, tab_h)
        self.rank_filter_endless_rect = pygame.Rect(tx + (tab_w + tab_gap) * 2, tab_y, tab_w, tab_h)
        self.rank_filter_blitz_rect = pygame.Rect(tx + (tab_w + tab_gap) * 3, tab_y, tab_w, tab_h)

    def _build_static_background(self):
        self.background = pygame.Surface((self.width, self.height))

        top = self.colors["bg_top"]
        bottom = self.colors["bg_bottom"]
        for y in range(self.height):
            t = y / max(1, self.height - 1)
            r = int(top[0] + (bottom[0] - top[0]) * t)
            g = int(top[1] + (bottom[1] - top[1]) * t)
            b = int(top[2] + (bottom[2] - top[2]) * t)
            pygame.draw.line(self.background, (r, g, b), (0, y), (self.width, y))

        glow = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(glow, (55, 177, 169, 42), (180, 120), 220)
        pygame.draw.circle(glow, (255, 166, 77, 30), (self.width - 150, self.height - 120), 260)
        pygame.draw.circle(glow, (70, 130, 180, 18), (self.width // 2, self.height // 2), 300)
        self.background.blit(glow, (0, 0))

        for x in range(0, self.width, 64):
            pygame.draw.line(self.background, (24, 34, 48), (x, 0), (x, self.height), 1)
        for y in range(0, self.height, 64):
            pygame.draw.line(self.background, (24, 34, 48), (0, y), (self.width, y), 1)

    def draw_gradient_background(self):
        self.screen.blit(self.background, (0, 0))

    def _draw_panel(self, rect, tone="panel", border=True):
        pygame.draw.rect(self.screen, self.colors[tone], rect, border_radius=14)
        if border:
            pygame.draw.rect(self.screen, self.colors["border"], rect, 2, border_radius=14)

    def draw_modern_button(self, rect, text, style="primary", hover=False, disabled=False):
        if disabled:
            bg = (66, 78, 92)
            border = (96, 108, 120)
            fg = (170, 180, 190)
        elif style == "primary":
            bg = self.colors["primary_dark"] if hover else self.colors["primary"]
            border = (95, 214, 206) if hover else self.colors["primary_dark"]
            fg = self.colors["text"]
        elif style == "secondary":
            bg = (73, 88, 108) if hover else (55, 70, 90)
            border = self.colors["accent"] if hover else self.colors["border"]
            fg = self.colors["text"]
        elif style == "danger":
            bg = (186, 55, 44) if hover else self.colors["danger"]
            border = (245, 114, 102) if hover else (178, 52, 40)
            fg = self.colors["text"]
        else:
            bg = (43, 54, 69)
            border = self.colors["border"]
            fg = self.colors["text"]

        pygame.draw.rect(self.screen, bg, rect, border_radius=12)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=12)
        label = self.fonts["small"].render(text, True, fg)
        self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_modern_button_with_alpha(self, rect, text, style="primary", hover=False, alpha=255):
        temp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        old_screen = self.screen
        self.screen = temp
        self.draw_modern_button(pygame.Rect(0, 0, rect.width, rect.height), text, style, hover)
        self.screen = old_screen
        temp.set_alpha(alpha)
        self.screen.blit(temp, rect.topleft)

    def draw_small_button(self, rect, color, text):
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, self.colors["border"], rect, 2, border_radius=10)
        lbl = self.fonts["tiny"].render(text, True, self.colors["text"])
        self.screen.blit(lbl, lbl.get_rect(center=rect.center))

    def draw_modern_dropdown(self, rect, selected_text, options, dropdown_open=None):
        is_open = self.mode_map_dropdown_open if dropdown_open is None else dropdown_open
        self._draw_panel(rect, tone="panel_alt")
        text = self.fonts["small"].render(selected_text, True, self.colors["text"])
        self.screen.blit(text, (rect.x + 14, rect.y + 10))

        arrow = "^" if is_open else "v"
        arrow_s = self.fonts["small"].render(arrow, True, self.colors["muted"])
        self.screen.blit(arrow_s, arrow_s.get_rect(center=(rect.right - 16, rect.centery)))

    def draw_music_dropdown(self, rect, color, selected_text, song_names):
        self._draw_panel(rect, tone="panel_alt")
        title = self.fonts["tiny"].render(selected_text[:30], True, self.colors["text"])
        self.screen.blit(title, (rect.x + 10, rect.y + 9))

        arrow = "^" if self.music_dropdown_open else "v"
        arr = self.fonts["tiny"].render(arrow, True, self.colors["muted"])
        self.screen.blit(arr, arr.get_rect(center=(rect.right - 14, rect.centery)))

        if self.music_dropdown_open:
            panel_h = min(170, len(song_names) * 32 + 10)
            panel = pygame.Rect(rect.x, rect.bottom + 4, rect.width, panel_h)
            self._draw_panel(panel, tone="panel")

            self.music_option_rects = []
            visible = song_names[:5]
            for i, name in enumerate(visible):
                row = pygame.Rect(panel.x + 6, panel.y + 6 + i * 32, panel.width - 12, 28)
                hover = row.collidepoint((self.mouse_x, self.mouse_y))
                bg = self.colors["panel_soft"] if hover else self.colors["panel"]
                pygame.draw.rect(self.screen, bg, row, border_radius=8)
                txt = self.fonts["tiny"].render(name[:34], True, self.colors["text"])
                self.screen.blit(txt, (row.x + 8, row.y + 5))
                self.music_option_rects.append((name, row))

    def draw_music_controls(self):
        self._draw_panel(self.music_panel_rect, tone="panel")
        label = self.fonts["tiny"].render("MUSIC", True, self.colors["muted"])
        self.screen.blit(label, (self.music_panel_rect.x + 14, self.music_panel_rect.y + 14))

        current_song = audio.get_current_song() or "None"
        song_label = self.fonts["tiny"].render(f"Now: {current_song[:22]}", True, self.colors["text"])
        self.screen.blit(song_label, (self.music_panel_rect.x + 14, self.music_panel_rect.y + 144))

        play_hover = self.music_play_button_rect.collidepoint((self.mouse_x, self.mouse_y))
        pause_hover = self.music_pause_button_rect.collidepoint((self.mouse_x, self.mouse_y))
        stop_hover = self.music_stop_button_rect.collidepoint((self.mouse_x, self.mouse_y))

        self.draw_modern_button(self.music_play_button_rect, "PLAY", "primary", play_hover)
        self.draw_modern_button(self.music_pause_button_rect, "PAUSE", "secondary", pause_hover)
        self.draw_modern_button(self.music_stop_button_rect, "STOP", "danger", stop_hover)

        song_names = ["Random"] + audio.get_song_names()
        self.draw_music_dropdown(self.music_dropdown_rect, self.colors["panel_alt"], self.selected_song, song_names)

    def draw_game_music_controls(self):
        self.draw_music_controls()

    def _flash_message(self, text, style="danger", duration=2600):
        self.error_message["active"] = True
        self.error_message["text"] = text
        self.error_message["start_time"] = pygame.time.get_ticks()
        self.error_message["duration"] = duration
        self.error_message["style"] = style

    def handle_music_controls_click(self, mouse_pos):
        if self.music_play_button_rect.collidepoint(mouse_pos):
            if self.selected_song == "Random":
                audio.playMusic(random_song=True)
            else:
                audio.playMusic(song_name=self.selected_song)
            return True

        if self.music_pause_button_rect.collidepoint(mouse_pos):
            audio.pauseMusic()
            return True

        if self.music_stop_button_rect.collidepoint(mouse_pos):
            audio.stopMusic()
            return True

        if self.music_dropdown_rect.collidepoint(mouse_pos):
            self.music_dropdown_open = not self.music_dropdown_open
            return True

        if self.music_dropdown_open:
            song_names = ["Random"] + audio.get_song_names()
            panel_h = min(170, len(song_names) * 32 + 10)
            panel = pygame.Rect(self.music_dropdown_rect.x, self.music_dropdown_rect.bottom + 4, self.music_dropdown_rect.width, panel_h)

            if panel.collidepoint(mouse_pos):
                for i, name in enumerate(song_names[:5]):
                    row = pygame.Rect(panel.x + 6, panel.y + 6 + i * 32, panel.width - 12, 28)
                    if row.collidepoint(mouse_pos):
                        self.selected_song = name
                        self.music_dropdown_open = False
                        if name == "Random":
                            audio.playMusic(random_song=True)
                        else:
                            audio.playMusic(song_name=name)
                        return True
            else:
                self.music_dropdown_open = False

        return False

    def handle_game_music_click(self, mouse_pos):
        return self.handle_music_controls_click(mouse_pos)

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
        play_hover = self.play_button_rect.collidepoint(mouse_pos)
        rank_hover = self.splash_rankings_button_rect.collidepoint(mouse_pos)
        quit_hover = self.splash_quit_button_rect.collidepoint(mouse_pos)

        self.draw_modern_button(self.play_button_rect, "PLAY", "primary", play_hover)
        self.draw_modern_button(self.splash_rankings_button_rect, "RANKINGS", "secondary", rank_hover)
        self.draw_modern_button(self.splash_quit_button_rect, "QUIT", "danger", quit_hover)

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
            if game_start_time > 0:
                elapsed = (pygame.time.get_ticks() - game_start_time) / 1000
            else:
                elapsed = 0
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

        text_to_show = self.input_text if self.input_text else ""
        text_surface = self.fonts["body"].render(text_to_show, True, self.colors["text"])
        self.screen.blit(text_surface, (self.input_rect.x + 14, self.input_rect.y + 14))

    def showGameOver(self, score, wrong_countries, gamemode):
        self.draw_gradient_background()

        panel = pygame.Rect(self.width // 2 - 430, 92, 860, 470)
        self._draw_panel(panel, tone="panel")

        title = self.fonts["title"].render("GAME OVER", True, self.colors["danger"])
        self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 74)))

        subtitle = self.fonts["body"].render(f"Map: {gamemode.upper()}    Score: {score}", True, self.colors["text"])
        self.screen.blit(subtitle, subtitle.get_rect(center=(panel.centerx, panel.y + 132)))

        wrong_title = self.fonts["small"].render("Mistakes", True, self.colors["accent"])
        self.screen.blit(wrong_title, (panel.x + 40, panel.y + 184))

        if wrong_countries:
            preview = wrong_countries[:8]
            for i, country in enumerate(preview):
                row = self.fonts["tiny"].render(f"{i + 1}. {country}", True, self.colors["muted"])
                self.screen.blit(row, (panel.x + 40, panel.y + 216 + i * 28))
        else:
            none = self.fonts["tiny"].render("No wrong answers recorded.", True, self.colors["muted"])
            self.screen.blit(none, (panel.x + 40, panel.y + 216))

        mouse_pos = pygame.mouse.get_pos()
        self.draw_modern_button(self.quit_button_rect, "QUIT", "danger", self.quit_button_rect.collidepoint(mouse_pos))
        self.draw_modern_button(self.rankings_button_rect, "SEE RANKINGS", "secondary", self.rankings_button_rect.collidepoint(mouse_pos))
        self.draw_modern_button(self.main_menu_button_rect, "MAIN MENU", "primary", self.main_menu_button_rect.collidepoint(mouse_pos))

        pygame.display.flip()

    def showVictory(self, score, gamemode):
        self.draw_gradient_background()

        panel = pygame.Rect(self.width // 2 - 430, 92, 860, 470)
        self._draw_panel(panel, tone="panel")

        title = self.fonts["title"].render("VICTORY", True, self.colors["success"])
        self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 74)))

        subtitle = self.fonts["body"].render(f"Completed {gamemode.upper()} with score {score}", True, self.colors["text"])
        self.screen.blit(subtitle, subtitle.get_rect(center=(panel.centerx, panel.y + 132)))

        msg = self.fonts["small"].render("Great run. Try endless or blitz for a new challenge.", True, self.colors["muted"])
        self.screen.blit(msg, msg.get_rect(center=(panel.centerx, panel.y + 230)))

        mouse_pos = pygame.mouse.get_pos()
        self.draw_modern_button(self.quit_button_rect, "QUIT", "danger", self.quit_button_rect.collidepoint(mouse_pos))
        self.draw_modern_button(self.rankings_button_rect, "SEE RANKINGS", "secondary", self.rankings_button_rect.collidepoint(mouse_pos))
        self.draw_modern_button(self.main_menu_button_rect, "MAIN MENU", "primary", self.main_menu_button_rect.collidepoint(mouse_pos))

        pygame.display.flip()

    def showModeSelection(self, gamemodes):
        self.draw_gradient_background()

        title = self.fonts["heading"].render("SELECT MODE", True, self.colors["text"])
        subtitle = self.fonts["small"].render("Choose rules and map before starting", True, self.colors["muted"])
        self.screen.blit(title, title.get_rect(center=(self.width // 2, 54)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(self.width // 2, 88)))

        map_label = self.fonts["tiny"].render("MAP", True, self.colors["accent"])
        self.screen.blit(map_label, (self.mode_map_dropdown_rect.x, self.mode_map_dropdown_rect.y - 20))
        self.draw_map_dropdown(gamemodes)

        cards = [
            (self.mode_normal_button_rect, "NORMAL", "Complete all flags", "primary"),
            (self.mode_endless_button_rect, "ENDLESS", "No finish line, 3 lives", "secondary"),
            (self.mode_blitz_button_rect, "BLITZ", "60 seconds speed run", "danger"),
        ]

        mouse_pos = pygame.mouse.get_pos()
        for rect, name, desc, style in cards:
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

            panel = pygame.Rect(
                self.mode_map_dropdown_rect.x,
                self.mode_map_dropdown_rect.bottom + 4,
                self.mode_map_dropdown_rect.width,
                len(["GLOBAL", "EUROPE", "OCEANIA", "AFRICA", "ASIA", "AMERICA"]) * 36 + 8,
            )
            if not panel.collidepoint(mouse_pos):
                self.mode_map_dropdown_open = False
            return None

        if self.mode_normal_button_rect.collidepoint(mouse_pos):
            self.selected_mode = "normal"
            return self.selected_mode, self.selected_mode_map

        if self.mode_endless_button_rect.collidepoint(mouse_pos):
            self.selected_mode = "endless"
            return self.selected_mode, self.selected_mode_map

        if self.mode_blitz_button_rect.collidepoint(mouse_pos):
            self.selected_mode = "blitz"
            return self.selected_mode, self.selected_mode_map

        if self.mode_back_button_rect.collidepoint(mouse_pos):
            return "back"

        return None

    def showModeSelectionScreen(self):
        self.draw_gradient_background()

        title = self.fonts["heading"].render("RANKINGS MAP", True, self.colors["text"])
        subtitle = self.fonts["small"].render("Choose a map to view top scores", True, self.colors["muted"])
        self.screen.blit(title, title.get_rect(center=(self.width // 2, 84)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(self.width // 2, 120)))

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
            hover = rect.collidepoint(mouse_pos)
            self.draw_modern_button(rect, name, "secondary", hover)

        self.draw_modern_button(
            self.rank_mode_main_menu_button_rect,
            "BACK",
            "primary",
            self.rank_mode_main_menu_button_rect.collidepoint(mouse_pos),
        )

        pygame.display.flip()

    def showRankings(self, scores, gamemode):
        self.draw_gradient_background()

        title = self.fonts["heading"].render("TOP RANKINGS", True, self.colors["text"])
        subtitle = self.fonts["small"].render(gamemode.upper(), True, self.colors["accent"])
        self.screen.blit(title, title.get_rect(center=(self.width // 2, 66)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(self.width // 2, 102)))

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

        x_positions = [24, 112, 230, 410, 610]
        for header, x in zip(headers, x_positions):
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
        x_positions = [24, 112, 230, 410, 610]
        for i, value in enumerate(values):
            font = self.fonts["small"] if i < 2 else self.fonts["tiny"]
            color = self.colors["text"] if i < 2 else self.colors["muted"]
            txt = font.render(str(value), True, color)
            surface.blit(txt, txt.get_rect(centery=card_rect.centery, x=x_positions[i]))

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

    def handle_ranking_filter_click(self, mouse_pos):
        if self.rank_filter_all_rect.collidepoint(mouse_pos):
            self.selected_rankings_filter = "all"
            self.scroll_y = 0
            return True
        if self.rank_filter_normal_rect.collidepoint(mouse_pos):
            self.selected_rankings_filter = "normal"
            self.scroll_y = 0
            return True
        if self.rank_filter_endless_rect.collidepoint(mouse_pos):
            self.selected_rankings_filter = "endless"
            self.scroll_y = 0
            return True
        if self.rank_filter_blitz_rect.collidepoint(mouse_pos):
            self.selected_rankings_filter = "blitz"
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

    def get_selected_gamemode(self):
        return self.selected_gamemode

    def set_selected_gamemode(self, gamemode):
        self.selected_gamemode = gamemode

    def get_rankings_gamemode(self):
        return self.rankings_gamemode

    def set_rankings_gamemode(self, gamemode):
        self.rankings_gamemode = gamemode

    def toggle_dropdown(self):
        self.mode_map_dropdown_open = not self.mode_map_dropdown_open

    def close_dropdown(self):
        self.mode_map_dropdown_open = False

    def is_dropdown_open(self):
        return self.mode_map_dropdown_open

    def handle_dropdown_click(self, mouse_pos, gamemodes):
        return False

    def reset_animations(self, screen_type="splash"):
        return None

    def get_animation_alpha(self, animation_name):
        return 255

    def get_animation_offset(self, animation_name, start_offset=50):
        return 0

    def trigger_feedback_animation(self, feedback_type):
        return None

    def draw_animated_surface(self, surface, rect, animation_name, slide_direction="up"):
        self.screen.blit(surface, rect)

    def draw_loading_indicator(self, x, y, size=40):
        ticks = pygame.time.get_ticks() / 220
        for i in range(8):
            angle = i * (math.pi / 4)
            px = x + math.cos(angle) * size * 0.5
            py = y + math.sin(angle) * size * 0.5
            alpha = int(80 + 175 * ((i + ticks) % 8) / 8)
            dot = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(dot, (255, 255, 255, alpha), (4, 4), 4)
            self.screen.blit(dot, (px, py))

    def set_state(self, new_state):
        return None

    def getWidthHeight(self):
        return self.width, self.height

    def getScreen(self):
        return self.screen

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width

    def getFlags(self):
        return self.flags

    def getFlagSize(self):
        return self.flag_size

    def getFont(self):
        return self.font

    def get_text_vertical_spacing(self):
        return self.text_vertical_spacing

    def get_input_text(self):
        return self.input_text

    def get_input_border(self):
        return self.input_border

    def get_input_rect(self):
        return self.input_rect

    def get_input_color(self):
        return self.colors["primary"]

    def get_input_active(self):
        return self.input_active

    def get_input_borde(self):
        return self.input_border

    def set_input_text(self, new_text):
        self.input_text = new_text

    def get_x_y(self):
        return self.mouse_x, self.mouse_y

    def get_mouse_x(self):
        return self.mouse_x

    def get_mouse_y(self):
        return self.mouse_y

    def set_mouse_x_y(self, mouse_pos):
        self.mouse_x, self.mouse_y = mouse_pos
        return self.mouse_x, self.mouse_y

    def get_quit_button_rect(self):
        return self.quit_button_rect

    def get_rankings_button_rect(self):
        return self.rankings_button_rect

    def get_game_exit_button_rect(self):
        return self.game_exit_button_rect

    def show_error_message(self, message):
        self._flash_message(message, style="danger")

    def clear_error_message(self):
        self.error_message["active"] = False
        self.error_message["text"] = ""

    def update_error_message(self):
        if not self.error_message["active"]:
            return False

        now = pygame.time.get_ticks()
        elapsed = now - self.error_message["start_time"]
        if elapsed >= self.error_message["duration"]:
            self.error_message["active"] = False
            return True
        return False

    def draw_error_message_overlay(self):
        if not self.error_message["active"]:
            return

        now = pygame.time.get_ticks()
        elapsed = now - self.error_message["start_time"]
        duration = self.error_message["duration"]

        if elapsed < 250:
            alpha = int(255 * (elapsed / 250))
        elif elapsed > duration - 350:
            alpha = int(255 * max(0, duration - elapsed) / 350)
        else:
            alpha = 255

        msg = self.error_message["text"]
        tone = self.colors["danger"] if self.error_message["style"] == "danger" else self.colors["success"]

        text = self.fonts["small"].render(msg[:64], True, self.colors["text"])
        box_w = max(420, text.get_width() + 40)
        box_h = 56
        box = pygame.Rect(self.width // 2 - box_w // 2, self.height - 164, box_w, box_h)

        overlay = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (18, 25, 36, alpha), overlay.get_rect(), border_radius=12)
        pygame.draw.rect(overlay, (*tone, alpha), overlay.get_rect(), 2, border_radius=12)
        text.set_alpha(alpha)
        overlay.blit(text, text.get_rect(center=overlay.get_rect().center))

        self.screen.blit(overlay, box.topleft)

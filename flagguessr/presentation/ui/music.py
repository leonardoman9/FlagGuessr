from __future__ import annotations

import pygame

from flagguessr.infrastructure import audio


class MusicMixin:
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

    def handle_music_controls_click(self, mouse_pos):
        if self.music_play_button_rect.collidepoint(mouse_pos):
            if self.selected_song == "Random":
                audio.play_music(random_song=True)
            else:
                audio.play_music(song_name=self.selected_song)
            return True

        if self.music_pause_button_rect.collidepoint(mouse_pos):
            audio.pause_music()
            return True

        if self.music_stop_button_rect.collidepoint(mouse_pos):
            audio.stop_music()
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
                            audio.play_music(random_song=True)
                        else:
                            audio.play_music(song_name=name)
                        return True
            else:
                self.music_dropdown_open = False

        return False

    def handle_game_music_click(self, mouse_pos):
        return self.handle_music_controls_click(mouse_pos)

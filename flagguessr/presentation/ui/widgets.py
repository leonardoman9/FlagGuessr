from __future__ import annotations

import math

import pygame


class WidgetMixin:
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

    def _flash_message(self, text, style="danger", duration=2600):
        self.error_message["active"] = True
        self.error_message["text"] = text
        self.error_message["start_time"] = pygame.time.get_ticks()
        self.error_message["duration"] = duration
        self.error_message["style"] = style

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

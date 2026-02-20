import pygame

from flagguessr.presentation.ui.background import build_static_background
from flagguessr.presentation.ui.interactions import InteractionMixin
from flagguessr.presentation.ui.layout import initialize_layout
from flagguessr.presentation.ui.music import MusicMixin
from flagguessr.presentation.ui.screens import ScreenMixin
from flagguessr.presentation.ui.theme import build_color_palette, build_fonts
from flagguessr.presentation.ui.widgets import WidgetMixin


class GUI(WidgetMixin, MusicMixin, ScreenMixin, InteractionMixin):
    def __init__(self):
        self.width, self.height = 1280, 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("FlagGuessr")

        self.colors = build_color_palette()
        self.fonts = build_fonts()

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
        self.mode_map_option_rects = []

        self.rankings_gamemode = "europe"
        self.selected_rankings_filter = "all"

        self.music_dropdown_open = False
        self.selected_song = "Random"
        self.music_option_rects = []

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
        initialize_layout(self)

    def _build_static_background(self):
        self.background = build_static_background(self.width, self.height, self.colors)

    def get_rankings_gamemode(self):
        return self.rankings_gamemode

    def set_rankings_gamemode(self, gamemode):
        self.rankings_gamemode = gamemode

    def getFlagSize(self):
        return self.flag_size

    def get_input_text(self):
        return self.input_text

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


# Backward-compatible alias for older imports/tests.
gui = GUI

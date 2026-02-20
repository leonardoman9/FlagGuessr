from __future__ import annotations

import pygame


def initialize_layout(ui) -> None:
    cx = ui.width // 2
    cy = ui.height // 2

    ui.play_button_rect = pygame.Rect(cx - 140, cy - 20, 280, 64)
    ui.splash_rankings_button_rect = pygame.Rect(cx - 140, cy + 62, 280, 64)
    ui.splash_quit_button_rect = pygame.Rect(cx - 140, cy + 144, 280, 64)

    ui.music_panel_rect = pygame.Rect(ui.width - 338, 20, 310, 176)
    ui.music_play_button_rect = pygame.Rect(ui.music_panel_rect.x + 14, ui.music_panel_rect.y + 46, 86, 34)
    ui.music_pause_button_rect = pygame.Rect(ui.music_panel_rect.x + 112, ui.music_panel_rect.y + 46, 86, 34)
    ui.music_stop_button_rect = pygame.Rect(ui.music_panel_rect.x + 210, ui.music_panel_rect.y + 46, 86, 34)
    ui.music_dropdown_rect = pygame.Rect(ui.music_panel_rect.x + 14, ui.music_panel_rect.y + 96, 282, 34)

    ui.input_rect = pygame.Rect(cx - 250, ui.height - 94, 500, 54)
    ui.input_border = ui.input_rect.inflate(4, 4)
    ui.game_exit_button_rect = pygame.Rect(ui.width - 170, ui.height - 78, 140, 48)

    ui.mode_map_dropdown_rect = pygame.Rect(ui.width - 300, 146, 248, 44)
    mode_w, mode_h, mode_gap = 330, 232, 24
    total_w = mode_w * 3 + mode_gap * 2
    start_x = cx - total_w // 2
    mode_y = 198
    ui.mode_normal_button_rect = pygame.Rect(start_x, mode_y, mode_w, mode_h)
    ui.mode_endless_button_rect = pygame.Rect(start_x + mode_w + mode_gap, mode_y, mode_w, mode_h)
    ui.mode_blitz_button_rect = pygame.Rect(start_x + (mode_w + mode_gap) * 2, mode_y, mode_w, mode_h)
    ui.mode_back_button_rect = pygame.Rect(cx - 130, ui.height - 82, 260, 50)

    ui.quit_button_rect = pygame.Rect(cx - 290, ui.height - 96, 180, 58)
    ui.rankings_button_rect = pygame.Rect(cx - 90, ui.height - 96, 220, 58)
    ui.main_menu_button_rect = pygame.Rect(cx + 150, ui.height - 96, 220, 58)

    ui.rankings_back_button_rect = pygame.Rect(cx - 310, ui.height - 82, 250, 50)
    ui.rank_sel_main_menu_button_rect = pygame.Rect(cx + 60, ui.height - 82, 250, 50)

    ui.rank_mode_main_menu_button_rect = pygame.Rect(cx - 130, ui.height - 82, 260, 50)

    btn_w, btn_h, col_gap, row_gap = 190, 80, 20, 16
    grid_w = btn_w * 3 + col_gap * 2
    gx = cx - grid_w // 2
    gy = 238
    ui.rank_mode_global_button_rect = pygame.Rect(gx, gy, btn_w, btn_h)
    ui.rank_mode_europe_button_rect = pygame.Rect(gx + btn_w + col_gap, gy, btn_w, btn_h)
    ui.rank_mode_america_button_rect = pygame.Rect(gx + (btn_w + col_gap) * 2, gy, btn_w, btn_h)
    ui.rank_mode_asia_button_rect = pygame.Rect(gx, gy + btn_h + row_gap, btn_w, btn_h)
    ui.rank_mode_oceania_button_rect = pygame.Rect(gx + btn_w + col_gap, gy + btn_h + row_gap, btn_w, btn_h)
    ui.rank_mode_africa_button_rect = pygame.Rect(gx + (btn_w + col_gap) * 2, gy + btn_h + row_gap, btn_w, btn_h)

    tab_y = 152
    tab_h = 46
    tab_w = 150
    tab_gap = 16
    tabs_total = tab_w * 4 + tab_gap * 3
    tx = cx - tabs_total // 2
    ui.rank_filter_all_rect = pygame.Rect(tx, tab_y, tab_w, tab_h)
    ui.rank_filter_normal_rect = pygame.Rect(tx + tab_w + tab_gap, tab_y, tab_w, tab_h)
    ui.rank_filter_endless_rect = pygame.Rect(tx + (tab_w + tab_gap) * 2, tab_y, tab_w, tab_h)
    ui.rank_filter_blitz_rect = pygame.Rect(tx + (tab_w + tab_gap) * 3, tab_y, tab_w, tab_h)

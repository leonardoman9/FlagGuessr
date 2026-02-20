import pygame
import random
import sys
import os

from countries import countries
import audio
import db
from gui import gui
from scripts import resource_path, get_user_data_path

# Initialize Pygame
icon = pygame.image.load(resource_path("data/icon.ico"))
pygame.display.set_icon(icon)
pygame.init()

# Database setup
db_scores = get_user_data_path("scores.db")
db_flags = get_user_data_path("flags.db")

# Ensure the 'scores' table is created
db.create_scores_table(db_scores)
# Populate the flags database if it's empty
db.populate_flags_database(db_flags)

# Game constants
MAXLIVES = 3
INITSCORE = 0
GAMEMODES = ["global", "europe", "oceania", "africa", "asia", "america"]

# Game variables
score = INITSCORE
lives = MAXLIVES
wrong_countries = []
selected_game_mode = "normal"
selected_map = "europe"
flags_shown_count = 0
game_start_time = 0
blitz_time_limit = 60
game_countries = {}
game_flags_images = {}
countries_list = []
current_country = None

# --- State Management ---
current_state = "splash"
previous_screen_for_rankings = None  # Remembers where we came from to rankings

def change_state(new_state):
    """Changes the current game state."""
    global current_state
    print(f"Changing state from '{current_state}' to '{new_state}'")
    current_state = new_state

# Initialize audio mixer
if not audio.init_mixer():
    print("Warning: Audio mixer failed to initialize. Music will not work.")

# Start with random music
audio.playMusic(random_song=True)

# Load the GUI and countries classes
g = gui()
countries = countries()

# Main game loop
running = True
while running:
    if current_state == "splash":
        g.showSplashScreen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                g.set_mouse_x_y(mouse_pos)
                if g.handle_music_controls_click(mouse_pos):
                    continue
                if g.play_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                    change_state("mode_selection")
                if g.splash_rankings_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                    previous_screen_for_rankings = "splash"
                    change_state("rankings_map_selection")
                if g.splash_quit_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                    running = False

    elif current_state == "mode_selection":
        g.showModeSelection(GAMEMODES)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION, pygame.MOUSEWHEEL]:
                mouse_pos = pygame.mouse.get_pos()
                g.set_mouse_x_y(mouse_pos)
                mode_result = g.handle_mode_selection_click(event, mouse_pos)
                if mode_result:
                    if mode_result == "back":
                        change_state("splash")
                    else:
                        selected_game_mode, selected_map = mode_result
                        # Reset and initialize game variables
                        score = INITSCORE
                        lives = MAXLIVES
                        wrong_countries = []
                        flags_shown_count = 0
                        g.set_input_text("")
                        g.clear_error_message()
                        if selected_game_mode == "blitz":
                            game_start_time = pygame.time.get_ticks()
                        
                        game_countries = countries.load_countries(db_flags, selected_map.lower())
                        if not game_countries:
                            g.show_error_message("No countries found for the selected map.")
                            continue

                        game_flags_images = countries.load_flags_images(game_countries, g.getFlagSize())
                        if not game_flags_images:
                            g.show_error_message("No flag images available for the selected map.")
                            continue

                        available_country_names = list(game_flags_images.keys())
                        current_country = random.choice(available_country_names)
                        countries_list = [current_country]
                        if selected_game_mode != "normal":
                            flags_shown_count = 1
                        
                        change_state("game")

    elif current_state == "game":
        if selected_game_mode == "blitz" and game_start_time > 0:
            elapsed_time = (pygame.time.get_ticks() - game_start_time) / 1000
            if elapsed_time >= blitz_time_limit:
                db.insert_score(db_scores, score, countries_list, wrong_countries, selected_map, selected_game_mode, blitz_time_limit, flags_shown_count, {})
                change_state("game_over")
                continue

        if not game_flags_images:
            g.show_error_message("No flags loaded. Returning to mode selection.")
            change_state("mode_selection")
            continue
        
        g.showGame(current_country, score, game_flags_images, lives, selected_game_mode, game_start_time, blitz_time_limit, flags_shown_count)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                g.set_mouse_x_y(mouse_pos)
                if g.get_game_exit_button_rect().collidepoint(mouse_pos):
                    change_state("splash")
                    continue
                g.handle_game_music_click(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    user_guess = g.get_input_text().strip().lower()
                    if user_guess == current_country.lower():
                        score += 1
                        g.clear_error_message()
                        if selected_game_mode == "normal":
                            available_countries = [c for c in game_flags_images.keys() if c not in countries_list]
                            if available_countries:
                                current_country = random.choice(available_countries)
                                countries_list.append(current_country)
                            else:
                                db.insert_score(db_scores, score, countries_list, wrong_countries, selected_map, selected_game_mode, 0, len(countries_list), {"completion": True})
                                change_state("victory")
                        else:
                            current_country = random.choice(list(game_flags_images.keys()))
                            countries_list.append(current_country)
                            flags_shown_count += 1
                        g.set_input_text("")
                    else:
                        lives -= 1
                        wrong_countries.append(current_country)
                        g.show_error_message(f"Wrong! It was: {current_country}")
                        if lives <= 0:
                            time_taken = 0
                            if selected_game_mode == "blitz":
                                time_taken = int((pygame.time.get_ticks() - game_start_time) / 1000)
                            db.insert_score(db_scores, score, countries_list, wrong_countries, selected_map, selected_game_mode, time_taken, flags_shown_count, {})
                            change_state("game_over")
                        else:
                            if selected_game_mode == "normal":
                                available_countries = [c for c in game_flags_images.keys() if c not in countries_list]
                                if available_countries:
                                    current_country = random.choice(available_countries)
                                    countries_list.append(current_country)
                                else: # Should not happen if lives > 0
                                    change_state("victory")
                            else:
                                current_country = random.choice(list(game_flags_images.keys()))
                                countries_list.append(current_country)
                                flags_shown_count += 1
                        g.set_input_text("")
                elif event.key == pygame.K_BACKSPACE:
                    g.set_input_text(g.get_input_text()[:-1])
                else:
                    g.set_input_text(g.get_input_text() + event.unicode)

    elif current_state == "game_over":
        g.showGameOver(score, wrong_countries, selected_map)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                g.set_mouse_x_y(pygame.mouse.get_pos())
                if g.get_quit_button_rect().collidepoint(g.get_x_y()):
                    running = False
                elif g.get_rankings_button_rect().collidepoint(g.get_x_y()):
                    previous_screen_for_rankings = "game_over"
                    g.set_rankings_gamemode(selected_map)
                    change_state("rankings")
                elif g.main_menu_button_rect.collidepoint(g.get_x_y()):
                    change_state("splash")

    elif current_state == "victory":
        g.showVictory(score, selected_map)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                g.set_mouse_x_y(pygame.mouse.get_pos())
                if g.get_quit_button_rect().collidepoint(g.get_x_y()):
                    running = False
                elif g.get_rankings_button_rect().collidepoint(g.get_x_y()):
                    previous_screen_for_rankings = "victory"
                    g.set_rankings_gamemode(selected_map)
                    change_state("rankings")
                elif g.main_menu_button_rect.collidepoint(g.get_x_y()):
                    change_state("splash")

    elif current_state == "rankings":
        rankings_gamemode = g.get_rankings_gamemode()
        rankings_filter = g.selected_rankings_filter
        top_scores = db.get_top_scores(db_scores, rankings_gamemode, rankings_filter, limit=10)
        g.showRankings(top_scores, rankings_gamemode)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION, pygame.MOUSEWHEEL]:
                mouse_pos = pygame.mouse.get_pos()
                g.set_mouse_x_y(mouse_pos)
                if g.handle_scroll(event, mouse_pos):
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if g.handle_ranking_filter_click(mouse_pos):
                        continue
                    if g.rankings_back_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        if previous_screen_for_rankings == "victory":
                            change_state("victory")
                        elif previous_screen_for_rankings == "game_over":
                            change_state("game_over")
                        else:
                            change_state("rankings_map_selection")
                    if g.rank_sel_main_menu_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        change_state("splash")

    elif current_state == "rankings_map_selection":
        g.showModeSelectionScreen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                result = g.handle_rankings_mode_click(mouse_pos)
                if result:
                    if result == "back":
                        change_state("splash")
                    else:
                        change_state("rankings")

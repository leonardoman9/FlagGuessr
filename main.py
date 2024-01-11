import pygame
import random
import sys
import os
import sqlite3
from datetime import datetime
import countries
import scripts
import audio
import db
import gui

# Initialize Pygame
icon = pygame.image.load("data/icon.ico")
pygame.display.set_icon(icon)
pygame.init()

# Database setup
db_filename = "scores.db"


# Ensure the 'scores' table is created
db.create_scores_table(db_filename)

#Game constants
MAXLIVES = 3
INITSCORE = 0
GAMEMODES = ["global",
             "europe",
             "oceania",
             "africa",
             "asia",
             "america"]

# Game variables
score = INITSCORE
lives = MAXLIVES
music = True
selected_gamemode = "asia"

# Game loop
running = True
splash_screen = True
game = False
game_over = False
show_rankings = False
game_mode_selection = False

#Start music
audio.playMusic(music)


try:
    if selected_gamemode.lower() in GAMEMODES:
        game_countries = countries.countries(selected_gamemode.lower())
    else:
        print("!!! Gamemode not valid !!! Quitting")
        sys.exit()
    current_country = random.choice(list
                                (game_countries
                                 .getResult()
                                 .keys()))
    countries_list, wrong_countries = [], []
    countries_list.append(current_country)
    
except Exception as e:
    print("Error while choosing gamemode:\n", e)
g = gui.gui(game_countries)
print(f"CURRENT GAME SEQUENCE: {current_country}", end=", ", flush=True)

def setGameLoop(sc, r, g, go, sr, gms):
    global splash_screen, running, game, game_over, show_rankings, game_mode_selection
    splash_screen = sc
    running = r
    game = g
    game_over = go
    show_rankings = sr
    game_mode_selection = gms


while running:
    if splash_screen and not show_rankings:
        g.showSplashScreen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.set_mouse_x_y(pygame.mouse.get_pos())
                    if g.play_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        setGameLoop(False, True, True, False, False, False)
                    if g.splash_rankings_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        setGameLoop(False, True, False, False, False, True)
                    if g.splash_quit_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        setGameLoop(False, False, False, False, False, False)
                    if g.mute_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        audio.stopMusic()

    if splash_screen and show_rankings:
        pass

    if game_mode_selection:
        g.showModeSelectionScreen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                setGameLoop(False, True, False, False, False, False)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.set_mouse_x_y(pygame.mouse.get_pos())
                    if g.rank_mode_global_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        top_scores = db.get_top_scores(db_filename, "global", limit=10)
                        g.showRankingsFromMenu(top_scores, "global")
                        setGameLoop(False, True, False, False, True,False)
                    if g.rank_mode_europe_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        top_scores = db.get_top_scores(db_filename, "europe", limit=10)
                        g.showRankings(top_scores, "europe")
                    if g.rank_mode_america_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        top_scores = db.get_top_scores(db_filename, "america", limit=10)
                        g.showRankingsFromMenu(top_scores, "america")
                    if g.rank_mode_asia_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        top_scores = db.get_top_scores(db_filename, "asia", limit=10)
                        g.showRankingsFromMenu(top_scores, "asia")
                    if g.rank_mode_oceania_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        top_scores = db.get_top_scores(db_filename, "oceania", limit=10)
                        g.showRankingsFromMenu(top_scores, "oceania")
                    if g.rank_mode_africa_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        top_scores = db.get_top_scores(db_filename, "africa", limit=10)
                        g.showRankingsFromMenu(top_scores, "africa")
                    if g.rank_mode_main_menu_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        setGameLoop(True, True, False, False, False, False)
                    while game_mode_selection:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                setGameLoop(False, False, False, False, False, False)
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                g.set_mouse_x_y(pygame.mouse.get_pos())
                               
                                


    if game:
        g.showGame(current_country, score, lives)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_RETURN:
                    # Check the user's input
                    if g.get_input_text().lower() == current_country.lower():
                        # Correct guess
                        score += 1
                        current_country = random.choice(list(game_countries.getResult().keys()))
                        print(current_country, end=", ", flush=True)
                        countries_list.append(current_country)
                        g.set_input_text("")
                    else:
                        # Incorrect guess
                        lives -= 1
                        wrong_countries.append(current_country)
                        print(f"<-WRONG!", end=", ", flush = True)
                        if lives == 0:
                            # Game over if no lives left
                            db.insert_score(db_filename, score, countries_list, wrong_countries, selected_gamemode)  # Save the score to the database
                            print(f"\n\nFull game: {countries_list}")
                            print(f"\nMistaken countries: {wrong_countries}")
                            game_over = True

                elif event.key == pygame.K_BACKSPACE:
                    g.set_input_text(g.get_input_text()[:-1])
                else:
                    g.set_input_text(g.get_input_text() + event.unicode)

    if game_over:
        # Display game over screen with Quit and Rankings buttons 
        g.showGameOver(score,wrong_countries,selected_gamemode)
        #Events Handling
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    setGameLoop(False, False, False, False, False)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.set_mouse_x_y(pygame.mouse.get_pos())
                    if g.get_quit_button_rect().collidepoint(g.get_x_y()):
                        setGameLoop(False, False, False, False, False, False)
                    elif g.get_rankings_button_rect().collidepoint(g.get_x_y()):
                        setGameLoop(False, True, False, False, True, False)
                    elif g.main_menu_button_rect.collidepoint(g.get_x_y()):
                        setGameLoop(True, True, False, False, False, False)

    if show_rankings:
        # Display rankings
        top_scores = db.get_top_scores(db_filename, selected_gamemode, limit=10)
        g.showRankings(top_scores, selected_gamemode)
        #Events handling
        while show_rankings:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    setGameLoop(False, False, False, False, False, False)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.set_mouse_x_y(pygame.mouse.get_pos())
                    if g.rankings_back_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        setGameLoop(False, True, False, True, False, False)
                    if g.rank_sel_main_menu_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        setGameLoop(True, True, False, False, False, False)


# Quit Pygame
pygame.quit()
sys.exit()

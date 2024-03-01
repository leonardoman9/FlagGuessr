import pygame
import random
import sys

from countries import countries
import audio
import db
from gui import gui

# Initialize Pygame
icon = pygame.image.load("data/icon.ico")
pygame.display.set_icon(icon)
pygame.init()

# Database setup
db_scores = "scores.db"
db_flags = "flags.db"

# Ensure the 'scores' table is created
db.create_scores_table(db_scores)

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
music = False
selected_gamemode = 'europe'

print(f"selected gamemode: {selected_gamemode}")

# Game loop
running = True
splash_screen = True
game = False
game_over = False
show_rankings = False
game_mode_selection = False

#Start music
audio.playMusic(music)

# load the gui and countries classes
g = gui() 
countries = countries()

def setGameLoop(set_splash_screen, set_running, 
                set_game, set_gameover, 
                set_show_rankings, set_game_mode_selection):
    global splash_screen, running, game, game_over, show_rankings, game_mode_selection
    splash_screen = set_splash_screen
    running = set_running
    game = set_game
    game_over = set_gameover
    show_rankings = set_show_rankings
    game_mode_selection = set_game_mode_selection


while running:
    if splash_screen and not show_rankings:
        g.showSplashScreen(GAMEMODES)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.set_mouse_x_y(pygame.mouse.get_pos())
                    if g.play_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        score = INITSCORE
                        lives = MAXLIVES
                        print(f"selected gamemode: {selected_gamemode}")
                        g.set_input_text("")
                        try:
                            # Load countries from the database
                            if selected_gamemode.lower() in GAMEMODES:
                                game_countries = countries.load_countries(db_flags, selected_gamemode.lower())
                                game_flags_images = countries.load_flags_images(game_countries,g.getFlagSize())
                            else:
                                print("!!! Gamemode not valid !!! Quitting")
                                sys.exit()
                            current_country = random.choice(list
                                                        (game_countries
                                                        .keys()))
                            countries_list, wrong_countries = [], []
                            countries_list.append(current_country)
                            print(f"CURRENT GAME SEQUENCE: {current_country}", end=", ", flush=True)
                            
                        except Exception as e:
                            print("Error while choosing gamemode:\n", e)
                            sys.exit()
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
                        top_scores = db.get_top_scores(db_scores, "global", limit=10)
                        g.showRankingsFromMenu(top_scores, "global")
                        setGameLoop(False, True, False, False, True,False)
                    if g.rank_mode_europe_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        top_scores = db.get_top_scores(db_scores, "europe", limit=10)
                        g.showRankings(top_scores, "europe")
                        setGameLoop(False, True, False, False, True,False)

                    if g.rank_mode_america_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        top_scores = db.get_top_scores(db_scores, "america", limit=10)
                        g.showRankingsFromMenu(top_scores, "america")
                        setGameLoop(False, True, False, False, True,False)

                    if g.rank_mode_asia_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        top_scores = db.get_top_scores(db_scores, "asia", limit=10)
                        g.showRankingsFromMenu(top_scores, "asia")
                        setGameLoop(False, True, False, False, True,False)

                    if g.rank_mode_oceania_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        top_scores = db.get_top_scores(db_scores, "oceania", limit=10)
                        g.showRankingsFromMenu(top_scores, "oceania")
                        setGameLoop(False, True, False, False, True,False)

                    if g.rank_mode_africa_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        top_scores = db.get_top_scores(db_scores, "africa", limit=10)
                        g.showRankingsFromMenu(top_scores, "africa")
                        setGameLoop(False, True, False, False, True,False)

                    if g.rank_mode_main_menu_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        setGameLoop(True, True, False, False, False, False)
                    while game_mode_selection:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                setGameLoop(False, False, False, False, False, False)
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                g.set_mouse_x_y(pygame.mouse.get_pos())
                               
    if game:
        g.showGame(current_country, 
                                    score, 
                                    game_flags_images,
                                    lives)
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
                        current_country = random.choice(list(game_countries.keys()))
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
                            db.insert_score(db_scores, score, countries_list, wrong_countries, selected_gamemode)  # Save the score to the database
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
        top_scores = db.get_top_scores(db_scores, selected_gamemode, limit=10)
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


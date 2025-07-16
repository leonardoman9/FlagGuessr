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
wrong_countries = []

# Initialize audio mixer
if not audio.init_mixer():
    print("Warning: Audio mixer failed to initialize. Music will not work.")

# Game loop
running = True
splash_screen = True
game = False
game_over = False
show_rankings = False

mode_selection = False  # New state for selecting game mode (Normal/Endless/Blitz)
came_from_game_over = False  # Track where we came from to rankings

# Game mode variables
selected_game_mode = "normal"  # normal, endless, blitz
selected_map = "europe"  # default map selection

# Game mode specific tracking
flags_shown_count = 0  # for endless mode
game_start_time = 0  # for blitz mode
blitz_time_limit = 60  # 60 seconds for blitz mode

# Start with random music
audio.playMusic(random_song=True)

# load the gui and countries classes
g = gui() 
countries = countries()

def setGameLoop(set_splash_screen, set_running, 
                set_game, set_gameover, 
                set_show_rankings, set_mode_selection=False):
    global splash_screen, running, game, game_over, show_rankings, mode_selection
    splash_screen = set_splash_screen
    running = set_running
    game = set_game
    game_over = set_gameover
    show_rankings = set_show_rankings
    mode_selection = set_mode_selection


while running:
    if splash_screen and not show_rankings:
        g.showSplashScreen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    g.set_mouse_x_y(mouse_pos)
                    
                    # Handle music controls first
                    if g.handle_music_controls_click(mouse_pos):
                        continue  # Skip other button checks if music control was clicked
                    

                    
                    if g.play_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        # Go to mode selection screen instead of starting game directly
                        setGameLoop(False, True, False, False, False, True)
                    if g.splash_rankings_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        came_from_game_over = False  # Coming from main menu
                        setGameLoop(False, True, False, False, True, False)
                    if g.splash_quit_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        setGameLoop(False, False, False, False, False)

    if splash_screen and show_rankings:
        pass

    if mode_selection:
        g.showModeSelection(GAMEMODES)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                setGameLoop(False, False, False, False, False, False, False)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                g.set_mouse_x_y(mouse_pos)
                
                # Handle mode selection clicks
                mode_result = g.handle_mode_selection_click(mouse_pos)
                if mode_result:
                    if mode_result == "back":
                        # Go back to main menu
                        setGameLoop(True, True, False, False, False, False)
                    else:
                        # Start game with selected mode and map
                        selected_game_mode, selected_map = mode_result
                        print(f"Selected mode: {selected_game_mode}, map: {selected_map}")
                        
                        # Initialize game with selected parameters
                        score = INITSCORE
                        lives = MAXLIVES
                        wrong_countries = []
                        flags_shown_count = 0  # Reset flag counter
                        g.set_input_text("")
                        g.clear_error_message()
                        
                        # Set game start time for blitz mode
                        if selected_game_mode == "blitz":
                            game_start_time = pygame.time.get_ticks()
                        
                        try:
                            # Load countries from the database
                            if selected_map.lower() in GAMEMODES:
                                game_countries = countries.load_countries(db_flags, selected_map.lower())
                                game_flags_images = countries.load_flags_images(game_countries, g.getFlagSize())
                            else:
                                print("!!! Map not valid !!! Quitting")
                                sys.exit()
                            
                            current_country = random.choice(list(game_countries.keys()))
                            
                            # Initialize countries_list based on game mode
                            if selected_game_mode == "normal":
                                # For normal mode, track all countries to complete
                                countries_list = []
                                countries_list.append(current_country)
                            else:
                                # For endless/blitz, just track shown flags for stats
                                countries_list = []  # Keep for compatibility, but don't use for completion
                                countries_list.append(current_country)
                                flags_shown_count = 1  # Start counting
                            
                            print(f"CURRENT GAME SEQUENCE ({selected_game_mode.upper()}): {current_country}", end=", ", flush=True)
                            
                        except Exception as e:
                            print("Error while choosing gamemode:\n", e)
                            sys.exit()
                        
                        # Start the game
                        setGameLoop(False, True, True, False, False, False)


    if game:
        # Check blitz mode timer outside of input events
        if selected_game_mode == "blitz" and game_start_time > 0:
            elapsed_time = (pygame.time.get_ticks() - game_start_time) / 1000
            if elapsed_time >= blitz_time_limit:
                # Time's up! End game automatically
                print(f"\nTIME'S UP! Final score: {score}")
                mode_data = {"time_taken": blitz_time_limit}
                db.insert_score(db_scores, score, countries_list, wrong_countries, 
                               selected_map, selected_game_mode, blitz_time_limit, flags_shown_count, mode_data)
                print(f"\nGame mode: {selected_game_mode}, Flags shown: {flags_shown_count}")
                game_over = True
                game = False
        
        g.showGame(current_country, 
                                    score, 
                                    game_flags_images,
                                    lives,
                                    selected_game_mode,
                                    game_start_time,
                                    blitz_time_limit,
                                    flags_shown_count)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                g.set_mouse_x_y(mouse_pos)
                
                # Handle EXIT button click
                if g.get_game_exit_button_rect().collidepoint(mouse_pos):
                    # Return to main menu
                    setGameLoop(True, True, False, False, False)
                    continue
                
                # Handle music controls during game
                g.handle_game_music_click(mouse_pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_RETURN:
                    # Check for blitz mode timeout
                    if selected_game_mode == "blitz":
                        elapsed_time = (pygame.time.get_ticks() - game_start_time) / 1000
                        if elapsed_time >= blitz_time_limit:
                            # Time's up! End game
                            print(f"\nTIME'S UP! Final score: {score}")
                            selected_gamemode = selected_map
                            mode_data = {"time_taken": blitz_time_limit}
                            db.insert_score(db_scores, score, countries_list, wrong_countries, 
                                           selected_map, selected_game_mode, blitz_time_limit, flags_shown_count, mode_data)
                            print(f"\nGame mode: {selected_game_mode}, Flags shown: {flags_shown_count}")
                            game_over = True
                            game = False
                            continue
                    
                    # Check the user's input
                    if g.get_input_text().lower() == current_country.lower():
                        # Correct guess
                        score += 1
                        g.clear_error_message()  # Clear any error message
                        
                        # Choose next country based on game mode
                        if selected_game_mode == "normal":
                            # Normal mode: remove from available countries (no repeats)
                            available_countries = [c for c in game_countries.keys() if c not in countries_list]
                            if available_countries:
                                current_country = random.choice(available_countries)
                                countries_list.append(current_country)
                            else:
                                # Completed all countries! Victory!
                                print(f"\nCOMPLETED! All {len(countries_list)} countries guessed!")
                                selected_gamemode = selected_map
                                mode_data = {"completion": True}
                                db.insert_score(db_scores, score, countries_list, wrong_countries, 
                                               selected_map, selected_game_mode, 0, len(countries_list), mode_data)
                                print(f"\nGame mode: {selected_game_mode}")
                                game_over = True
                                game = False
                                continue
                        else:
                            # Endless/Blitz mode: infinite random selection
                            current_country = random.choice(list(game_countries.keys()))
                            countries_list.append(current_country)
                            flags_shown_count += 1
                        
                        print(current_country, end=", ", flush=True)
                        g.set_input_text("")
                    else:
                        # Incorrect guess - immediately continue to next country with error message
                        lives -= 1
                        wrong_countries.append(current_country)
                        user_answer = g.get_input_text()
                        print(f"<-WRONG! It was {current_country}", end=", ", flush=True)
                        
                        # Show error message overlay for next country
                        g.show_error_message(f"Wrong! It was: {current_country}")
                        
                        # Check if game over
                        if lives <= 0:
                            selected_gamemode = selected_map
                            # Calculate mode-specific data
                            mode_data = {}
                            time_taken = 0
                            
                            if selected_game_mode == "endless":
                                mode_data["flags_shown"] = flags_shown_count
                            elif selected_game_mode == "blitz":
                                time_taken = int((pygame.time.get_ticks() - game_start_time) / 1000)
                                mode_data["time_taken"] = time_taken
                            
                            db.insert_score(db_scores, score, countries_list, wrong_countries, 
                                           selected_map, selected_game_mode, time_taken, flags_shown_count, mode_data)
                            print(f"\n\nFull game: {countries_list}")
                            print(f"\nMistaken countries: {wrong_countries}")
                            print(f"\nGame mode: {selected_game_mode}")
                            if selected_game_mode == "endless":
                                print(f"Flags shown: {flags_shown_count}")
                            elif selected_game_mode == "blitz":
                                print(f"Time taken: {time_taken}s")
                            game_over = True
                            game = False
                        else:
                            # Continue to next country immediately
                            if selected_game_mode == "normal":
                                # Normal mode: choose from remaining countries
                                available_countries = [c for c in game_countries.keys() if c not in countries_list]
                                if available_countries:
                                    current_country = random.choice(available_countries)
                                    countries_list.append(current_country)
                                else:
                                    # This shouldn't happen, but fallback to any country
                                    current_country = random.choice(list(game_countries.keys()))
                                    countries_list.append(current_country)
                            else:
                                # Endless/Blitz mode: infinite random
                                current_country = random.choice(list(game_countries.keys()))
                                countries_list.append(current_country)
                                flags_shown_count += 1
                            
                            print(current_country, end=", ", flush=True)
                        
                        g.set_input_text("")  # Clear input for next round

                elif event.key == pygame.K_BACKSPACE:
                    g.set_input_text(g.get_input_text()[:-1])
                else:
                    g.set_input_text(g.get_input_text() + event.unicode)

    if game_over:
        # Display game over screen with Quit and Rankings buttons 
        selected_gamemode = g.get_selected_gamemode()
        g.showGameOver(score,wrong_countries,selected_gamemode)
        #Events Handling
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    setGameLoop(False, False, False, False, False, False)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.set_mouse_x_y(pygame.mouse.get_pos())
                    if g.get_quit_button_rect().collidepoint(g.get_x_y()):
                        setGameLoop(False, False, False, False, False)
                    elif g.get_rankings_button_rect().collidepoint(g.get_x_y()):
                        came_from_game_over = True  # Coming from game over
                        setGameLoop(False, True, False, False, True)
                    elif g.main_menu_button_rect.collidepoint(g.get_x_y()):
                        setGameLoop(True, True, False, False, False)

    if show_rankings:
        # Display rankings
        rankings_gamemode = g.get_rankings_gamemode()
        # Use the selected filter for database query
        rankings_filter = g.selected_rankings_filter
        top_scores = db.get_top_scores(db_scores, rankings_gamemode, rankings_filter, limit=10)
        # Handle case when db.get_top_scores returns None due to error
        if top_scores is None:
            top_scores = []
        g.showRankings(top_scores, rankings_gamemode)
        #Events handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                setGameLoop(False, False, False, False, False)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                g.set_mouse_x_y(mouse_pos)
                
                # Handle filter tab clicks
                if g.handle_ranking_filter_click(mouse_pos):
                    # The filter has been updated, rankings will refresh on next frame
                    continue  # Skip other button checks
                
                if g.rankings_back_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                    if came_from_game_over:
                        # Return to game over screen
                        setGameLoop(False, True, False, True, False)
                    else:
                        # Return to main menu (no more mode selection screen from rankings)
                        setGameLoop(True, True, False, False, False)
                if g.rank_sel_main_menu_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                    setGameLoop(True, True, False, False, False)


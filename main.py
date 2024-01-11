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
# Load and play a random song from the "data" folder

#Game constants
MAXLIVES = 3
INITSCORE = 0
MUSIC = False

#Start music
audio.playMusic(MUSIC)

# Game variables
gamemode = "oceania"
game_countries = countries.countries(gamemode)
current_country = random.choice(list
                                (game_countries
                                 .getResult()
                                 .keys()))
countries_list, wrong_countries = [], []
countries_list.append(current_country)
score = INITSCORE
lives = MAXLIVES

g = gui.gui(game_countries)
print(f"CURRENT GAME SEQUENCE: {current_country}", end=", ", flush=True)

# Game loop
running = True
game_over = False
show_rankings = False

while running:
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
                        db.insert_score(db_filename, score, countries_list, wrong_countries, gamemode)  # Save the score to the database
                        print(f"\n\nFull game: {countries_list}")
                        print(f"\nMistaken countries: {wrong_countries}")
                        game_over = True

            elif event.key == pygame.K_BACKSPACE:
                g.set_input_text(g.get_input_text()[:-1])
            else:
                g.set_input_text(g.get_input_text() + event.unicode)

    # Display the current flag
    scripts.showFlag(g.getScreen(), 
                     g.getFlags(), 
                     current_country, 
                     g.get_width(), g.get_height(),
                     g.getFlagSize())
    # Display score and lives with increased vertical separation
    score_text = g.getFont().render(f"Score: {score}", True, (255, 255, 255))  # White color for score
    lives_text = g.getFont().render(f"Lives: {lives}", True, (255, 255, 255))
    g.getScreen().blit(score_text, (10, 10))
    g.getScreen().blit(lives_text, (g.get_width() - 120, 10 + g.get_text_vertical_spacing()))

    # Draw the input box
    pygame.draw.rect(g.getScreen(), g.get_input_color(), g.get_input_rect(), 2)
    pygame.draw.rect(g.getScreen(), (0, 0, 0), g.get_input_border(), 2)  # Black color for input box border
    text_surface = g.getFont().render(g.get_input_text(), True, (255, 255, 255), (0, 0, 0))  # White color for text, black background
    input_box_width = max(200, text_surface.get_width() + 10)
    g.get_input_rect().w = input_box_width
    g.getScreen().blit(text_surface, (g.get_input_rect().x + 5, g.get_input_rect().y + 5))
    pygame.display.flip()

    if game_over:
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    wait = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.set_mouse_x_y(pygame.mouse.get_pos())
                    if g.get_quit_button_rect().collidepoint(g.get_x_y()):
                        running = False
                        wait = False
                    elif g.get_rankings_button_rect().collidepoint(g.get_x_y()):
                        show_rankings = True
                        wait = False
            # Display game over screen with Quit and Rankings buttons 
            g.showGameOver(score,wrong_countries,gamemode)
            

    # Display rankings screen
    if show_rankings:
        while show_rankings:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    show_rankings = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.set_mouse_x_y(pygame.mouse.get_pos())
                    quit_button_rect = pygame.Rect(g.get_width() // 2 - 100, g.get_height() // 2 + 50, 100, 50)
                    back_button_rect = pygame.Rect(g.get_width() // 2 - 70, g.get_height() - 50, 140, 50)

                    if quit_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        show_rankings = False
                    elif back_button_rect.collidepoint(g.get_mouse_x(), g.get_mouse_y()):
                        show_rankings = False

            # Display rankings
            g.showRankings(db_filename, gamemode)

# Quit Pygame
pygame.quit()
sys.exit()

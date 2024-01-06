import pygame
import random
import sys
import os
import sqlite3
from datetime import datetime
from countries import countries

# Initialize Pygame
icon = pygame.image.load("data/icon.ico")
pygame.display.set_icon(icon)
pygame.init()
# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("FlagGuessr")
# Load and resize flag images
flag_size = (300, 200)
flags = {country: pygame.transform.scale(pygame.image.load(os.path.join("data/flags", filename)), flag_size) for country, filename in countries.items()}

# Font setup    
font = pygame.font.Font(None, 36)

# Database setup
db_filename = "scores.db"

def create_scores_table():
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       score INTEGER,
                       timestamp TEXT)''')
    connection.commit()
    connection.close()

def insert_score(score):
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO scores (score, timestamp) VALUES (?, ?)", (score, timestamp))
    connection.commit()
    connection.close()

def get_top_scores(limit=10):
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    cursor.execute("SELECT score, timestamp FROM scores ORDER BY score DESC LIMIT ?", (limit,))
    top_scores = cursor.fetchall()
    connection.close()
    return top_scores

# Ensure the 'scores' table is created
create_scores_table()

# Load and play a random song from the "data" folder
song_files = [f for f in os.listdir("data/music") if f.endswith(".mp3")]
if song_files:
    random_song = os.path.join("data/music", random.choice(song_files))
    pygame.mixer.music.load(random_song)
    pygame.mixer.music.play(-1)  # -1 makes the music loop indefinitely


# Game variables
current_country = random.choice(list(countries.keys()))
score = 0
lives = 3

# Text input variables
input_text = ""
input_rect = pygame.Rect(250, height - 50, 200, 32)
input_color = pygame.Color('dodgerblue2')
input_active = False

# Vertical separation between text elements
text_vertical_spacing = 20

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
                if input_text.lower() == current_country.lower():
                    # Correct guess
                    score += 1
                    current_country = random.choice(list(countries.keys()))
                    print(current_country)
                    input_text = ""
                else:
                    # Incorrect guess
                    lives -= 1
                    if lives == 0:
                        # Game over if no lives left
                        insert_score(score)  # Save the score to the database
                        game_over = True

            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]

            else:
                input_text += event.unicode

    # Display the current flag
    screen.fill((128, 128, 128))  # Set background color to white
    screen.blit(flags[current_country], (width // 2 - flag_size[0] // 2, height // 2 - flag_size[1] // 2))

    # Display score and lives with increased vertical separation
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    lives_text = font.render(f"Lives: {lives}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (width - 120, 10 + text_vertical_spacing))

    # Draw the input box
    pygame.draw.rect(screen, input_color, input_rect, 2)
    text_surface = font.render(input_text, True, (0, 0, 0))
    input_box_width = max(200, text_surface.get_width() + 10)
    input_rect.w = input_box_width
    screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

    pygame.display.flip()

    if game_over:
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    wait = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    quit_button_rect = pygame.Rect(width // 2 - 100, height // 2 + 50, 100, 50)
                    rankings_button_rect = pygame.Rect(width // 2 + 20, height // 2 + 50, 140, 50)

                    if quit_button_rect.collidepoint(mouse_x, mouse_y):
                        running = False
                        wait = False
                    elif rankings_button_rect.collidepoint(mouse_x, mouse_y):
                        show_rankings = True
                        wait = False

            # Display game over screen with Quit and Rankings buttons
            screen.fill((255, 255, 255))
            game_over_text = font.render(f"Game Over - Score: {score}", True, (255, 0, 0))
            screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - game_over_text.get_height() // 2))

            quit_button_rect = pygame.Rect(width // 2 - 100, height // 2 + 50, 100, 50)
            pygame.draw.rect(screen, (0, 255, 0), quit_button_rect)
            quit_text = font.render("Quit", True, (255, 255, 255))
            screen.blit(quit_text, (quit_button_rect.centerx - quit_text.get_width() // 2, quit_button_rect.centery - quit_text.get_height() // 2))

            rankings_button_rect = pygame.Rect(width // 2 + 20, height // 2 + 50, 140, 50)
            pygame.draw.rect(screen, (0, 0, 255), rankings_button_rect)
            rankings_text = font.render("See Rankings", True, (255, 255, 255))
            screen.blit(rankings_text, (rankings_button_rect.centerx - rankings_text.get_width() // 2, rankings_button_rect.centery - rankings_text.get_height() // 2))

            pygame.display.flip()

            pygame.time.delay(50)  # Add a delay to avoid flickering

    # Display rankings screen
    if show_rankings:
        while show_rankings:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    show_rankings = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    quit_button_rect = pygame.Rect(width // 2 - 100, height // 2 + 50, 100, 50)
                    back_button_rect = pygame.Rect(width // 2 - 70, height - 50, 140, 50)

                    if quit_button_rect.collidepoint(mouse_x, mouse_y):
                        show_rankings = False
                    elif back_button_rect.collidepoint(mouse_x, mouse_y):
                        show_rankings = False

            # Display rankings
            screen.fill((255, 255, 255))
            rankings_text = font.render("Top 10 Rankings:", True, (0, 0, 0))
            screen.blit(rankings_text, (width // 2 - rankings_text.get_width() // 2, 50))

            # Fetch and display top 10 rankings from the database (ordered by score)
            top_scores = get_top_scores(limit=10)

            for i, (rank, timestamp) in enumerate(top_scores):
                rank_text = font.render(f"{i + 1}. Score: {rank} - {timestamp}", True, (0, 0, 0))
                screen.blit(rank_text, (width // 2 - rank_text.get_width() // 2, 100 + i * 30))

            back_button_rect = pygame.Rect(width // 2 - 70, height - 50, 140, 50)
            pygame.draw.rect(screen, (255, 0, 0), back_button_rect)
            back_text = font.render("Back", True, (255, 255, 255))
            screen.blit(back_text, (back_button_rect.centerx - back_text.get_width() // 2, back_button_rect.centery - back_text.get_height() // 2))

            pygame.display.flip()

            pygame.time.delay(50)  # Add a delay to avoid flickering

# Quit Pygame
pygame.quit()
sys.exit()

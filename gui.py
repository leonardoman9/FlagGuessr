import pygame
import os
from countries import countries
import db

class gui:
    def __init__(self, game_countries):
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.flag_size = (500, 400)
        self.flags = self.load_flags(game_countries)
        self.font = pygame.font.Font("./data/fonts/americancaptain.ttf", 30)
        # Vertical separation between text elements
        self.text_vertical_spacing = 20
        # Text input variables
        self.input_text = ""
        self.input_border = pygame.Rect(252, self.height - 48, 196, 28)
        self.input_rect = pygame.Rect(250, self.height - 50, 200, 32)
        self.input_color = pygame.Color('#FFD700')  # Gold color for input box
        self.input_active = False
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        self.quit_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 + 50, 100, 50)
        self.rankings_button_rect = pygame.Rect(self.width // 2 + 20, self.height // 2 + 50, 140, 50)

    def load_flags(self, game_countries):
        result = game_countries.getResult()
        flags = {}
        with game_countries.connect_db() as conn:
            cursor = conn.cursor()
            for country, continent in result.items():
                flag_path = os.path.join("data/flags", continent, f"{country}.png")
                flags[country] = pygame.transform.scale(pygame.image.load(flag_path), self.flag_size)

        return flags
    def showSplashScreen(self):
        self.screen.fill((0, 0, 0))  # Black background

        play_button_rect = pygame.Rect(self.width // 2 - 50, self.height // 2 - 50, 100, 50)
        rankings_button_rect = pygame.Rect(self.width // 2 - 50, self.height // 2 + 20, 100, 50)
        quit_button_rect = pygame.Rect(self.width // 2 - 50, self.height // 2 + 90, 100, 50)
        mute_button_rect = pygame.Rect(self.width - 70, 20, 50, 50)  # Adjust the position as needed

        # Draw buttons
        pygame.draw.rect(self.screen, (0, 255, 0), play_button_rect)
        play_text = self.font.render("Play", True, (0, 0, 0))
        self.screen.blit(play_text, (play_button_rect.centerx - play_text.get_width() // 2, play_button_rect.centery - play_text.get_height() // 2))

        pygame.draw.rect(self.screen, (0, 0, 255), rankings_button_rect)
        rankings_text = self.font.render("Rankings", True, (0, 0, 0))
        self.screen.blit(rankings_text, (rankings_button_rect.centerx - rankings_text.get_width() // 2, rankings_button_rect.centery - rankings_text.get_height() // 2))

        pygame.draw.rect(self.screen, (255, 0, 0), quit_button_rect)
        quit_text = self.font.render("Quit", True, (0, 0, 0))
        self.screen.blit(quit_text, (quit_button_rect.centerx - quit_text.get_width() // 2, quit_button_rect.centery - quit_text.get_height() // 2))

        pygame.draw.rect(self.screen, (255, 255, 0), mute_button_rect)
        mute_text = self.font.render("Mute", True, (0, 0, 0))
        self.screen.blit(mute_text, (mute_button_rect.centerx - mute_text.get_width() // 2, mute_button_rect.centery - mute_text.get_height() // 2))

        pygame.display.flip()
    def showGameOver(self, score, wrong_countries,gamemode):
        self.screen.fill((0, 0, 0))  # Black background
        game_over_text = self.font.render(f"Game Over - Score: {score}", True, (255, 0, 0))
        mistakes_text = self.font.render(f"Mistakes: {', '.join(wrong_countries)}", True, (255, 0, 0))

        self.screen.blit(game_over_text, (self.width // 2 - game_over_text.get_width() // 2, self.height // 2 - game_over_text.get_height() // 2))

        pygame.draw.rect(self.screen, (0, 255, 0), self.quit_button_rect)
        quit_text = self.font.render("Quit", True, (0, 0, 0))
        self.screen.blit(quit_text, (self.quit_button_rect.centerx - quit_text.get_width() // 2, self.quit_button_rect.centery - quit_text.get_height() // 2))

        pygame.draw.rect(self.screen, (0, 0, 255), self.rankings_button_rect)  # Corrected this line
        rankings_text = self.font.render("See Rankings", True, (0, 0, 0))
        self.screen.blit(rankings_text, (self.rankings_button_rect.centerx - rankings_text.get_width() // 2, self.rankings_button_rect.centery - rankings_text.get_height() // 2))

        pygame.display.flip()

        pygame.time.delay(50)  # Add a delay to avoid flickering
    def showRankings(self,db_filename, gamemode):
        self.screen.fill((0, 0, 0))  # Black background
        rankings_text = self.font.render(f"Top 10 Rankings for gamemode {gamemode}:", True, (255, 255, 255))  # White color for rankings text
        self.screen.blit(rankings_text, (self.width // 2 - rankings_text.get_width() // 2, 50))

        # Fetch and display top 10 rankings from the database (ordered by score)
        top_scores = db.get_top_scores(db_filename, gamemode,limit=10)

        for i, (rank, timestamp, gamemode, game_sequence, mistakes,) in enumerate(top_scores):
            rank_text = self.font.render(f"{i + 1}. Score: {rank} - {timestamp} - {mistakes}", True, (255, 255, 255))
            self.screen.blit(rank_text, (self.width // 2 - rank_text.get_width() // 2, 100 + i * 30))

        back_button_rect = pygame.Rect(self.width // 2 - 70, self.height - 50, 140, 50)
        pygame.draw.rect(self.screen, (255, 0, 0), back_button_rect)
        back_text = self.font.render("Back", True, (0, 0, 0))
        self.screen.blit(back_text, (back_button_rect.centerx - back_text.get_width() // 2, back_button_rect.centery - back_text.get_height() // 2))

        pygame.display.flip()

        pygame.time.delay(50)  # Add a delay to avoid flickering
    def getWidthHeight(self):
        return self.width, self.height
    def getScreen(self):
        return self.screen
    def get_height(self):
        return self.height
    def get_width(self):
        return self.width
    def getFlags(self):
        return self.flags
    def getFlagSize(self):
        return self.flag_size
    def getFont(self):
        return self.font
    def get_text_vertical_spacing(self):
        return self.text_vertical_spacing
    def get_input_text(self):
        return self.input_text
    def get_input_border(self):
        return self.input_border 
    def get_input_rect(self):
        return self.input_rect 
    def get_input_color(self):
        return self.input_color 
    def get_input_active(self):
        return self.input_active 
    def get_input_text(self):
        return self.input_text
    def get_input_borde(self):
        return self.input_border 
    def get_input_rect(self):    
        return self.input_rect 
    def get_input_color(self):    
        return self.input_color 
    def get_input_active(self):    
        return self.input_active
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
        return self.mouse_x, self.mouse_y  # Add this line
    def get_quit_button_rect(self):
        return self.quit_button_rect
    def get_rankings_button_rect(self):    
        return self.rankings_button_rect
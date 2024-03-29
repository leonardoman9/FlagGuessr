import pygame
import os
from countries import countries
import db
import scripts

class gui:
    def __init__(self):
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.flag_size = (500, 400)
        #self.flags = self.load_flags(game_countries)
        self.font = pygame.font.Font("./data/fonts/americancaptain.ttf", 30)
        # Vertical separation between text elements
        self.text_vertical_spacing = 20
        
        #Splash Screen
        self.play_button_rect = pygame.Rect(self.width // 2 - 50, self.height // 2 - 50, 100, 50)
        self.splash_rankings_button_rect = pygame.Rect(self.width // 2 - 50, self.height // 2 + 20, 100, 50)
        self.splash_quit_button_rect = pygame.Rect(self.width // 2 - 50, self.height // 2 + 90, 100, 50)
        self.mute_button_rect = pygame.Rect(self.width - 70, 20, 50, 50)  # Adjust the position as needed

        
        # Text input variables
        self.input_text = ""
        self.input_border = pygame.Rect(252, self.height - 48, 196, 28)
        self.input_rect = pygame.Rect(250, self.height - 50, 200, 32)
        self.input_color = pygame.Color('#FFD700')  # Gold color for input box
        self.input_active = False
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        self.quit_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 + 50, 100, 50)
        self.rankings_button_rect = pygame.Rect(self.width // 2 + 20, self.height // 2 + 50, 140, 50)
        self.rankings_back_button_rect = pygame.Rect(self.width // 2 - 70, self.height - 50, 140, 50)
        self.rankings_back_text = self.font.render("Back", True, (0, 0, 0))
        self.main_menu_button_rect = pygame.Rect(self.width // 2 - 70, self.height // 2 + 110, 140, 50)

        #game mode selection screen# Draw buttons for different game modes
        button_width, button_height = 140, 50
        button_padding_x, button_padding_y = 20, 20
        self.rank_mode_global_button_rect = pygame.Rect(self.width // 2 - (button_width + button_padding_x), self.height // 2 - (button_height + button_padding_y), button_width, button_height)
        self.rank_mode_europe_button_rect = pygame.Rect(self.width // 2, self.height // 2 - (button_height + button_padding_y), button_width, button_height)
        self.rank_mode_america_button_rect = pygame.Rect(self.width // 2 - (button_width + button_padding_x), self.height // 2, button_width, button_height)
        self.rank_mode_asia_button_rect = pygame.Rect(self.width // 2, self.height // 2, button_width, button_height)
        self.rank_mode_oceania_button_rect = pygame.Rect(self.width // 2 - (button_width + button_padding_x), self.height // 2 + (button_height + button_padding_y), button_width, button_height)
        self.rank_mode_africa_button_rect = pygame.Rect(self.width // 2, self.height // 2 + (button_height + button_padding_y), button_width, button_height)
        self.rank_mode_main_menu_button_rect = pygame.Rect(self.width // 2 - 70, self.height - 100, 140, 50)
        self.rank_sel_main_menu_button_rect = pygame.Rect(self.width // 2 - 70, self.height - 100, 140, 50)
        self.rank_sel_main_menu_text = self.font.render("Main Menu", True, (255, 0, 0))
        self.dropdown_rect = pygame.Rect(self.play_button_rect.x + self.play_button_rect.width, self.play_button_rect.y,
                                        self.play_button_rect.width, 30)

   
    def showGame(self, current_country, score, game_flags_images, lives):
        # Display the current flag
        self.screen.fill((0, 0, 0))  # Set background color to black
        # Ensure the flag size is applied correctly
        flag_image = game_flags_images[current_country]
        flag_rect = flag_image.get_rect()
        flag_rect.center = (self.width // 2, self.height // 2)
        self.screen.blit(flag_image, flag_rect.topleft)

        # Display score and lives with increased vertical separation
        score_text = self.font.render(f"Score: {score}", True, (255, 255, 255))  # White color for score
        lives_text = self.font.render(f"Lives: {lives}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (self.width - 120, 10 + self.text_vertical_spacing))

        # Draw the input box
        pygame.draw.rect(self.screen, self.input_color, self.input_rect, 2)
        pygame.draw.rect(self.screen, (0, 0, 0), self.input_border, 2)  # Black color for input box border
        text_surface = self.font.render(self.input_text, True, (255, 255, 255), (0, 0, 0))  # White color for text, black background
        input_box_width = max(200, text_surface.get_width() + 10)
        self.input_rect.w = input_box_width
        self.screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        pygame.display.flip()

    def draw_dropdown(self, rect, color, text, dropdown_rect, gamemodes):
        # Draw dropdown menu function
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.polygon(self.screen, color, [(rect.x + rect.width - 20, rect.centery - 5),
                                                 (rect.x + rect.width - 10, rect.centery),
                                                 (rect.x + rect.width - 20, rect.centery + 5)])

        text_surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, (rect.x + 10, rect.centery - text_surface.get_height() // 2))

        pygame.draw.rect(self.screen, color, dropdown_rect)
    def draw_button(self, rect, color, text):
        pygame.draw.rect(self.screen, color, rect)
        text_surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, (rect.centerx - text_surface.get_width() // 2, rect.centery - text_surface.get_height() // 2))

    def showSplashScreen(self, gamemodes):
        self.screen.fill((0, 0, 0))  # Black background

        # Draw buttons
        self.draw_button(self.play_button_rect, (0, 255, 0), "Play")
        self.draw_button(self.splash_rankings_button_rect, (0, 0, 255), "Rankings")
        self.draw_button(self.splash_quit_button_rect, (255, 0, 0), "Quit")
        self.draw_button(self.mute_button_rect, (255, 255, 0), "Mute")

         # Draw dropdown menu for choosing game mode
        dropdown_y = self.height // 2 + 20
        dropdown_rect = pygame.Rect(self.play_button_rect.x, dropdown_y,
                                    self.play_button_rect.width, 30)
        self.draw_dropdown(dropdown_rect, (150, 150, 150), "Game Mode", dropdown_rect, gamemodes)

        pygame.display.flip()
   
    def showGameOver(self, score, wrong_countries, gamemode):
        self.screen.fill((0, 0, 0))  # Black background
        # Game over text
        game_over_text = self.font.render(f"Game Over - Score: {score}", True, (255, 0, 0))
        game_over_text_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - game_over_text.get_height()))
        self.screen.blit(game_over_text, game_over_text_rect)
        # Mistakes text
        mistakes_text = self.font.render(f"Mistakes: {', '.join(wrong_countries)}", True, (255, 0, 0))
        mistakes_text_rect = mistakes_text.get_rect(center=(self.width // 2, self.height // 2 + mistakes_text.get_height()))
        self.screen.blit(mistakes_text, mistakes_text_rect)
        pygame.display.flip()
        #quit
        pygame.draw.rect(self.screen, (0, 255, 0), self.quit_button_rect)
        quit_text = self.font.render("Quit", True, (0, 0, 0))
        self.screen.blit(quit_text, (self.quit_button_rect.centerx - quit_text.get_width() // 2, self.quit_button_rect.centery - quit_text.get_height() // 2))
        #see rankings
        pygame.draw.rect(self.screen, (0, 0, 255), self.rankings_button_rect)  # Corrected this line
        rankings_text = self.font.render("See Rankings", True, (0, 0, 0))
        self.screen.blit(rankings_text, (self.rankings_button_rect.centerx - rankings_text.get_width() // 2, self.rankings_button_rect.centery - rankings_text.get_height() // 2))
        #main menu
        pygame.draw.rect(self.screen, (255, 0, 0), self.main_menu_button_rect)
        main_menu_text = self.font.render("Main Menu", True, (0, 0, 0))
        self.screen.blit(main_menu_text, (self.main_menu_button_rect.centerx - main_menu_text.get_width() // 2, self.main_menu_button_rect.centery - main_menu_text.get_height() // 2))

        pygame.display.flip()

        pygame.time.delay(50)  # Add a delay to avoid flickering
    def showModeSelectionScreen(self):
        self.screen.fill((0, 0, 0))  # Black background

        # Draw borders for the buttons
        pygame.draw.rect(self.screen, (255, 255, 255), self.rank_mode_global_button_rect, 2)
        pygame.draw.rect(self.screen, (255, 255, 255), self.rank_mode_europe_button_rect, 2)
        pygame.draw.rect(self.screen, (255, 255, 255), self.rank_mode_america_button_rect, 2)
        pygame.draw.rect(self.screen, (255, 255, 255), self.rank_mode_asia_button_rect, 2)
        pygame.draw.rect(self.screen, (255, 255, 255), self.rank_mode_oceania_button_rect, 2)
        pygame.draw.rect(self.screen, (255, 255, 255), self.rank_mode_africa_button_rect, 2)

        # Draw text on the buttons
        global_text = self.font.render("Global", True, (255, 255, 255))
        europe_text = self.font.render("Europe", True, (255, 255, 255))
        america_text = self.font.render("America", True, (255, 255, 255))
        asia_text = self.font.render("Asia", True, (255, 255, 255))
        oceania_text = self.font.render("Oceania", True, (255, 255, 255))
        africa_text = self.font.render("Africa", True, (255, 255, 255))

        self.screen.blit(global_text, (
            self.rank_mode_global_button_rect.centerx - global_text.get_width() // 2,
            self.rank_mode_global_button_rect.centery - global_text.get_height() // 2
        ))
        self.screen.blit(europe_text, (
            self.rank_mode_europe_button_rect.centerx - europe_text.get_width() // 2,
            self.rank_mode_europe_button_rect.centery - europe_text.get_height() // 2
        ))
        self.screen.blit(america_text, (
            self.rank_mode_america_button_rect.centerx - america_text.get_width() // 2,
            self.rank_mode_america_button_rect.centery - america_text.get_height() // 2
        ))
        self.screen.blit(asia_text, (
            self.rank_mode_asia_button_rect.centerx - asia_text.get_width() // 2,
            self.rank_mode_asia_button_rect.centery - asia_text.get_height() // 2
        ))
        self.screen.blit(oceania_text, (
            self.rank_mode_oceania_button_rect.centerx - oceania_text.get_width() // 2,
            self.rank_mode_oceania_button_rect.centery - oceania_text.get_height() // 2
        ))
        self.screen.blit(africa_text, (
            self.rank_mode_africa_button_rect.centerx - africa_text.get_width() // 2,
            self.rank_mode_africa_button_rect.centery - africa_text.get_height() // 2
        ))

        # "Main Menu" button
        pygame.draw.rect(self.screen, (255, 0, 0), self.rank_mode_main_menu_button_rect, 2)  # Red border
        self.rank_mode_main_menu_text = self.font.render("Main Menu", True, (255, 0, 0))
        self.screen.blit(self.rank_mode_main_menu_text, (
            self.rank_mode_main_menu_button_rect.centerx - self.rank_mode_main_menu_text.get_width() // 2,
            self.rank_mode_main_menu_button_rect.centery - self.rank_mode_main_menu_text.get_height() // 2
        ))

        pygame.display.flip()
    def showRankings(self, scores, gamemode):
        self.screen.fill((0, 0, 0))  # Black background
        rankings_text = self.font.render(f"Top 10 Rankings - {gamemode}:", True, (255, 255, 255))  # White color for rankings text
        self.screen.blit(rankings_text, (self.width // 2 - rankings_text.get_width() // 2, 50))
        # Fetch and display top 10 rankings from the database (ordered by score)
        for i, (rank, timestamp, top_scores, game_sequence, mistakes,) in enumerate(scores):
            rank_text = self.font.render(f"{i + 1}. Score: {rank} - {timestamp} - {mistakes}", True, (255, 255, 255))
            self.screen.blit(rank_text, (self.width // 2 - rank_text.get_width() // 2, 100 + i * 30))
        pygame.draw.rect(self.screen, (255, 0, 0), self.rankings_back_button_rect)
        self.rankings_back_text = self.font.render("Back", True, (0, 0, 0))
        self.screen.blit(self.rankings_back_text, (self.rankings_back_button_rect.centerx - self.rankings_back_text.get_width() // 2, self.rankings_back_button_rect.centery - self.rankings_back_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.delay(50)  # Add a delay to avoid flickering
   
    def showRankingsFromMenu(self, scores, gamemode):
        self.screen.fill((0, 0, 0))  # Black background
        rankings_text = self.font.render(f"Top 10 Rankings - {gamemode}:", True, (255, 255, 255))  # White color for rankings text
        self.screen.blit(rankings_text, (self.width // 2 - rankings_text.get_width() // 2, 50))
        # Fetch and display top 10 rankings from the database (ordered by score)
        for i, (rank, timestamp, top_scores, game_sequence, mistakes,) in enumerate(scores):
            rank_text = self.font.render(f"{i + 1}. Score: {rank} - {timestamp} - {mistakes}", True, (255, 255, 255))
            self.screen.blit(rank_text, (self.width // 2 - rank_text.get_width() // 2, 100 + i * 30))
        pygame.draw.rect(self.screen, (255, 0, 0), self.rank_sel_main_menu_button_rect, 2)  # Red border
        self.screen.blit(self.rank_sel_main_menu_text, (
            self.rank_sel_main_menu_button_rect.centerx - self.rank_sel_main_menu_text.get_width() // 2,
            self.rank_sel_main_menu_button_rect.centery - self.rank_sel_main_menu_text.get_height() // 2
        ))

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
    
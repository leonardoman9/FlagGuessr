import pygame
import os
import math
from countries import countries
import db
import scripts

class gui:
    def __init__(self):
        
        # Modern 16:9 resolution
        self.width, self.height = 1280, 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Flag Guesser - Ultimate Edition")
        
        # Animation system for progressive disclosure
        self.animation_start_time = pygame.time.get_ticks()
        self.animations = {
            'splash_title': {'delay': 0, 'duration': 1000, 'completed': False},
            'splash_subtitle': {'delay': 300, 'duration': 800, 'completed': False},
            'splash_buttons': {'delay': 800, 'duration': 1200, 'completed': False},
            'splash_music': {'delay': 1200, 'duration': 800, 'completed': False},
            'game_flag': {'delay': 0, 'duration': 600, 'completed': False},
            'game_hud': {'delay': 200, 'duration': 400, 'completed': False},
            'game_input': {'delay': 400, 'duration': 400, 'completed': False},
        }
        
        # State management
        self.current_state = "splash"  # splash, game, rankings, settings
        self.previous_state = None
        self.transition_progress = 0.0
        self.is_transitioning = False
        
        # Loading states
        self.loading_states = {
            'database': False,
            'flags': False,
            'music': False
        }
        
        # Game feedback animations
        self.feedback_animations = {
            'correct': {'active': False, 'start_time': 0, 'duration': 1000},
            'incorrect': {'active': False, 'start_time': 0, 'duration': 1000},
            'score_change': {'active': False, 'start_time': 0, 'duration': 600}
        }
        
        # Wrong answer feedback
        self.wrong_answer_feedback = {
            'active': False,
            'start_time': 0,
            'duration': 2000,  # Show for 2 seconds
            'correct_country': '',
            'user_input': ''
        }
        
        # Simple error message overlay (non-blocking)
        self.error_message = {
            'active': False,
            'text': '',
            'start_time': 0,
            'duration': 3000  # Show for 3 seconds
        }
        
        # Design system - Color palette
        self.colors = {
            # Primary colors
            'primary': (64, 128, 255),        # Modern blue
            'primary_dark': (45, 90, 180),    # Darker blue for hover
            'secondary': (255, 193, 7),       # Golden yellow
            'secondary_dark': (218, 165, 32), # Darker yellow
            
            # Background colors
            'bg_main': (18, 18, 24),          # Dark navy background
            'bg_surface': (28, 28, 38),       # Slightly lighter surface
            'bg_card': (38, 38, 48),          # Card backgrounds
            
            # Text colors
            'text_primary': (255, 255, 255),  # White
            'text_secondary': (200, 200, 220), # Light gray
            'text_muted': (150, 150, 170),    # Muted gray
            
            # Status colors
            'success': (46, 204, 113),        # Green
            'success_dark': (39, 174, 96),    # Darker green
            'error': (231, 76, 60),           # Red
            'error_dark': (192, 57, 43),      # Darker red
            'warning': (241, 196, 15),        # Yellow warning
            'info': (52, 152, 219),           # Blue info
            
            # UI elements
            'border': (60, 60, 80),           # Border color
            'border_active': (100, 100, 130), # Active border
            'shadow': (0, 0, 0, 50),          # Shadow with transparency
        }
        
        # Typography hierarchy
        try:
            self.fonts = {
                'title': pygame.font.Font("./data/fonts/americancaptain.ttf", 48),      # Big titles
                'heading': pygame.font.Font("./data/fonts/americancaptain.ttf", 36),    # Section headings
                'body': pygame.font.Font("./data/fonts/americancaptain.ttf", 24),       # Body text
                'small': pygame.font.Font("./data/fonts/americancaptain.ttf", 18),      # Small text
                'caption': pygame.font.Font("./data/fonts/americancaptain.ttf", 14),    # Captions
            }
        except:
            # Fallback to system font if custom font fails
            self.fonts = {
                'title': pygame.font.Font(None, 48),
                'heading': pygame.font.Font(None, 36),
                'body': pygame.font.Font(None, 24),
                'small': pygame.font.Font(None, 18),
                'caption': pygame.font.Font(None, 14),
            }
        
        # Keep backward compatibility
        self.font = self.fonts['body']
        
        # Layout grid system (16-column grid)
        self.grid = {
            'cols': 16,
            'margin': 40,  # Margin from screen edges
            'gutter': 20,  # Space between columns
        }
        self.col_width = (self.width - 2 * self.grid['margin'] - (self.grid['cols'] - 1) * self.grid['gutter']) // self.grid['cols']
        
        # Updated flag size for new resolution
        self.flag_size = (600, 450)
        self.text_vertical_spacing = 30
        
        # Dropdown state variables
        self.dropdown_open = False
        self.selected_gamemode = "europe"  # Default gamemode
        self.rankings_gamemode = "europe"  # Gamemode for rankings display
        
        # Music control variables
        self.music_dropdown_open = False
        self.selected_song = "Random"  # Default to random
        
        # Mode selection variables
        self.selected_mode = "normal"  # normal, endless, blitz
        self.selected_mode_map = "europe"  # map for mode selection
        self.mode_map_dropdown_open = False  # dropdown state for mode selection map
        
        # Rankings filter variables
        self.selected_rankings_filter = "all"  # all, normal, endless, blitz
        
        # Modern layout using grid system
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Main action buttons (larger, more prominent)
        button_width = 200
        button_height = 60
        button_spacing = 25
        
        self.play_button_rect = pygame.Rect(center_x - button_width // 2, center_y - 40, button_width, button_height)
        self.splash_rankings_button_rect = pygame.Rect(center_x - button_width // 2, center_y + 35, button_width, button_height)
        self.splash_quit_button_rect = pygame.Rect(center_x - button_width // 2, center_y + 110, button_width, button_height)
        
        # Music controls (top right, refined) - made wider for text
        music_controls_x = self.width - 280
        self.music_play_button_rect = pygame.Rect(music_controls_x, 30, 80, 40)
        self.music_pause_button_rect = pygame.Rect(music_controls_x + 90, 30, 80, 40)
        self.music_stop_button_rect = pygame.Rect(music_controls_x + 180, 30, 80, 40)
        
        # Music dropdown (wider for new resolution)
        self.music_dropdown_rect = pygame.Rect(music_controls_x, 80, 270, 40)

        
        # Modern text input design
        self.input_text = ""
        input_width = 400
        input_height = 50
        input_x = self.width // 2 - input_width // 2
        input_y = self.height - 120
        
        self.input_border = pygame.Rect(input_x - 2, input_y - 2, input_width + 4, input_height + 4)
        self.input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
        self.input_color = self.colors['secondary']  # Modern gold color
        self.input_active = False
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        
        # Game control buttons
        self.game_exit_button_rect = pygame.Rect(self.width - 150, self.height - 80, 120, 50)  # Bottom-right corner
        
        # Game over and rankings buttons (updated for new layout)
        self.quit_button_rect = pygame.Rect(center_x - 160, center_y + 100, 140, 60)
        self.rankings_button_rect = pygame.Rect(center_x + 20, center_y + 100, 140, 60)
        
        # Rankings navigation buttons (side by side to avoid overlap)
        button_width = 180
        button_height = 50
        button_spacing = 30
        rankings_buttons_y = self.height - 80
        
        self.rankings_back_button_rect = pygame.Rect(
            center_x - button_width - button_spacing // 2, 
            rankings_buttons_y, 
            button_width, 
            button_height
        )
        self.rank_sel_main_menu_button_rect = pygame.Rect(
            center_x + button_spacing // 2, 
            rankings_buttons_y, 
            button_width, 
            button_height
        )
        
        self.rankings_back_text = self.fonts['body'].render("Back", True, self.colors['text_primary'])
        self.main_menu_button_rect = pygame.Rect(center_x - 100, center_y + 180, 200, 60)

        # Modern ranking mode selection layout (3x2 grid)
        mode_button_width, mode_button_height = 180, 80
        mode_padding_x, mode_padding_y = 30, 25
        
        # Calculate grid positions
        grid_start_x = center_x - (mode_button_width * 1.5 + mode_padding_x * 0.5)
        grid_start_y = center_y - (mode_button_height + mode_padding_y * 0.5)
        
        # Row 1
        self.rank_mode_global_button_rect = pygame.Rect(grid_start_x, grid_start_y, mode_button_width, mode_button_height)
        self.rank_mode_europe_button_rect = pygame.Rect(grid_start_x + mode_button_width + mode_padding_x, grid_start_y, mode_button_width, mode_button_height)
        self.rank_mode_america_button_rect = pygame.Rect(grid_start_x + (mode_button_width + mode_padding_x) * 2, grid_start_y, mode_button_width, mode_button_height)
        
        # Row 2
        row2_y = grid_start_y + mode_button_height + mode_padding_y
        self.rank_mode_asia_button_rect = pygame.Rect(grid_start_x, row2_y, mode_button_width, mode_button_height)
        self.rank_mode_oceania_button_rect = pygame.Rect(grid_start_x + mode_button_width + mode_padding_x, row2_y, mode_button_width, mode_button_height)
        self.rank_mode_africa_button_rect = pygame.Rect(grid_start_x + (mode_button_width + mode_padding_x) * 2, row2_y, mode_button_width, mode_button_height)
        
        # Navigation buttons
        self.rank_mode_main_menu_button_rect = pygame.Rect(center_x - 100, self.height - 80, 200, 50)
        self.rank_sel_main_menu_text = self.fonts['body'].render("Main Menu", True, self.colors['text_primary'])
        self.dropdown_rect = pygame.Rect(self.play_button_rect.x + self.play_button_rect.width, self.play_button_rect.y,
                                        self.play_button_rect.width, 30)

        # Mode selection screen - completely redesigned modern layout
        mode_card_width, mode_card_height = 350, 240
        mode_spacing = 60
        mode_start_x = center_x - (mode_card_width * 1.5 + mode_spacing)
        mode_y = center_y - 80  # Centered vertically
        
        # Mode selection cards - larger and more spaced
        self.mode_normal_button_rect = pygame.Rect(mode_start_x, mode_y, mode_card_width, mode_card_height)
        self.mode_endless_button_rect = pygame.Rect(mode_start_x + mode_card_width + mode_spacing, mode_y, mode_card_width, mode_card_height)
        self.mode_blitz_button_rect = pygame.Rect(mode_start_x + (mode_card_width + mode_spacing) * 2, mode_y, mode_card_width, mode_card_height)
        
        # Map selector - moved to top right corner as compact buttons
        map_button_width = 120
        map_button_height = 35
        map_start_x = self.width - 150
        map_start_y = 80
        
        self.map_global_rect = pygame.Rect(map_start_x, map_start_y, map_button_width, map_button_height)
        self.map_europe_rect = pygame.Rect(map_start_x, map_start_y + 40, map_button_width, map_button_height)
        self.map_asia_rect = pygame.Rect(map_start_x, map_start_y + 80, map_button_width, map_button_height)
        self.map_america_rect = pygame.Rect(map_start_x, map_start_y + 120, map_button_width, map_button_height)
        self.map_africa_rect = pygame.Rect(map_start_x, map_start_y + 160, map_button_width, map_button_height)
        self.map_oceania_rect = pygame.Rect(map_start_x, map_start_y + 200, map_button_width, map_button_height)
        
        # Mode selection navigation
        self.mode_back_button_rect = pygame.Rect(center_x - 100, self.height - 100, 200, 50)

        # Rankings filter tabs - completely repositioned for 1920x1080
        tab_width = 180
        tab_height = 60
        tab_spacing = 30
        # Calculate proper center positioning for 4 tabs with new resolution
        total_width = tab_width * 4 + tab_spacing * 3
        tabs_start_x = center_x - (total_width // 2)
        tabs_y = 180  # More space from top with higher resolution
        
        self.rank_filter_all_rect = pygame.Rect(tabs_start_x, tabs_y, tab_width, tab_height)
        self.rank_filter_normal_rect = pygame.Rect(tabs_start_x + tab_width + tab_spacing, tabs_y, tab_width, tab_height)
        self.rank_filter_endless_rect = pygame.Rect(tabs_start_x + (tab_width + tab_spacing) * 2, tabs_y, tab_width, tab_height)
        self.rank_filter_blitz_rect = pygame.Rect(tabs_start_x + (tab_width + tab_spacing) * 3, tabs_y, tab_width, tab_height)

    # Getter and setter methods for gamemode selection
    def get_selected_gamemode(self):
        return self.selected_gamemode
    
    def set_selected_gamemode(self, gamemode):
        self.selected_gamemode = gamemode
    
    def get_rankings_gamemode(self):
        return self.rankings_gamemode
    
    def set_rankings_gamemode(self, gamemode):
        self.rankings_gamemode = gamemode
    
    def toggle_dropdown(self):
        self.dropdown_open = not self.dropdown_open
    
    def close_dropdown(self):
        self.dropdown_open = False
    
    def is_dropdown_open(self):
        return self.dropdown_open
    
    def handle_dropdown_click(self, mouse_pos, gamemodes):
        """Handle clicks on dropdown menu and return True if a selection was made"""
        if hasattr(self, 'dropdown_rect') and self.dropdown_rect.collidepoint(mouse_pos):
            if not self.dropdown_open:
                self.toggle_dropdown()
                return True
            else:
                self.close_dropdown()
                return True
        
        # Check clicks on dropdown options
        if self.dropdown_open:
            for i, mode in enumerate(gamemodes):
                option_rect_name = f"dropdown_option_{i}_rect"
                if hasattr(self, option_rect_name):
                    option_rect = getattr(self, option_rect_name)
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_gamemode = mode
                        self.close_dropdown()
                        return True
        
        # Click outside dropdown - close it
        if self.dropdown_open:
            self.close_dropdown()
            return True
            
        return False

    # Animation and State Management Methods
    def reset_animations(self, screen_type="splash"):
        """Reset animations for a new screen"""
        self.animation_start_time = pygame.time.get_ticks()
        for anim_name in self.animations:
            if anim_name.startswith(screen_type):
                self.animations[anim_name]['completed'] = False

    def get_animation_alpha(self, animation_name):
        """Calculate alpha value for fade-in animation"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.animation_start_time
        
        anim = self.animations.get(animation_name, {})
        delay = anim.get('delay', 0)
        duration = anim.get('duration', 1000)
        
        if elapsed < delay:
            return 0
        
        progress = min(1.0, (elapsed - delay) / duration)
        
        # Smooth easing function (ease-out)
        alpha = int(255 * (1 - (1 - progress) ** 3))
        
        if progress >= 1.0:
            self.animations[animation_name]['completed'] = True
            
        return alpha

    def get_animation_offset(self, animation_name, start_offset=50):
        """Calculate position offset for slide-in animation"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.animation_start_time
        
        anim = self.animations.get(animation_name, {})
        delay = anim.get('delay', 0)
        duration = anim.get('duration', 1000)
        
        if elapsed < delay:
            return start_offset
        
        progress = min(1.0, (elapsed - delay) / duration)
        
        # Smooth easing for slide-in
        offset = int(start_offset * (1 - progress) ** 2)
        return offset

    def trigger_feedback_animation(self, feedback_type):
        """Trigger feedback animation for correct/incorrect answers"""
        if feedback_type in self.feedback_animations:
            self.feedback_animations[feedback_type]['active'] = True
            self.feedback_animations[feedback_type]['start_time'] = pygame.time.get_ticks()
    


    def draw_animated_surface(self, surface, rect, animation_name, slide_direction="up"):
        """Draw surface with fade-in and slide animation"""
        alpha = self.get_animation_alpha(animation_name)
        if alpha <= 0:
            return
            
        # Create animated surface
        animated_surface = surface.copy()
        animated_surface.set_alpha(alpha)
        
        # Calculate slide offset
        if slide_direction == "up":
            offset_y = self.get_animation_offset(animation_name, 30)
            draw_rect = pygame.Rect(rect.x, rect.y + offset_y, rect.width, rect.height)
        elif slide_direction == "down":
            offset_y = -self.get_animation_offset(animation_name, 30)
            draw_rect = pygame.Rect(rect.x, rect.y + offset_y, rect.width, rect.height)
        elif slide_direction == "left":
            offset_x = self.get_animation_offset(animation_name, 40)
            draw_rect = pygame.Rect(rect.x + offset_x, rect.y, rect.width, rect.height)
        elif slide_direction == "right":
            offset_x = -self.get_animation_offset(animation_name, 40)
            draw_rect = pygame.Rect(rect.x + offset_x, rect.y, rect.width, rect.height)
        else:
            draw_rect = rect
            
        self.screen.blit(animated_surface, draw_rect)

    def draw_loading_indicator(self, x, y, size=40):
        """Draw modern spinning loading indicator"""
        current_time = pygame.time.get_ticks()
        rotation = (current_time * 0.3) % 360
        
        # Draw spinning circle segments
        center = (x, y)
        for i in range(8):
            angle = rotation + (i * 45)
            alpha = int(255 * (1 - i / 8))
            
            # Calculate position
            rad = math.radians(angle)
            start_x = center[0] + math.cos(rad) * (size // 2 - 5)
            start_y = center[1] + math.sin(rad) * (size // 2 - 5)
            end_x = center[0] + math.cos(rad) * (size // 2)
            end_y = center[1] + math.sin(rad) * (size // 2)
            
            # Create surface for alpha blending
            line_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            color = (*self.colors['primary'][:3], alpha)
            pygame.draw.line(line_surface, color, 
                           (start_x - x + size//2, start_y - y + size//2), 
                           (end_x - x + size//2, end_y - y + size//2), 3)
            self.screen.blit(line_surface, (x - size//2, y - size//2))

    def set_state(self, new_state):
        """Change application state with transition"""
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.reset_animations(new_state)

    def draw_modern_button_with_alpha(self, rect, text, style='primary', hover=False, alpha=255):
        """Draw modern button with alpha transparency"""
        # Create a surface for the button with alpha
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Determine colors based on style and state
        if style == 'primary':
            bg_color = self.colors['primary_dark'] if hover else self.colors['primary']
            text_color = self.colors['text_primary']
            border_color = self.colors['primary_dark'] if hover else self.colors['primary']
        elif style == 'success':
            bg_color = self.colors['success_dark'] if hover else self.colors['success']
            text_color = self.colors['text_primary']
            border_color = self.colors['success_dark'] if hover else self.colors['success']
        elif style == 'error':
            bg_color = self.colors['error_dark'] if hover else self.colors['error']
            text_color = self.colors['text_primary']
            border_color = self.colors['error_dark'] if hover else self.colors['error']
        elif style == 'secondary':
            bg_color = self.colors['secondary_dark'] if hover else self.colors['secondary']
            text_color = self.colors['bg_main']
            border_color = self.colors['secondary_dark'] if hover else self.colors['secondary']
        else:  # default/outline style
            bg_color = self.colors['bg_surface'] if not hover else self.colors['bg_card']
            text_color = self.colors['text_primary']
            border_color = self.colors['border_active'] if hover else self.colors['border']
        
        # Apply alpha to colors
        bg_color = (*bg_color[:3], int(alpha * 0.9))
        border_color = (*border_color[:3], alpha)
        text_color = (*text_color[:3], alpha)
        
        # Draw shadow effect on surface
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        shadow_alpha = int(alpha * 0.3)
        shadow_color = (0, 0, 0, shadow_alpha)
        pygame.draw.rect(shadow_surface, shadow_color, (2, 2, rect.width, rect.height))
        
        # Draw main button on surface
        pygame.draw.rect(button_surface, bg_color, (0, 0, rect.width, rect.height))
        pygame.draw.rect(button_surface, border_color, (0, 0, rect.width, rect.height), 2)
        
        # Add gradient effect for hover
        if hover:
            gradient_surface = pygame.Surface((rect.width, rect.height // 2), pygame.SRCALPHA)
            gradient_color = (255, 255, 255, int(alpha * 0.2))
            gradient_surface.fill(gradient_color)
            button_surface.blit(gradient_surface, (0, 0))
        
        # Draw text on surface (ensure it's visible)
        if alpha < 255:
            # For fading buttons, use solid colors but apply alpha to entire surface
            text_surface = self.fonts['body'].render(text, True, self.colors['text_primary'] if style != 'secondary' else self.colors['bg_main'])
        else:
            text_surface = self.fonts['body'].render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(rect.width // 2, rect.height // 2))
        button_surface.blit(text_surface, text_rect)
        
        # Blit the complete button to screen
        self.screen.blit(shadow_surface, (rect.x, rect.y))
        self.screen.blit(button_surface, rect)

    def draw_functional_dropdown_with_alpha(self, rect, color, selected_text, gamemodes, alpha=255):
        """Draw functional dropdown with alpha transparency"""
        # Create dropdown surface
        dropdown_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Apply alpha to colors
        bg_color = (*self.colors['bg_surface'][:3], alpha)
        border_color = (*self.colors['border'][:3], alpha)
        text_color = (*self.colors['text_primary'][:3], alpha)
        
        # Draw main dropdown button
        pygame.draw.rect(dropdown_surface, bg_color, (0, 0, rect.width, rect.height))
        pygame.draw.rect(dropdown_surface, border_color, (0, 0, rect.width, rect.height), 2)
        
        # Draw text
        display_text = selected_text.upper()
        text_surface = self.fonts['body'].render(display_text, True, text_color)
        text_rect = text_surface.get_rect(center=(rect.width // 2, rect.height // 2))
        dropdown_surface.blit(text_surface, text_rect)
        
        # Draw arrow
        arrow_color = (*self.colors['text_secondary'][:3], alpha)
        arrow_x = rect.width - 20
        arrow_y = rect.height // 2
        
        if self.dropdown_open:
            # Up arrow when open
            pygame.draw.polygon(dropdown_surface, arrow_color, [
                (arrow_x, arrow_y + 3),
                (arrow_x + 8, arrow_y + 3),
                (arrow_x + 4, arrow_y - 3)
            ])
        else:
            # Down arrow when closed
            pygame.draw.polygon(dropdown_surface, arrow_color, [
                (arrow_x, arrow_y - 3),
                (arrow_x + 8, arrow_y - 3),
                (arrow_x + 4, arrow_y + 3)
            ])
        
        self.screen.blit(dropdown_surface, rect)
        
        # Note: Dropdown options rendering will be handled by the regular dropdown system

    def draw_music_dropdown_with_alpha(self, rect, color, selected_text, song_names, alpha=255):
        """Draw music dropdown with alpha transparency"""
        # Draw main dropdown button
        pygame.draw.rect(self.screen, (*self.colors['bg_surface'][:3], int(alpha * 0.9)), rect)
        pygame.draw.rect(self.screen, (*self.colors['border'][:3], alpha), rect, 2)
        
        # Truncate text if needed
        display_text = selected_text
        if len(display_text) > 18:
            display_text = display_text[:15] + "..."
        
        # Draw text with good visibility
        if alpha < 255:
            text_surface = self.fonts['small'].render(display_text, True, self.colors['text_primary'])
            text_surface.set_alpha(alpha)
        else:
            text_surface = self.fonts['small'].render(display_text, True, self.colors['text_primary'])
            
        text_y = rect.y + rect.height // 2 - text_surface.get_height() // 2
        self.screen.blit(text_surface, (rect.x + 8, text_y))
        
        # Draw arrow
        arrow_x = rect.x + rect.width - 25
        arrow_y = rect.y + rect.height // 2
        
        if self.music_dropdown_open:
            # Up arrow when open
            pygame.draw.polygon(self.screen, (*self.colors['text_secondary'][:3], alpha), [
                (arrow_x, arrow_y + 3),
                (arrow_x + 8, arrow_y + 3),
                (arrow_x + 4, arrow_y - 3)
            ])
        else:
            # Down arrow when closed
            pygame.draw.polygon(self.screen, (*self.colors['text_secondary'][:3], alpha), [
                (arrow_x, arrow_y - 3),
                (arrow_x + 8, arrow_y - 3),
                (arrow_x + 4, arrow_y + 3)
            ])
        
        # Only draw dropdown options if open (handled by the main music dropdown system)
        if self.music_dropdown_open and alpha >= 255:
            # Let the main system handle the options to avoid duplication
            pass

    def draw_game_music_controls(self):
        """Draw compact modern music controls during gameplay"""
        import audio
        
        # Compact music controls panel in top right
        panel_width = 200
        panel_height = 60
        controls_x = self.width - panel_width - 20
        controls_y = 20
        
        # Control panel background
        panel_rect = pygame.Rect(controls_x, controls_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, self.colors['bg_surface'], panel_rect)
        pygame.draw.rect(self.screen, self.colors['border'], panel_rect, 2)
        
        # Small music control buttons
        button_size = 25
        button_y = controls_y + 8
        play_rect = pygame.Rect(controls_x + 10, button_y, button_size, button_size)
        pause_rect = pygame.Rect(controls_x + 40, button_y, button_size, button_size)
        stop_rect = pygame.Rect(controls_x + 70, button_y, button_size, button_size)
        
        # Get music state
        is_playing = audio.is_playing()
        is_paused = audio.is_paused()
        
        # Draw buttons with modern styling
        mouse_pos = pygame.mouse.get_pos()
        
        # Play button
        play_hover = play_rect.collidepoint(mouse_pos)
        play_color = self.colors['text_muted'] if is_playing else (self.colors['success_dark'] if play_hover else self.colors['success'])
        pygame.draw.rect(self.screen, play_color, play_rect)
        pygame.draw.rect(self.screen, self.colors['border'], play_rect, 1)
        play_text = self.fonts['caption'].render("►", True, self.colors['text_primary'])
        play_text_rect = play_text.get_rect(center=play_rect.center)
        self.screen.blit(play_text, play_text_rect)
        
        # Pause button
        pause_hover = pause_rect.collidepoint(mouse_pos)
        pause_color = (self.colors['warning'] if pause_hover else self.colors['secondary']) if is_playing else self.colors['text_muted']
        pygame.draw.rect(self.screen, pause_color, pause_rect)
        pygame.draw.rect(self.screen, self.colors['border'], pause_rect, 1)
        pause_text = self.fonts['caption'].render("‖", True, self.colors['text_primary'])
        pause_text_rect = pause_text.get_rect(center=pause_rect.center)
        self.screen.blit(pause_text, pause_text_rect)
        
        # Stop button
        stop_hover = stop_rect.collidepoint(mouse_pos)
        stop_color = (self.colors['error_dark'] if stop_hover else self.colors['error']) if (is_playing or is_paused) else self.colors['text_muted']
        pygame.draw.rect(self.screen, stop_color, stop_rect)
        pygame.draw.rect(self.screen, self.colors['border'], stop_rect, 1)
        stop_text = self.fonts['caption'].render("■", True, self.colors['text_primary'])
        stop_text_rect = stop_text.get_rect(center=stop_rect.center)
        self.screen.blit(stop_text, stop_text_rect)
        
        # Store rects for click detection
        self.game_music_play_rect = play_rect
        self.game_music_pause_rect = pause_rect
        self.game_music_stop_rect = stop_rect
        
        # Show current song (compact)
        current = audio.get_current_song()
        if current and is_playing:
            display_name = current.replace(".mp3", "").replace("OST - ", "").replace("OST_ ", "")
            display_name = display_name.replace("_ ", " - ").replace("__", " - ")
            if len(display_name) > 22:
                display_name = display_name[:19] + "..."
            song_text = self.fonts['caption'].render(f"♪ {display_name}", True, self.colors['info'])
            self.screen.blit(song_text, (controls_x + 10, controls_y + 40))
        else:
            status_text = self.fonts['caption'].render("♪ No music", True, self.colors['text_muted'])
            self.screen.blit(status_text, (controls_x + 10, controls_y + 40))

    def handle_game_music_click(self, mouse_pos):
        """Handle music controls during gameplay"""
        import audio
        
        if hasattr(self, 'game_music_play_rect') and self.game_music_play_rect.collidepoint(mouse_pos):
            audio.playMusic(random_song=True)
            return True
        elif hasattr(self, 'game_music_pause_rect') and self.game_music_pause_rect.collidepoint(mouse_pos):
            audio.pauseMusic()
            return True
        elif hasattr(self, 'game_music_stop_rect') and self.game_music_stop_rect.collidepoint(mouse_pos):
            audio.stopMusic()
            return True
            
        return False

    def draw_music_controls(self):
        """Draw music control buttons and dropdown"""
        import audio
        
        # Draw music control buttons with different colors based on state
        is_playing = audio.is_playing()
        is_paused = audio.is_paused()
        
        # Play button (green if not playing, gray if playing)
        play_color = (100, 100, 100) if is_playing else (0, 200, 0)
        self.draw_small_button(self.music_play_button_rect, play_color, "PLAY")
        
        # Pause button (yellow if music is playing, gray if not)
        pause_color = (200, 200, 0) if is_playing else (100, 100, 100)
        self.draw_small_button(self.music_pause_button_rect, pause_color, "PAUSE")
        
        # Stop button (red if music is playing or paused, gray if stopped)
        stop_color = (200, 0, 0) if (is_playing or is_paused) else (100, 100, 100)
        self.draw_small_button(self.music_stop_button_rect, stop_color, "STOP")
        
        # Music selection dropdown
        song_names = ["Random"] + audio.get_song_names()
        self.draw_music_dropdown(self.music_dropdown_rect, (120, 120, 180), self.selected_song, song_names)
        
        # Show current playing song
        current = audio.get_current_song()
        if current:
            display_name = current.replace(".mp3", "").replace("OST - ", "").replace("OST_ ", "")
            display_name = display_name.replace("_ ", " - ").replace("__", " - ")
            now_playing_text = f"♪ {display_name}"
            # Truncate if too long
            if len(now_playing_text) > 30:
                now_playing_text = now_playing_text[:27] + "..."
        else:
            now_playing_text = "♪ No music playing"
            
        # Draw now playing text
        small_font = pygame.font.Font("./data/fonts/americancaptain.ttf", 18)
        playing_surface = small_font.render(now_playing_text, True, (200, 200, 255))
        self.screen.blit(playing_surface, (self.music_dropdown_rect.x, self.music_dropdown_rect.y + 35))

    def draw_small_button(self, rect, color, text):
        """Draw a smaller button for music controls"""
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)  # White border
        small_font = pygame.font.Font("./data/fonts/americancaptain.ttf", 18)
        text_surface = small_font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, (rect.centerx - text_surface.get_width() // 2, rect.centery - text_surface.get_height() // 2))

    def draw_music_dropdown(self, rect, color, selected_text, song_names):
        """Draw modern music selection dropdown with proper spacing"""
        # Modern dropdown styling
        dropdown_bg = self.colors['bg_surface']
        dropdown_border = self.colors['border']
        dropdown_text = self.colors['text_primary']
        
        # Draw main dropdown button with modern styling
        pygame.draw.rect(self.screen, dropdown_bg, rect)
        pygame.draw.rect(self.screen, dropdown_border, rect, 2)
        
        # Modern arrow design
        arrow_x = rect.x + rect.width - 25
        arrow_y = rect.centery
        arrow_color = self.colors['text_secondary']
        
        if self.music_dropdown_open:
            # Up arrow when open - modern triangular design
            pygame.draw.polygon(self.screen, arrow_color, [
                (arrow_x, arrow_y + 3),
                (arrow_x + 8, arrow_y + 3),
                (arrow_x + 4, arrow_y - 3)
            ])
        else:
            # Down arrow when closed
            pygame.draw.polygon(self.screen, arrow_color, [
                (arrow_x, arrow_y - 3),
                (arrow_x + 8, arrow_y - 3),
                (arrow_x + 4, arrow_y + 3)
            ])

        # Draw selected text with modern typography
        display_text = selected_text
        if len(display_text) > 18:  # Adjusted for better fit
            display_text = display_text[:15] + "..."
            
        # Use design system font
        text_surface = self.fonts['small'].render(display_text, True, dropdown_text)
        text_y = rect.centery - text_surface.get_height() // 2
        self.screen.blit(text_surface, (rect.x + 8, text_y))

        # Draw dropdown options if open with proper spacing
        if self.music_dropdown_open:
            option_height = 35  # Increased height for better readability
            max_options = min(7, len(song_names))  # Limit to 7 for better fit
            
            # Calculate dropdown panel dimensions
            panel_height = option_height * max_options
            panel_rect = pygame.Rect(rect.x, rect.y + rect.height + 2, rect.width, panel_height)
            
            # Draw dropdown panel background with shadow
            shadow_rect = pygame.Rect(panel_rect.x + 3, panel_rect.y + 3, panel_rect.width, panel_rect.height)
            shadow_surface = pygame.Surface((panel_rect.width, panel_rect.height))
            shadow_surface.set_alpha(40)
            shadow_surface.fill((0, 0, 0))
            self.screen.blit(shadow_surface, shadow_rect)
            
            # Main panel
            pygame.draw.rect(self.screen, dropdown_bg, panel_rect)
            pygame.draw.rect(self.screen, dropdown_border, panel_rect, 2)
            
            # Draw individual options
            for i in range(max_options):
                if i >= len(song_names):
                    break
                    
                song = song_names[i]
                option_rect = pygame.Rect(
                    rect.x + 1, 
                    rect.y + rect.height + 2 + (i * option_height) + 1, 
                    rect.width - 2, 
                    option_height - 1
                )
                
                # Modern option styling
                if song == self.selected_song:
                    # Selected option - use primary color
                    pygame.draw.rect(self.screen, self.colors['primary'], option_rect)
                    text_color = self.colors['text_primary']
                else:
                    # Regular option with hover detection
                    mouse_pos = pygame.mouse.get_pos()
                    if option_rect.collidepoint(mouse_pos):
                        # Hover state
                        pygame.draw.rect(self.screen, self.colors['bg_card'], option_rect)
                        text_color = self.colors['text_primary']
                    else:
                        # Normal state
                        text_color = self.colors['text_secondary']
                
                # Truncate song name appropriately
                display_song = song
                if len(display_song) > 22:
                    display_song = display_song[:19] + "..."
                
                # Draw option text with proper vertical centering
                option_text = self.fonts['caption'].render(display_song, True, text_color)
                text_x = option_rect.x + 8
                text_y = option_rect.centery - option_text.get_height() // 2
                self.screen.blit(option_text, (text_x, text_y))
                
                # Store option rect for click detection
                setattr(self, f"music_option_{i}_rect", option_rect)

    def handle_music_controls_click(self, mouse_pos):
        """Handle clicks on music control buttons and dropdown"""
        import audio
        
        # Check music control buttons
        if self.music_play_button_rect.collidepoint(mouse_pos):
            if self.selected_song == "Random":
                audio.playMusic(random_song=True)
            else:
                audio.playMusic(song_name=self.selected_song)
            return True
            
        elif self.music_pause_button_rect.collidepoint(mouse_pos):
            audio.pauseMusic()
            return True
            
        elif self.music_stop_button_rect.collidepoint(mouse_pos):
            audio.stopMusic()
            return True
            
        # Handle music dropdown
        elif self.music_dropdown_rect.collidepoint(mouse_pos):
            if not self.music_dropdown_open:
                self.music_dropdown_open = True
            else:
                self.music_dropdown_open = False
            return True
        
        # Check clicks on dropdown options
        if self.music_dropdown_open:
            song_names = ["Random"] + audio.get_song_names()
            max_options = min(8, len(song_names))
            
            for i in range(max_options):
                if i >= len(song_names):
                    break
                    
                option_rect_name = f"music_option_{i}_rect"
                if hasattr(self, option_rect_name):
                    option_rect = getattr(self, option_rect_name)
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_song = song_names[i]
                        self.music_dropdown_open = False
                        return True
        
        # Click outside music dropdown - close it
        if self.music_dropdown_open:
            self.music_dropdown_open = False
            return True
            
        return False

    
    def showGame(self, current_country, score, game_flags_images, lives, 
                 selected_game_mode="normal", game_start_time=0, blitz_time_limit=60, flags_shown_count=0):
        # Modern gradient background
        self.screen.fill(self.colors['bg_main'])
        self.draw_gradient_background()
        
        # Draw EXIT button (top-left) - ALWAYS VISIBLE with better contrast
        mouse_pos = pygame.mouse.get_pos()
        exit_hover = self.game_exit_button_rect.collidepoint(mouse_pos)
        
        # Draw EXIT button with extra emphasis to make it more visible
        # Add a semi-transparent background for better visibility
        exit_bg_rect = pygame.Rect(self.game_exit_button_rect.x - 5, self.game_exit_button_rect.y - 5, 
                                   self.game_exit_button_rect.width + 10, self.game_exit_button_rect.height + 10)
        exit_bg_surface = pygame.Surface((exit_bg_rect.width, exit_bg_rect.height))
        exit_bg_surface.set_alpha(100)
        exit_bg_surface.fill((0, 0, 0))  # Dark background for contrast
        self.screen.blit(exit_bg_surface, exit_bg_rect)
        
        # Draw the actual EXIT button
        self.draw_modern_button(self.game_exit_button_rect, "EXIT", 'error', exit_hover)
        
        # Update error message state (non-blocking)
        self.update_error_message()
        
        # Draw mode-specific UI elements
        self.draw_mode_info(selected_game_mode, game_start_time, blitz_time_limit, flags_shown_count)
        
        # Display the current flag with modern card styling
        flag_image = game_flags_images[current_country]
        flag_rect = flag_image.get_rect()
        flag_rect.center = (self.width // 2, self.height // 2 - 50)
        
        # Draw flag card background
        card_padding = 20
        flag_card_rect = pygame.Rect(
            flag_rect.x - card_padding,
            flag_rect.y - card_padding,
            flag_rect.width + card_padding * 2,
            flag_rect.height + card_padding * 2
        )
        
        # Card shadow
        shadow_rect = pygame.Rect(flag_card_rect.x + 4, flag_card_rect.y + 4, flag_card_rect.width, flag_card_rect.height)
        shadow_surface = pygame.Surface((flag_card_rect.width, flag_card_rect.height))
        shadow_surface.set_alpha(40)
        shadow_surface.fill((0, 0, 0))
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Main card
        pygame.draw.rect(self.screen, self.colors['bg_card'], flag_card_rect)
        pygame.draw.rect(self.screen, self.colors['border'], flag_card_rect, 3)
        
        # Flag image
        self.screen.blit(flag_image, flag_rect)

        # Modern HUD design
        self.draw_game_hud(score, lives)

        # Modern input box
        self.draw_modern_input_box()

        # Game instructions
        instruction_text = self.fonts['small'].render("Type the country name and press ENTER", True, self.colors['text_secondary'])
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height - 60))
        self.screen.blit(instruction_text, instruction_rect)

        # Draw error message overlay if active (above everything except music controls)
        self.draw_error_message_overlay()

        # Draw music controls (compact in top right) - always visible
        self.draw_game_music_controls()

        pygame.display.flip()
    
    def draw_mode_info(self, selected_game_mode, game_start_time, blitz_time_limit, flags_shown_count):
        """Draw mode-specific information (timer, counters, etc.)"""
        
        if selected_game_mode == "blitz":
            # Special positioning for blitz timer - bottom left corner
            timer_width = 200
            timer_height = 80
            timer_x = 30  # Left side, matching EXIT button position
            timer_y = self.height - 150  # Above EXIT button area
            
            # Timer panel background
            timer_rect = pygame.Rect(timer_x, timer_y, timer_width, timer_height)
            pygame.draw.rect(self.screen, self.colors['bg_surface'], timer_rect)
            pygame.draw.rect(self.screen, self.colors['border'], timer_rect, 2)
            
            # Mode title
            mode_title = "⚡ BLITZ MODE"
            title_text = self.fonts['small'].render(mode_title, True, self.colors['text_primary'])
            title_rect = title_text.get_rect(center=(timer_x + timer_width // 2, timer_y + 20))
            self.screen.blit(title_text, title_rect)
            
            # Timer display
            if game_start_time > 0:
                elapsed_time = (pygame.time.get_ticks() - game_start_time) / 1000
                remaining_time = max(0, blitz_time_limit - elapsed_time)
                
                # Color based on remaining time
                if remaining_time <= 10:
                    timer_color = self.colors['error']  # Red when low
                elif remaining_time <= 20:
                    timer_color = self.colors['warning']  # Yellow when medium
                else:
                    timer_color = self.colors['success']  # Green when high
                
                timer_text = f"⏱️ {remaining_time:.1f}s"
                timer_surface = self.fonts['heading'].render(timer_text, True, timer_color)
                timer_surface_rect = timer_surface.get_rect(center=(timer_x + timer_width // 2, timer_y + 50))
                self.screen.blit(timer_surface, timer_surface_rect)
        else:
            # Standard positioning for other modes - top center
            info_x = self.width // 2 - 200
            info_y = 20
            info_width = 400
            info_height = 80
            
            # Mode info panel background
            info_rect = pygame.Rect(info_x, info_y, info_width, info_height)
            pygame.draw.rect(self.screen, self.colors['bg_surface'], info_rect)
            pygame.draw.rect(self.screen, self.colors['border'], info_rect, 2)
            
            # Mode title with icon
            mode_icons = {"normal": "🎯", "endless": "♾️"}
            mode_icon = mode_icons.get(selected_game_mode, "🎮")
            mode_title = f"{mode_icon} {selected_game_mode.upper()} MODE"
            
            title_text = self.fonts['body'].render(mode_title, True, self.colors['text_primary'])
            title_rect = title_text.get_rect(center=(info_x + info_width // 2, info_y + 25))
            self.screen.blit(title_text, title_rect)
            
            # Mode-specific information
            if selected_game_mode == "endless":
                # Flag counter for endless mode
                counter_text = f"🚩 Flags Shown: {flags_shown_count}"
                counter_surface = self.fonts['small'].render(counter_text, True, self.colors['secondary'])
                counter_rect = counter_surface.get_rect(center=(info_x + info_width // 2, info_y + 55))
                self.screen.blit(counter_surface, counter_rect)
            
            elif selected_game_mode == "normal":
                # Completion indicator for normal mode
                normal_text = "Complete all flags to win!"
                normal_surface = self.fonts['small'].render(normal_text, True, self.colors['text_secondary'])
                normal_rect = normal_surface.get_rect(center=(info_x + info_width // 2, info_y + 55))
                self.screen.blit(normal_surface, normal_rect)
    
    def draw_game_hud(self, score, lives):
        """Draw modern game HUD with score and lives"""
        # HUD background panel
        hud_rect = pygame.Rect(20, 20, 300, 80)
        pygame.draw.rect(self.screen, self.colors['bg_surface'], hud_rect)
        pygame.draw.rect(self.screen, self.colors['border'], hud_rect, 2)
        
        # Score
        score_label = self.fonts['small'].render("SCORE", True, self.colors['text_secondary'])
        score_value = self.fonts['heading'].render(str(score), True, self.colors['secondary'])
        self.screen.blit(score_label, (30, 30))
        self.screen.blit(score_value, (30, 50))
        
        # Lives with heart icons
        lives_label = self.fonts['small'].render("LIVES", True, self.colors['text_secondary'])
        self.screen.blit(lives_label, (150, 30))
        
        # Draw heart icons for lives
        heart_y = 55
        for i in range(3):
            heart_x = 150 + i * 30
            heart_color = self.colors['error'] if i < lives else self.colors['text_muted']
            # Simple heart shape using circles and triangle
            pygame.draw.circle(self.screen, heart_color, (heart_x + 5, heart_y), 8)
            pygame.draw.circle(self.screen, heart_color, (heart_x + 15, heart_y), 8)
            pygame.draw.polygon(self.screen, heart_color, [
                (heart_x, heart_y + 5),
                (heart_x + 20, heart_y + 5),
                (heart_x + 10, heart_y + 15)
            ])
    
    def draw_modern_input_box(self):
        """Draw modern styled input box"""
        # Input box with modern styling
        active_color = self.colors['border_active'] if self.input_active else self.colors['border']
        
        # Background
        pygame.draw.rect(self.screen, self.colors['bg_surface'], self.input_rect)
        pygame.draw.rect(self.screen, active_color, self.input_rect, 3)
        
        # Input text
        if self.input_text:
            text_surface = self.fonts['body'].render(self.input_text, True, self.colors['text_primary'])
        else:
            # Placeholder text
            text_surface = self.fonts['body'].render("Enter country name...", True, self.colors['text_muted'])
        
        # Center text vertically in input box
        text_rect = text_surface.get_rect(centery=self.input_rect.centery, x=self.input_rect.x + 15)
        self.screen.blit(text_surface, text_rect)
        
        # Cursor blink effect when active
        if self.input_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = text_rect.right + 2 if self.input_text else text_rect.x
            cursor_rect = pygame.Rect(cursor_x, text_rect.y, 2, text_rect.height)
            pygame.draw.rect(self.screen, self.colors['text_primary'], cursor_rect)

    def draw_functional_dropdown(self, rect, color, selected_text, gamemodes):
        # Draw main dropdown button
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)  # White border
        
        # Draw arrow
        arrow_x = rect.x + rect.width - 20
        arrow_y = rect.centery
        if self.dropdown_open:
            # Up arrow when open
            pygame.draw.polygon(self.screen, (0, 0, 0), [
                (arrow_x, arrow_y + 5),
                (arrow_x + 10, arrow_y + 5),
                (arrow_x + 5, arrow_y - 5)
            ])
        else:
            # Down arrow when closed
            pygame.draw.polygon(self.screen, (0, 0, 0), [
                (arrow_x, arrow_y - 5),
                (arrow_x + 10, arrow_y - 5),
                (arrow_x + 5, arrow_y + 5)
            ])

        # Draw selected text
        text_surface = self.font.render(selected_text, True, (0, 0, 0))
        self.screen.blit(text_surface, (rect.x + 10, rect.centery - text_surface.get_height() // 2))

        # Draw dropdown options if open
        if self.dropdown_open:
            option_height = 30
            for i, mode in enumerate(gamemodes):
                option_rect = pygame.Rect(rect.x, rect.y + rect.height + (i * option_height), rect.width, option_height)
                
                # Highlight selected option
                if mode.lower() == self.selected_gamemode.lower():
                    pygame.draw.rect(self.screen, (200, 200, 255), option_rect)
                else:
                    pygame.draw.rect(self.screen, (180, 180, 180), option_rect)
                    
                pygame.draw.rect(self.screen, (255, 255, 255), option_rect, 1)  # Border
                
                option_text = self.font.render(mode.upper(), True, (0, 0, 0))
                self.screen.blit(option_text, (option_rect.x + 10, option_rect.centery - option_text.get_height() // 2))
                
                # Store option rect for click detection
                setattr(self, f"dropdown_option_{i}_rect", option_rect)

    def draw_dropdown(self, rect, color, text, dropdown_rect, gamemodes):
        # Keep old method for compatibility but make it call the new one
        self.draw_functional_dropdown(rect, color, text, gamemodes)
    
    def draw_modern_button(self, rect, text, style='primary', hover=False, disabled=False):
        """Draw a modern button with proper styling and states"""
        # Determine colors based on style and state
        if disabled:
            bg_color = self.colors['text_muted']
            text_color = self.colors['bg_main']
            border_color = self.colors['border']
        elif style == 'primary':
            bg_color = self.colors['primary_dark'] if hover else self.colors['primary']
            text_color = self.colors['text_primary']
            border_color = self.colors['primary_dark'] if hover else self.colors['primary']
        elif style == 'success':
            bg_color = self.colors['success_dark'] if hover else self.colors['success']
            text_color = self.colors['text_primary']
            border_color = self.colors['success_dark'] if hover else self.colors['success']
        elif style == 'error':
            bg_color = self.colors['error_dark'] if hover else self.colors['error']
            text_color = self.colors['text_primary']
            border_color = self.colors['error_dark'] if hover else self.colors['error']
        elif style == 'secondary':
            bg_color = self.colors['secondary_dark'] if hover else self.colors['secondary']
            text_color = self.colors['bg_main']
            border_color = self.colors['secondary_dark'] if hover else self.colors['secondary']
        else:  # default/outline style
            bg_color = self.colors['bg_surface'] if not hover else self.colors['bg_card']
            text_color = self.colors['text_primary']
            border_color = self.colors['border_active'] if hover else self.colors['border']
        
        # Draw shadow effect (elevated look)
        if not disabled:
            shadow_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height)
            shadow_surface = pygame.Surface((rect.width, rect.height))
            shadow_surface.set_alpha(30)
            shadow_surface.fill((0, 0, 0))
            self.screen.blit(shadow_surface, shadow_rect)
        
        # Draw main button
        pygame.draw.rect(self.screen, bg_color, rect)
        pygame.draw.rect(self.screen, border_color, rect, 2)
        
        # Add subtle gradient effect for hover
        if hover and not disabled:
            gradient_surface = pygame.Surface((rect.width, rect.height // 2))
            gradient_surface.set_alpha(20)
            gradient_surface.fill((255, 255, 255))
            self.screen.blit(gradient_surface, rect)
        
        # Draw text
        text_surface = self.fonts['body'].render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_button(self, rect, color, text):
        """Legacy button method - redirects to modern button"""
        style = 'primary' if color == (0, 255, 0) else 'error' if color == (255, 0, 0) else 'secondary' if color == (100, 100, 255) else 'default'
        self.draw_modern_button(rect, text, style)

    def showSplashScreen(self):
        import audio  # Import here to avoid circular import
        
        # Set state for animation system
        if self.current_state != "splash":
            self.set_state("splash")
        
        # Modern gradient background
        self.screen.fill(self.colors['bg_main'])
        self.draw_gradient_background()

        # Progressive disclosure - Title animation (appears first)
        title_alpha = self.get_animation_alpha('splash_title')
        if title_alpha > 0:
            title_text = self.fonts['title'].render("FLAG GUESSER", True, self.colors['text_primary'])
            title_surface = title_text.copy()
            title_surface.set_alpha(title_alpha)
            
            # Slide-in effect from top
            title_offset = self.get_animation_offset('splash_title', 50)
            title_rect = title_text.get_rect(center=(self.width // 2, 150 + title_offset))
            
            self.screen.blit(title_surface, title_rect)

        # Progressive disclosure - Subtitle animation (appears second)
        subtitle_alpha = self.get_animation_alpha('splash_subtitle')
        if subtitle_alpha > 0:
            subtitle_text = self.fonts['body'].render("Ultimate Edition", True, self.colors['secondary'])
            subtitle_surface = subtitle_text.copy()
            subtitle_surface.set_alpha(subtitle_alpha)
            
            # Slide-in effect from left
            subtitle_offset = self.get_animation_offset('splash_subtitle', 30)
            subtitle_rect = subtitle_text.get_rect(center=(self.width // 2 + subtitle_offset, 200))
            
            self.screen.blit(subtitle_surface, subtitle_rect)

        # Progressive disclosure - Buttons animation (appears third)
        buttons_alpha = self.get_animation_alpha('splash_buttons')
        if buttons_alpha > 0:
            # Get mouse position for hover effects
            mouse_pos = pygame.mouse.get_pos()

            # Draw main game buttons with animated appearance (keep original positions for functionality)
            play_hover = self.play_button_rect.collidepoint(mouse_pos)
            rankings_hover = self.splash_rankings_button_rect.collidepoint(mouse_pos)
            quit_hover = self.splash_quit_button_rect.collidepoint(mouse_pos)
            
            # Draw buttons with alpha fade-in only (no position offset to maintain functionality)
            self.draw_modern_button_with_alpha(self.play_button_rect, "PLAY", 'success', play_hover, buttons_alpha)
            self.draw_modern_button_with_alpha(self.splash_rankings_button_rect, "RANKINGS", 'primary', rankings_hover, buttons_alpha)
            self.draw_modern_button_with_alpha(self.splash_quit_button_rect, "QUIT", 'error', quit_hover, buttons_alpha)



        # Progressive disclosure - Music controls (appears last)
        music_alpha = self.get_animation_alpha('splash_music')
        if music_alpha > 0:
            # Music controls section with fade-in only (keep positions for functionality)
            music_label = self.fonts['small'].render("Music Controls:", True, self.colors['text_secondary'])
            music_label_surface = music_label.copy()
            music_label_surface.set_alpha(music_alpha)
            music_label_rect = music_label.get_rect(topleft=(self.width - 280, 20))
            self.screen.blit(music_label_surface, music_label_rect)
            
            # Music control buttons with modern styling and alpha (keep original positions)
            mouse_pos = pygame.mouse.get_pos()
            
            play_hover = self.music_play_button_rect.collidepoint(mouse_pos)
            pause_hover = self.music_pause_button_rect.collidepoint(mouse_pos)
            stop_hover = self.music_stop_button_rect.collidepoint(mouse_pos)
            
            # Draw buttons in original positions for functionality with simple text
            self.draw_modern_button_with_alpha(self.music_play_button_rect, "PLAY", 'success', play_hover, music_alpha)
            self.draw_modern_button_with_alpha(self.music_pause_button_rect, "PAUSE", 'secondary', pause_hover, music_alpha)
            self.draw_modern_button_with_alpha(self.music_stop_button_rect, "STOP", 'error', stop_hover, music_alpha)
            
            # Music selection dropdown with alpha
            song_names = ["Random"] + audio.get_song_names()
            
            # Always use the original dropdown, just apply alpha to the whole area if needed
            if music_alpha < 255:
                # Save current state
                temp_pos = pygame.mouse.get_pos()
                # Draw dropdown normally but with modified colors
                self.draw_music_dropdown_with_alpha(self.music_dropdown_rect, (120, 120, 180), self.selected_song, song_names, music_alpha)
            else:
                self.draw_music_dropdown(self.music_dropdown_rect, (120, 120, 180), self.selected_song, song_names)
            
            # Current track display with alpha
            current_track = audio.get_current_song()
            if current_track:
                playing_text = f"♪ Now Playing: {current_track}"
                if len(playing_text) > 35:
                    playing_text = playing_text[:32] + "..."
                playing_surface = self.fonts['caption'].render(playing_text, True, self.colors['success'])
                playing_surface.set_alpha(music_alpha)
                self.screen.blit(playing_surface, (self.music_dropdown_rect.x, self.music_dropdown_rect.y + 35))

        pygame.display.flip()
    
    def draw_gradient_background(self):
        """Draw a subtle gradient background"""
        # Create a vertical gradient from bg_main to slightly lighter
        for y in range(self.height):
            color_ratio = y / self.height
            r = int(self.colors['bg_main'][0] + (self.colors['bg_surface'][0] - self.colors['bg_main'][0]) * color_ratio)
            g = int(self.colors['bg_main'][1] + (self.colors['bg_surface'][1] - self.colors['bg_main'][1]) * color_ratio)
            b = int(self.colors['bg_main'][2] + (self.colors['bg_surface'][2] - self.colors['bg_main'][2]) * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))
    
    def draw_modern_dropdown(self, rect, selected_text, options, dropdown_open=None):
        """Draw a modern dropdown with the new design system"""
        mouse_pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse_pos)
        
        # Use provided dropdown_open state or default to self.dropdown_open
        is_open = dropdown_open if dropdown_open is not None else self.dropdown_open
        
        # Background and border
        bg_color = self.colors['bg_card'] if hover else self.colors['bg_surface']
        border_color = self.colors['border_active'] if is_open else self.colors['border']
        
        pygame.draw.rect(self.screen, bg_color, rect)
        pygame.draw.rect(self.screen, border_color, rect, 2)
        
        # Arrow icon
        arrow_x = rect.x + rect.width - 30
        arrow_y = rect.centery
        arrow_color = self.colors['text_primary']
        
        if is_open:
            # Up arrow
            pygame.draw.polygon(self.screen, arrow_color, [
                (arrow_x, arrow_y + 5),
                (arrow_x + 10, arrow_y + 5),
                (arrow_x + 5, arrow_y - 5)
            ])
        else:
            # Down arrow
            pygame.draw.polygon(self.screen, arrow_color, [
                (arrow_x, arrow_y - 5),
                (arrow_x + 10, arrow_y - 5),
                (arrow_x + 5, arrow_y + 5)
            ])

        # Selected text
        text_surface = self.fonts['body'].render(selected_text, True, self.colors['text_primary'])
        text_rect = text_surface.get_rect(centery=rect.centery, x=rect.x + 15)
        self.screen.blit(text_surface, text_rect)

        # Draw dropdown options if open
        if is_open:
            option_height = 35
            for i, option in enumerate(options):
                option_rect = pygame.Rect(rect.x, rect.y + rect.height + (i * option_height), rect.width, option_height)
                option_hover = option_rect.collidepoint(mouse_pos)
                
                # For mode selection dropdown, use selected_mode_map instead of selected_gamemode
                selected_value = getattr(self, 'selected_mode_map', getattr(self, 'selected_gamemode', ''))
                
                # Highlight selected and hovered options
                if option.lower() == selected_value.lower():
                    option_bg = self.colors['primary']
                    option_text_color = self.colors['text_primary']
                elif option_hover:
                    option_bg = self.colors['bg_card']
                    option_text_color = self.colors['text_primary']
                else:
                    option_bg = self.colors['bg_surface']
                    option_text_color = self.colors['text_secondary']
                    
                pygame.draw.rect(self.screen, option_bg, option_rect)
                pygame.draw.rect(self.screen, self.colors['border'], option_rect, 1)
                
                option_text = self.fonts['body'].render(option.upper(), True, option_text_color)
                option_text_rect = option_text.get_rect(centery=option_rect.centery, x=option_rect.x + 15)
                self.screen.blit(option_text, option_text_rect)
                
                # Store for click detection
                setattr(self, f"dropdown_option_{i}_rect", option_rect)
   
    def showGameOver(self, score, wrong_countries, gamemode):
        # Modern gradient background
        self.screen.fill(self.colors['bg_main'])
        self.draw_gradient_background()
        
        # Game Over main title
        game_over_title = self.fonts['title'].render("GAME OVER", True, self.colors['error'])
        title_rect = game_over_title.get_rect(center=(self.width // 2, 150))
        self.screen.blit(game_over_title, title_rect)
        
        # Score display with modern card
        score_card_rect = pygame.Rect(self.width // 2 - 200, 220, 400, 100)
        
        # Card shadow
        shadow_rect = pygame.Rect(score_card_rect.x + 4, score_card_rect.y + 4, score_card_rect.width, score_card_rect.height)
        shadow_surface = pygame.Surface((score_card_rect.width, score_card_rect.height))
        shadow_surface.set_alpha(40)
        shadow_surface.fill((0, 0, 0))
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Main score card
        pygame.draw.rect(self.screen, self.colors['bg_surface'], score_card_rect)
        pygame.draw.rect(self.screen, self.colors['secondary'], score_card_rect, 3)
        
        # Score content
        final_score_label = self.fonts['small'].render("FINAL SCORE", True, self.colors['text_secondary'])
        final_score_value = self.fonts['title'].render(str(score), True, self.colors['secondary'])
        gamemode_label = self.fonts['small'].render(f"Mode: {gamemode.upper()}", True, self.colors['text_muted'])
        
        label_rect = final_score_label.get_rect(center=(self.width // 2, 240))
        value_rect = final_score_value.get_rect(center=(self.width // 2, 270))
        mode_rect = gamemode_label.get_rect(center=(self.width // 2, 300))
        
        self.screen.blit(final_score_label, label_rect)
        self.screen.blit(final_score_value, value_rect)
        self.screen.blit(gamemode_label, mode_rect)
        
        # Mistakes section (only if there are mistakes)
        if wrong_countries:
            mistakes_y = 350
            mistakes_title = self.fonts['body'].render("Countries you missed:", True, self.colors['text_secondary'])
            mistakes_title_rect = mistakes_title.get_rect(center=(self.width // 2, mistakes_y))
            self.screen.blit(mistakes_title, mistakes_title_rect)
            
            # Display mistakes in a nice format
            mistakes_text = ", ".join(wrong_countries)
            if len(mistakes_text) > 80:
                # Split into multiple lines if too long
                words = wrong_countries
                lines = []
                current_line = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + 2 > 60:  # +2 for ", "
                        if current_line:
                            lines.append(", ".join(current_line))
                            current_line = [word]
                            current_length = len(word)
                        else:
                            lines.append(word)
                    else:
                        current_line.append(word)
                        current_length += len(word) + 2
                
                if current_line:
                    lines.append(", ".join(current_line))
                
                # Display each line
                for i, line in enumerate(lines[:3]):  # Max 3 lines
                    line_text = self.fonts['small'].render(line, True, self.colors['error'])
                    line_rect = line_text.get_rect(center=(self.width // 2, mistakes_y + 35 + i * 25))
                    self.screen.blit(line_text, line_rect)
                    
                if len(lines) > 3:
                    more_text = self.fonts['small'].render(f"... and {len(words) - sum(len(line.split(', ')) for line in lines[:3])} more", True, self.colors['text_muted'])
                    more_rect = more_text.get_rect(center=(self.width // 2, mistakes_y + 35 + 3 * 25))
                    self.screen.blit(more_text, more_rect)
            else:
                mistakes_display = self.fonts['small'].render(mistakes_text, True, self.colors['error'])
                mistakes_rect = mistakes_display.get_rect(center=(self.width // 2, mistakes_y + 35))
                self.screen.blit(mistakes_display, mistakes_rect)
        
        # Action buttons with hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        main_menu_hover = self.main_menu_button_rect.collidepoint(mouse_pos)
        rankings_hover = self.rankings_button_rect.collidepoint(mouse_pos)
        quit_hover = self.quit_button_rect.collidepoint(mouse_pos)
        
        self.draw_modern_button(self.main_menu_button_rect, "MAIN MENU", 'primary', main_menu_hover)
        self.draw_modern_button(self.rankings_button_rect, "SEE RANKINGS", 'secondary', rankings_hover)
        self.draw_modern_button(self.quit_button_rect, "QUIT", 'error', quit_hover)
        
        # Motivational message based on score
        if score >= 20:
            message = "🏆 Excellent! You're a geography master!"
            color = self.colors['success']
        elif score >= 10:
            message = "👏 Great job! Keep practicing!"
            color = self.colors['secondary']
        elif score >= 5:
            message = "📚 Not bad! Room for improvement!"
            color = self.colors['info']
        else:
            message = "💪 Keep trying! Practice makes perfect!"
            color = self.colors['text_secondary']
        
        message_text = self.fonts['small'].render(message, True, color)
        message_rect = message_text.get_rect(center=(self.width // 2, self.height - 100))
        self.screen.blit(message_text, message_rect)

        pygame.display.flip()
        pygame.time.delay(50)
    def showModeSelectionScreen(self):
        # Modern gradient background
        self.screen.fill(self.colors['bg_main'])
        self.draw_gradient_background()
        
        # Title section
        title_text = self.fonts['heading'].render("CHOOSE RANKINGS MODE", True, self.colors['text_primary'])
        subtitle_text = self.fonts['body'].render("Select a game mode to view its rankings", True, self.colors['text_secondary'])
        
        title_rect = title_text.get_rect(center=(self.width // 2, 120))
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 160))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Mode selection buttons with hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Get hover states for all buttons
        mode_buttons = [
            (self.rank_mode_global_button_rect, "GLOBAL", "🌍"),
            (self.rank_mode_europe_button_rect, "EUROPE", "🇪🇺"),
            (self.rank_mode_america_button_rect, "AMERICA", "🌎"),
            (self.rank_mode_asia_button_rect, "ASIA", "🌏"),
            (self.rank_mode_oceania_button_rect, "OCEANIA", "🏝️"),
            (self.rank_mode_africa_button_rect, "AFRICA", "🌍")
        ]
        
        # Draw mode selection cards
        for i, (button_rect, mode_name, icon) in enumerate(mode_buttons):
            hover = button_rect.collidepoint(mouse_pos)
            
            # Card styling with hover effect
            if hover:
                # Shadow effect on hover
                shadow_rect = pygame.Rect(button_rect.x + 2, button_rect.y + 2, button_rect.width, button_rect.height)
                shadow_surface = pygame.Surface((button_rect.width, button_rect.height))
                shadow_surface.set_alpha(50)
                shadow_surface.fill((0, 0, 0))
                self.screen.blit(shadow_surface, shadow_rect)
                
                card_color = self.colors['bg_card']
                border_color = self.colors['primary']
                text_color = self.colors['text_primary']
                border_width = 3
            else:
                card_color = self.colors['bg_surface']
                border_color = self.colors['border']
                text_color = self.colors['text_secondary']
                border_width = 2
            
            # Draw card
            pygame.draw.rect(self.screen, card_color, button_rect)
            pygame.draw.rect(self.screen, border_color, button_rect, border_width)
            
            # Add icon and text
            icon_text = self.fonts['body'].render(icon, True, text_color)
            mode_text = self.fonts['body'].render(mode_name, True, text_color)
            
            # Center icon and text in card
            icon_rect = icon_text.get_rect(center=(button_rect.centerx, button_rect.centery - 15))
            text_rect = mode_text.get_rect(center=(button_rect.centerx, button_rect.centery + 15))
            
            self.screen.blit(icon_text, icon_rect)
            self.screen.blit(mode_text, text_rect)
        
        # Navigation section
        nav_y = self.height - 120
        nav_instruction = self.fonts['small'].render("Click a mode above to view its rankings", True, self.colors['text_muted'])
        nav_rect = nav_instruction.get_rect(center=(self.width // 2, nav_y))
        self.screen.blit(nav_instruction, nav_rect)
        
        # Main Menu button with hover effect
        main_menu_hover = self.rank_mode_main_menu_button_rect.collidepoint(mouse_pos)
        self.draw_modern_button(self.rank_mode_main_menu_button_rect, "MAIN MENU", 'primary', main_menu_hover)

        pygame.display.flip()
    def showRankings(self, scores, gamemode):
        # Modern gradient background
        self.screen.fill(self.colors['bg_main'])
        self.draw_gradient_background()
        
        # Modern title section
        title_text = self.fonts['heading'].render(f"TOP 10 RANKINGS", True, self.colors['text_primary'])
        subtitle_text = self.fonts['body'].render(f"{gamemode.upper()} MODE", True, self.colors['secondary'])
        
        title_rect = title_text.get_rect(center=(self.width // 2, 80))
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 120))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Filter tabs
        mouse_pos = pygame.mouse.get_pos()
        self.draw_ranking_filter_tabs(mouse_pos)
        
        # Rankings content area (adjusted for tabs with more spacing for 1920x1080)
        content_start_y = 280  # More space between tabs and content
        
        if scores and len(scores) > 0:
            # Mode-specific headers
            self.draw_mode_specific_headers(content_start_y)
            
            # Display rankings with modern card styling
            for i, row in enumerate(scores):
                # Handle both old and new database format
                if len(row) >= 9:  # New format with game mode
                    score, timestamp, gamemode_db, game_sequence, mistakes, game_mode, time_taken, flags_shown, mode_data = row
                else:  # Old format
                    score, timestamp, gamemode_db, game_sequence, mistakes = row
                    game_mode = "normal"  # Default for old records
                    time_taken = 0
                    flags_shown = 0
                
                y_pos = content_start_y + 40 + (i * 45)  # +40 for header space
                
                # Ranking card background
                card_rect = pygame.Rect(self.width // 2 - 500, y_pos, 1000, 40)
                
                # Highlight top 3 with special colors
                if i == 0:  # Gold for 1st place
                    card_color = (*self.colors['secondary'], 20)  # Semi-transparent
                    border_color = self.colors['secondary']
                elif i == 1:  # Silver for 2nd place
                    card_color = (*self.colors['text_secondary'], 20)
                    border_color = self.colors['text_secondary']
                elif i == 2:  # Bronze for 3rd place
                    card_color = (*self.colors['warning'], 20)
                    border_color = self.colors['warning']
                else:
                    card_color = self.colors['bg_surface']
                    border_color = self.colors['border']
                
                # Draw card with shadow for top 3
                if i < 3:
                    shadow_rect = pygame.Rect(card_rect.x + 2, card_rect.y + 2, card_rect.width, card_rect.height)
                    shadow_surface = pygame.Surface((card_rect.width, card_rect.height))
                    shadow_surface.set_alpha(30)
                    shadow_surface.fill((0, 0, 0))
                    self.screen.blit(shadow_surface, shadow_rect)
                
                pygame.draw.rect(self.screen, card_color if i >= 3 else self.colors['bg_surface'], card_rect)
                pygame.draw.rect(self.screen, border_color, card_rect, 2 if i < 3 else 1)
                
                # Rank number with special styling for top 3
                rank_font = self.fonts['heading'] if i < 3 else self.fonts['body']
                rank_color = border_color if i < 3 else self.colors['text_primary']
                
                rank_text = rank_font.render(f"#{i + 1}", True, rank_color)
                score_text = self.fonts['body'].render(str(score), True, self.colors['text_primary'])
                
                # Mode-specific data display
                self.draw_mode_specific_data(card_rect, game_mode, score, time_taken, flags_shown, timestamp, mistakes, i + 1)
                
        else:
            # Empty state with nice styling
            empty_card = pygame.Rect(self.width // 2 - 250, content_start_y + 100, 500, 100)
            pygame.draw.rect(self.screen, self.colors['bg_surface'], empty_card)
            pygame.draw.rect(self.screen, self.colors['border'], empty_card, 2)
            
            filter_name = self.selected_rankings_filter.upper()
            no_scores_icon = self.fonts['heading'].render("🏆", True, self.colors['text_muted'])
            no_scores_text = self.fonts['body'].render(f"No {filter_name} games in {gamemode.upper()} yet!", True, self.colors['text_secondary'])
            play_suggestion = self.fonts['small'].render("Start playing to see your scores here!", True, self.colors['text_muted'])
            
            icon_rect = no_scores_icon.get_rect(center=(self.width // 2, content_start_y + 125))
            text_rect = no_scores_text.get_rect(center=(self.width // 2, content_start_y + 155))
            suggestion_rect = play_suggestion.get_rect(center=(self.width // 2, content_start_y + 175))
            
            self.screen.blit(no_scores_icon, icon_rect)
            self.screen.blit(no_scores_text, text_rect)
            self.screen.blit(play_suggestion, suggestion_rect)
        
        # Modern navigation buttons
        back_hover = self.rankings_back_button_rect.collidepoint(mouse_pos)
        menu_hover = self.rank_sel_main_menu_button_rect.collidepoint(mouse_pos)
        
        self.draw_modern_button(self.rankings_back_button_rect, "BACK", 'secondary', back_hover)
        self.draw_modern_button(self.rank_sel_main_menu_button_rect, "MAIN MENU", 'primary', menu_hover)
        
        pygame.display.flip()
        pygame.time.delay(50)
    
    def draw_mode_specific_headers(self, content_start_y):
        """Draw headers based on selected ranking filter"""
        header_rect = pygame.Rect(self.width // 2 - 500, content_start_y - 30, 1000, 25)
        pygame.draw.rect(self.screen, self.colors['bg_surface'], header_rect)
        pygame.draw.rect(self.screen, self.colors['border'], header_rect, 1)
        
        # Common headers
        rank_header = self.fonts['small'].render("RANK", True, self.colors['text_secondary'])
        score_header = self.fonts['small'].render("SCORE", True, self.colors['text_secondary'])
        
        self.screen.blit(rank_header, (self.width // 2 - 480, content_start_y - 25))
        self.screen.blit(score_header, (self.width // 2 - 400, content_start_y - 25))
        
        # Mode-specific headers
        if self.selected_rankings_filter == "blitz":
            time_header = self.fonts['small'].render("TIME", True, self.colors['text_secondary'])
            rate_header = self.fonts['small'].render("FLAGS/SEC", True, self.colors['text_secondary'])
            date_header = self.fonts['small'].render("DATE", True, self.colors['text_secondary'])
            
            self.screen.blit(time_header, (self.width // 2 - 300, content_start_y - 25))
            self.screen.blit(rate_header, (self.width // 2 - 180, content_start_y - 25))
            self.screen.blit(date_header, (self.width // 2 - 50, content_start_y - 25))
            
        elif self.selected_rankings_filter == "endless":
            flags_header = self.fonts['small'].render("FLAGS", True, self.colors['text_secondary'])
            rate_header = self.fonts['small'].render("AVG/LIFE", True, self.colors['text_secondary'])
            date_header = self.fonts['small'].render("DATE", True, self.colors['text_secondary'])
            
            self.screen.blit(flags_header, (self.width // 2 - 300, content_start_y - 25))
            self.screen.blit(rate_header, (self.width // 2 - 180, content_start_y - 25))
            self.screen.blit(date_header, (self.width // 2 - 50, content_start_y - 25))
            
        elif self.selected_rankings_filter == "normal":
            completion_header = self.fonts['small'].render("COMPLETION", True, self.colors['text_secondary'])
            accuracy_header = self.fonts['small'].render("ACCURACY", True, self.colors['text_secondary'])
            date_header = self.fonts['small'].render("DATE", True, self.colors['text_secondary'])
            
            self.screen.blit(completion_header, (self.width // 2 - 300, content_start_y - 25))
            self.screen.blit(accuracy_header, (self.width // 2 - 180, content_start_y - 25))
            self.screen.blit(date_header, (self.width // 2 - 50, content_start_y - 25))
            
        else:  # "all" filter
            mode_header = self.fonts['small'].render("MODE", True, self.colors['text_secondary'])
            stat_header = self.fonts['small'].render("STAT", True, self.colors['text_secondary'])
            date_header = self.fonts['small'].render("DATE", True, self.colors['text_secondary'])
            
            self.screen.blit(mode_header, (self.width // 2 - 300, content_start_y - 25))
            self.screen.blit(stat_header, (self.width // 2 - 180, content_start_y - 25))
            self.screen.blit(date_header, (self.width // 2 - 50, content_start_y - 25))
    
    def draw_mode_specific_data(self, card_rect, game_mode, score, time_taken, flags_shown, timestamp, mistakes, rank):
        """Draw mode-specific data in ranking rows"""
        text_y = card_rect.y + 12
        
        # Common data
        rank_text = self.fonts['body'].render(f"#{rank}", True, self.colors['text_primary'])
        score_text = self.fonts['body'].render(str(score), True, self.colors['text_primary'])
        
        self.screen.blit(rank_text, (self.width // 2 - 480, text_y))
        self.screen.blit(score_text, (self.width // 2 - 400, text_y))
        
        # Format date
        try:
            from datetime import datetime
            date_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            formatted_date = date_obj.strftime('%d/%m')
        except:
            formatted_date = timestamp[:5]
        
        date_text = self.fonts['small'].render(formatted_date, True, self.colors['text_secondary'])
        
        # Mode-specific data
        if self.selected_rankings_filter == "blitz":
            time_display = f"{time_taken}s" if time_taken > 0 else "N/A"
            flags_per_sec = f"{score/max(time_taken, 1):.1f}" if time_taken > 0 else "N/A"
            
            time_text = self.fonts['small'].render(time_display, True, self.colors['text_secondary'])
            rate_text = self.fonts['small'].render(flags_per_sec, True, self.colors['secondary'])
            
            self.screen.blit(time_text, (self.width // 2 - 300, text_y))
            self.screen.blit(rate_text, (self.width // 2 - 180, text_y))
            self.screen.blit(date_text, (self.width // 2 - 50, text_y))
            
        elif self.selected_rankings_filter == "endless":
            flags_display = str(flags_shown) if flags_shown > 0 else "N/A"
            avg_per_life = f"{flags_shown/3:.1f}" if flags_shown > 0 else "N/A"
            
            flags_text = self.fonts['small'].render(flags_display, True, self.colors['text_secondary'])
            avg_text = self.fonts['small'].render(avg_per_life, True, self.colors['secondary'])
            
            self.screen.blit(flags_text, (self.width // 2 - 300, text_y))
            self.screen.blit(avg_text, (self.width // 2 - 180, text_y))
            self.screen.blit(date_text, (self.width // 2 - 50, text_y))
            
        elif self.selected_rankings_filter == "normal":
            # Calculate completion and accuracy for normal mode
            total_mistakes = len(mistakes.split(',')) if mistakes else 0
            total_attempted = score + total_mistakes
            completion = f"{score}/{total_attempted}" if total_attempted > 0 else "N/A"
            accuracy = f"{(score/total_attempted*100):.0f}%" if total_attempted > 0 else "N/A"
            
            completion_text = self.fonts['small'].render(completion, True, self.colors['text_secondary'])
            accuracy_text = self.fonts['small'].render(accuracy, True, self.colors['secondary'])
            
            self.screen.blit(completion_text, (self.width // 2 - 300, text_y))
            self.screen.blit(accuracy_text, (self.width // 2 - 180, text_y))
            self.screen.blit(date_text, (self.width // 2 - 50, text_y))
            
        else:  # "all" filter
            # Show mode icon and a relevant stat
            mode_icons = {"normal": "🎯", "endless": "♾️", "blitz": "⚡"}
            mode_icon = mode_icons.get(game_mode, "🎮")
            mode_display = f"{mode_icon} {game_mode.upper()}"
            
            if game_mode == "blitz":
                stat_display = f"{score/max(time_taken, 1):.1f}/s" if time_taken > 0 else "N/A"
            elif game_mode == "endless":
                stat_display = f"{flags_shown} flags" if flags_shown > 0 else "N/A"
            else:  # normal
                total_mistakes = len(mistakes.split(',')) if mistakes else 0
                total_attempted = score + total_mistakes
                stat_display = f"{(score/total_attempted*100):.0f}%" if total_attempted > 0 else "N/A"
            
            mode_text = self.fonts['small'].render(mode_display, True, self.colors['text_secondary'])
            stat_text = self.fonts['small'].render(stat_display, True, self.colors['secondary'])
            
            self.screen.blit(mode_text, (self.width // 2 - 300, text_y))
            self.screen.blit(stat_text, (self.width // 2 - 180, text_y))
            self.screen.blit(date_text, (self.width // 2 - 50, text_y))

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
    def get_game_exit_button_rect(self):
        return self.game_exit_button_rect
    
    def show_error_message(self, message):
        """Show error message overlay (non-blocking)"""
        self.error_message['active'] = True
        self.error_message['text'] = message
        self.error_message['start_time'] = pygame.time.get_ticks()
    
    def clear_error_message(self):
        """Clear error message"""
        self.error_message['active'] = False
        self.error_message['text'] = ''
    
    def update_error_message(self):
        """Update error message state and return True if expired"""
        if self.error_message['active']:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.error_message['start_time']
            if elapsed >= self.error_message['duration']:
                self.error_message['active'] = False
                return True
        return False
    
    def draw_error_message_overlay(self):
        """Draw simple error message over the flag area"""
        if not self.error_message['active']:
            return
        
        # Calculate fade effect
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.error_message['start_time']
        duration = self.error_message['duration']
        
        # Fade in first 500ms, stay solid for middle time, fade out last 500ms
        if elapsed < 500:
            alpha = int(255 * (elapsed / 500))
        elif elapsed > duration - 500:
            alpha = int(255 * ((duration - elapsed) / 500))
        else:
            alpha = 255
        
        # Create message box
        message_text = self.error_message['text']
        text_surface = self.fonts['body'].render(message_text, True, self.colors['error'])
        text_rect = text_surface.get_rect()
        
        # Position above flag area
        box_width = max(300, text_rect.width + 40)
        box_height = 60
        box_x = (self.width - box_width) // 2
        box_y = (self.height // 2) - 200  # Above flag
        
        # Create semi-transparent background
        error_surface = pygame.Surface((box_width, box_height))
        error_surface.set_alpha(alpha)
        error_surface.fill(self.colors['bg_card'])
        
        # Draw box with border
        pygame.draw.rect(error_surface, self.colors['error'], (0, 0, box_width, box_height), 3)
        
        # Center text in box
        text_x = (box_width - text_rect.width) // 2
        text_y = (box_height - text_rect.height) // 2
        
        # Apply alpha to text
        text_with_alpha = text_surface.copy()
        text_with_alpha.set_alpha(alpha)
        error_surface.blit(text_with_alpha, (text_x, text_y))
        
        # Draw to screen
        self.screen.blit(error_surface, (box_x, box_y))
    
    def showModeSelection(self, gamemodes):
        """Display the completely redesigned game mode selection screen"""
        # Modern gradient background
        self.screen.fill(self.colors['bg_main'])
        self.draw_gradient_background()
        
        # Main title section
        title_text = self.fonts['title'].render("SELECT GAME MODE", True, self.colors['text_primary'])
        title_rect = title_text.get_rect(center=(self.width // 2, 120))
        self.screen.blit(title_text, title_rect)
        
        # Map selection section - new button-based design
        map_label = self.fonts['body'].render("Map:", True, self.colors['text_secondary'])
        map_label_rect = map_label.get_rect(center=(self.width - 150, 50))
        self.screen.blit(map_label, map_label_rect)
        
        # Map buttons (replace dropdown with clean buttons)
        mouse_pos = pygame.mouse.get_pos()
        maps = [
            {"name": "GLOBAL", "rect": self.map_global_rect, "id": "global"},
            {"name": "EUROPE", "rect": self.map_europe_rect, "id": "europe"},
            {"name": "ASIA", "rect": self.map_asia_rect, "id": "asia"},
            {"name": "AMERICA", "rect": self.map_america_rect, "id": "america"},
            {"name": "AFRICA", "rect": self.map_africa_rect, "id": "africa"},
            {"name": "OCEANIA", "rect": self.map_oceania_rect, "id": "oceania"}
        ]
        
        for map_item in maps:
            rect = map_item["rect"]
            hover = rect.collidepoint(mouse_pos)
            selected = map_item["id"] == self.selected_mode_map
            
            # Button styling
            if selected:
                self.draw_modern_button(rect, map_item["name"], 'primary', hover)
            else:
                self.draw_modern_button(rect, map_item["name"], 'secondary', hover)
        
        # Mode cards - enhanced modern design
        modes = [
            {
                'name': 'NORMAL',
                'icon': '🎯',
                'title': 'Classic Challenge',
                'description': 'Complete all flags\nfrom selected map',
                'rect': self.mode_normal_button_rect,
                'mode_id': 'normal',
                'color': (52, 152, 219)  # Blue
            },
            {
                'name': 'ENDLESS',
                'icon': '♾️',
                'title': 'Infinite Challenge', 
                'description': 'Play until you lose\nall 3 lives',
                'rect': self.mode_endless_button_rect,
                'mode_id': 'endless',
                'color': (155, 89, 182)  # Purple
            },
            {
                'name': 'BLITZ',
                'icon': '⚡',
                'title': 'Speed Challenge',
                'description': 'Maximum flags\nin 60 seconds',
                'rect': self.mode_blitz_button_rect,
                'mode_id': 'blitz',
                'color': (231, 76, 60)  # Red
            }
        ]
        
        # Draw enhanced mode cards
        for mode in modes:
            rect = mode['rect']
            hover = rect.collidepoint(mouse_pos)
            
            # Enhanced card styling with accent colors
            if hover:
                # Hover glow effect
                glow_rect = pygame.Rect(rect.x - 8, rect.y - 8, rect.width + 16, rect.height + 16)
                glow_surface = pygame.Surface((rect.width + 16, rect.height + 16))
                glow_surface.set_alpha(40)
                glow_surface.fill(mode['color'])
                self.screen.blit(glow_surface, glow_rect)
                
                card_color = (*mode['color'], 40)  # Semi-transparent accent
                border_color = mode['color']
                text_color = self.colors['text_primary']
                icon_color = mode['color']
                border_width = 4
            else:
                card_color = self.colors['bg_surface']
                border_color = self.colors['border']
                text_color = self.colors['text_secondary']
                icon_color = text_color
                border_width = 2
            
            # Draw main card with gradient-like effect
            pygame.draw.rect(self.screen, card_color if not hover else self.colors['bg_surface'], rect)
            if hover:
                # Accent border on top
                top_border = pygame.Rect(rect.x, rect.y, rect.width, 6)
                pygame.draw.rect(self.screen, mode['color'], top_border)
            pygame.draw.rect(self.screen, border_color, rect, border_width)
            
            # Large icon with enhanced styling
            icon_text = self.fonts['title'].render(mode['icon'], True, icon_color)
            icon_rect = icon_text.get_rect(center=(rect.centerx, rect.y + 70))
            self.screen.blit(icon_text, icon_rect)
            
            # Title with better typography
            title_text = self.fonts['heading'].render(mode['title'], True, text_color)
            title_rect = title_text.get_rect(center=(rect.centerx, rect.y + 140))
            self.screen.blit(title_text, title_rect)
            
            # Description with improved spacing
            desc_lines = mode['description'].split('\n')
            for i, line in enumerate(desc_lines):
                desc_text = self.fonts['body'].render(line, True, text_color)
                desc_rect = desc_text.get_rect(center=(rect.centerx, rect.y + 180 + i * 25))
                self.screen.blit(desc_text, desc_rect)
        
        # Navigation buttons
        back_hover = self.mode_back_button_rect.collidepoint(mouse_pos)
        self.draw_modern_button(self.mode_back_button_rect, "BACK TO MENU", 'secondary', back_hover)
        
        pygame.display.flip()
    
    def handle_mode_selection_click(self, mouse_pos):
        """Handle clicks on the mode selection screen"""
        # Check mode card clicks
        if self.mode_normal_button_rect.collidepoint(mouse_pos):
            self.selected_mode = "normal"
            return ("normal", self.selected_mode_map)
        elif self.mode_endless_button_rect.collidepoint(mouse_pos):
            self.selected_mode = "endless"
            return ("endless", self.selected_mode_map)
        elif self.mode_blitz_button_rect.collidepoint(mouse_pos):
            self.selected_mode = "blitz"
            return ("blitz", self.selected_mode_map)
        
        # Check map button clicks (replace dropdown system)
        map_buttons = [
            (self.map_global_rect, "global"),
            (self.map_europe_rect, "europe"),
            (self.map_asia_rect, "asia"),
            (self.map_america_rect, "america"),
            (self.map_africa_rect, "africa"),
            (self.map_oceania_rect, "oceania")
        ]
        
        for rect, map_id in map_buttons:
            if rect.collidepoint(mouse_pos):
                self.selected_mode_map = map_id
                return None
        
        # Check back button
        if self.mode_back_button_rect.collidepoint(mouse_pos):
            return "back"
        

        
        return None
    
    def draw_ranking_filter_tabs(self, mouse_pos):
        """Draw filter tabs for rankings (All/Normal/Endless/Blitz)"""
        tabs = [
            {"name": "ALL", "filter": "all", "rect": self.rank_filter_all_rect, "icon": "🏆"},
            {"name": "NORMAL", "filter": "normal", "rect": self.rank_filter_normal_rect, "icon": "🎯"},
            {"name": "ENDLESS", "filter": "endless", "rect": self.rank_filter_endless_rect, "icon": "♾️"},
            {"name": "BLITZ", "filter": "blitz", "rect": self.rank_filter_blitz_rect, "icon": "⚡"}
        ]
        
        for tab in tabs:
            rect = tab["rect"]
            hover = rect.collidepoint(mouse_pos)
            selected = tab["filter"] == self.selected_rankings_filter
            
            # Tab styling
            if selected:
                bg_color = self.colors['primary']
                text_color = self.colors['text_primary']
                border_color = self.colors['primary_dark']
                border_width = 3
            elif hover:
                bg_color = self.colors['bg_card']
                text_color = self.colors['text_primary']
                border_color = self.colors['primary']
                border_width = 2
            else:
                bg_color = self.colors['bg_surface']
                text_color = self.colors['text_secondary']
                border_color = self.colors['border']
                border_width = 1
            
            # Draw tab background
            pygame.draw.rect(self.screen, bg_color, rect)
            pygame.draw.rect(self.screen, border_color, rect, border_width)
            
            # Tab content - optimized for 180x60 tabs in 1920x1080
            if selected or hover:
                # Show icon + text for active/hover with better spacing
                icon_text = self.fonts['body'].render(tab["icon"], True, text_color)
                name_text = self.fonts['small'].render(tab["name"], True, text_color)
                
                icon_rect = icon_text.get_rect(center=(rect.centerx, rect.y + 22))
                name_rect = name_text.get_rect(center=(rect.centerx, rect.y + 42))
                
                self.screen.blit(icon_text, icon_rect)
                self.screen.blit(name_text, name_rect)
            else:
                # Show icon + text for inactive tabs too (larger tabs can fit both)
                icon_text = self.fonts['small'].render(tab["icon"], True, text_color)
                name_text = self.fonts['caption'].render(tab["name"], True, text_color)
                
                icon_rect = icon_text.get_rect(center=(rect.centerx, rect.y + 22))
                name_rect = name_text.get_rect(center=(rect.centerx, rect.y + 42))
                
                self.screen.blit(icon_text, icon_rect)
                self.screen.blit(name_text, name_rect)
    
    def handle_ranking_filter_click(self, mouse_pos):
        """Handle clicks on ranking filter tabs"""
        if self.rank_filter_all_rect.collidepoint(mouse_pos):
            self.selected_rankings_filter = "all"
            return True
        elif self.rank_filter_normal_rect.collidepoint(mouse_pos):
            self.selected_rankings_filter = "normal"
            return True
        elif self.rank_filter_endless_rect.collidepoint(mouse_pos):
            self.selected_rankings_filter = "endless"
            return True
        elif self.rank_filter_blitz_rect.collidepoint(mouse_pos):
            self.selected_rankings_filter = "blitz"
            return True
        return False
    
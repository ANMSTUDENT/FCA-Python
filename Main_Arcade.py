import pygame
import sys
import time
import random
import math

# --- Global Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
SHELL_GAME_UNLOCK_SCORE = 500
PLAY_AREA_MARGIN = 50

# --- Colors (Standardized Carnival Palette for Visual Richness) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (80, 80, 80) 

# Carnival Palette (Unified Naming)
CARNIVAL_RED = (200, 50, 50)     # Main red color (Dart Pop BG, Menu Stripe)
CARNIVAL_YELLOW = (255, 215, 0)  # Main gold/yellow color (Menu Title, Menu Stripe)
HOOP_BLUE = (0, 150, 255)        # Bright Blue
SPLASH_GREEN = (50, 200, 50)     # Bright Green
UI_BRIGHT_YELLOW = (255, 255, 0) # Bright Yellow for Aimer/Score UI
MENU_DARK_BLUE = (10, 10, 40)    # Base background color for deep contrast

# Other specific colors needed for visual elements
OG_ORANGE = (255, 140, 0) # Basketball color
OG_BROWN = (139, 69, 19)  # Shell Game Table
OG_WATER_CYAN = (100, 200, 255) # Splash Water

# --- Game State Definitions ---
STATE_MENU = 0
STATE_DARTPOP = 1
STATE_HOOPSHOT = 2
STATE_SPLASH = 3
STATE_SHELLGAME = 4
STATE_PRIZES = 5
STATE_STATS = 6

# --- Game-Specific Constants ---
# Clown Splash
HIT_SCORE_INTERVAL = 0.5
MAX_SWING_ANGLE = math.pi / 4.5
SWING_SPEED = 1.0
STREAM_LENGTH = 450

# Shell Game
SHUFFLE_EVENT = pygame.USEREVENT + 1
SHUFFLE_DURATION_MS = 500
INITIAL_REVEAL_DURATION_MS = 1500

# --- Prize Data (Simplified for display) ---
PRIZES = [
    {"name": "Teddy Bear", "cost": 500, "icon": "🧸"},
    {"name": "Mini Robot", "cost": 1500, "icon": "🤖"},
    {"name": "Giant Lollipop", "cost": 2500, "icon": "🍭"},
    {"name": "VR Headset", "cost": 5000, "icon": "👓"},
    {"name": "Electric Scooter", "cost": 10000, "icon": "🛴"},
    {"name": "New Car", "cost": 50000, "icon": "🚗"},
]

# --- Utility Functions ---
def draw_button(surface, text, rect, color, text_color, font, locked=False):
    """A helper function to draw standardized, carnival-style buttons."""
    # Base button color (lighter/darker if locked)
    base_color = DARK_GRAY if locked else color
    
    # Draw button background with rounded corners
    pygame.draw.rect(surface, base_color, rect, 0, border_radius=15)
    
    # Draw a carnival-style border (gold if not locked)
    border_color = CARNIVAL_YELLOW if not locked else BLACK
    pygame.draw.rect(surface, border_color, rect, 3, border_radius=15)

    # Text rendering
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


# --- Pygame Initialization ---
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Jay's Carnival Arcade")

# --- Audio Simulation (No actual files loaded) ---
class SoundManager:
    """Manages simulated audio output via print statements."""
    def __init__(self):
        self.is_spraying = False

    def play_background_music(self):
        # print("AUDIO: (Simulated) Playing looping carnival music.")
        pass

    def play_pop(self):
        print("AUDIO: POP!")

    def play_swish_cheer(self):
        print("AUDIO: SWISH! CHEER!")
    
    def play_fanfare(self):
        print("AUDIO: Congratulations Fanfare!")

    def play_water_spray(self, start=True):
        if start and not self.is_spraying:
            self.is_spraying = True
            # print("AUDIO: WHOOOSH (Spray Start/Loop)")
        elif not start and self.is_spraying:
            self.is_spraying = False
            # print("AUDIO: (Spray Stop)")

    def play_clown_honk(self):
        print("AUDIO: HONK!")

# ------------------------------------------------------------------------------
# 5. PRIZE SCREEN
# ------------------------------------------------------------------------------

class PrizeScreen:
    def __init__(self, screen, font, sound_manager):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager
        self.small_font = pygame.font.Font(None, 24)
        self.prize_font = pygame.font.Font(None, 40)
        
        self.reset()
        
    def reset(self):
        pass

    def handle_input(self, event):
        return 0

    def update(self, dt):
        return 0

    def draw(self, total_score): # Requires total_score
        # Background: Deep Blue for contrast
        self.screen.fill(MENU_DARK_BLUE) 

        # Title: Gold Text
        title_surf = self.font.render("CARNIVAL PRIZE CENTER", True, CARNIVAL_YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_surf, title_rect)
        
        # Current Score Readout: Bright Yellow
        score_surf = self.prize_font.render(f"YOUR SCORE: {total_score}", True, UI_BRIGHT_YELLOW)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 110))
        self.screen.blit(score_surf, score_rect)

        y_start = 180
        item_height = 60
        
        for i, prize in enumerate(PRIZES):
            y_pos = y_start + i * (item_height + 10)
            is_unlocked = total_score >= prize['cost']
            
            # Use the center width for the prize area
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 350, y_pos, 700, item_height)
            
            # Background element for the prize row
            bg_color = DARK_GRAY if not is_unlocked else (30, 30, 30)
            pygame.draw.rect(self.screen, bg_color, rect, 0, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)

            # 1. Prize Icon
            try:
                # Emojis/Symbols might not render perfectly depending on the Pygame font
                icon_surf = self.prize_font.render(prize['icon'], True, WHITE)
            except Exception:
                icon_surf = self.prize_font.render("?", True, WHITE) # Fallback
            self.screen.blit(icon_surf, (rect.left + 20, rect.centery - icon_surf.get_height() // 2))

            # 2. Prize Name
            name_color = WHITE if is_unlocked else DARK_GRAY
            name_surf = self.prize_font.render(prize['name'], True, name_color)
            self.screen.blit(name_surf, (rect.left + 80, rect.centery - name_surf.get_height() // 2))

            # 3. Unlock Indicator (Small Title)
            if is_unlocked:
                unlocked_surf = self.small_font.render("UNLOCKED!", True, SPLASH_GREEN) # Bright Green for visual "Win"
                self.screen.blit(unlocked_surf, (rect.left + 80 + name_surf.get_width() + 10, rect.centery - unlocked_surf.get_height() // 2))
                
            # 4. Cost/Requirement
            cost_color = UI_BRIGHT_YELLOW if is_unlocked else CARNIVAL_RED
            cost_text = "CLAIMED" if is_unlocked else f"{prize['cost']} Points"
            cost_surf = self.prize_font.render(cost_text, True, cost_color)
            self.screen.blit(cost_surf, (rect.right - cost_surf.get_width() - 20, rect.centery - cost_surf.get_height() // 2))
            
        # Instruction text at the bottom
        inst_surf = self.small_font.render("Press ESC to return to the Main Menu.", True, DARK_GRAY)
        self.screen.blit(inst_surf, (SCREEN_WIDTH // 2 - inst_surf.get_width() // 2, SCREEN_HEIGHT - 30))

    def cleanup(self):
        pass

# ------------------------------------------------------------------------------
# 1. DART POP GAME 
# ------------------------------------------------------------------------------

class DartPopGame:
    def __init__(self, screen, font, sound_manager):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager
        
        # Define the centralized Black Play Area
        self.PLAY_AREA_RECT = pygame.Rect(
            PLAY_AREA_MARGIN, PLAY_AREA_MARGIN, 
            SCREEN_WIDTH - 2 * PLAY_AREA_MARGIN, 
            SCREEN_HEIGHT - 2 * PLAY_AREA_MARGIN
        )
        self.center_x = self.PLAY_AREA_RECT.centerx
        self.center_y = self.PLAY_AREA_RECT.centery
        
        # Dart Pop specific constants, relative to the play area
        self.target_radius = self.PLAY_AREA_RECT.width // 2 * 0.7 
        self.arm_length = self.target_radius * 0.75
        self.target_angle = 3 * math.pi / 2
        self.hit_angle_min = self.target_angle - 0.26
        self.hit_angle_max = self.target_angle + 0.26
        
        self.reset()
        self.message = "Press SPACE to throw the dart!"

    def generate_balloons(self):
        self.balloons = []
        balloon_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        color = HOOP_BLUE 
        for angle in balloon_angles:
            x = self.center_x + self.arm_length * math.cos(angle)
            y = self.center_y + self.arm_length * math.sin(angle)
            size = random.randint(18, 25)
            self.balloons.append({'pos': (int(x), int(y)), 'size': size, 'color': color, 'hit': False})

    def reset(self):
        self.game_time = 0.0
        self.dart_thrown = False
        self.hit_result = None
        self.bullseye_radius = 20
        self.rotation_speed = 1.5 * random.choice([1, -1])
        self.generate_balloons()
        self.message = "Press SPACE to throw the dart!"

    def handle_input(self, event):
        score_to_report = 0
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not self.dart_thrown:
                self.dart_thrown = True
                angle = self.game_time * self.rotation_speed
                dart_x = self.center_x + self.arm_length * math.cos(angle)
                dart_y = self.center_y + self.arm_length * math.sin(angle)
                normalized_angle = angle % (2 * math.pi)
                hit_balloon = False
                hit_score = 0
                
                # Check balloon hits
                for balloon in self.balloons:
                    if not balloon['hit']:
                        dist = math.hypot(dart_x - balloon['pos'][0], dart_y - balloon['pos'][1])
                        if dist < balloon['size']:
                            balloon['hit'] = True
                            hit_balloon = True
                            hit_score += 100
                            self.sound_manager.play_pop()
                            
                if hit_balloon:
                    self.hit_result = 'HIT'
                    score_to_report = hit_score
                    self.message = f"POP! +{score_to_report} Points! (Press R to Reset/Continue)"
                else:
                    # Check near miss on bullseye (for extra points)
                    if (self.hit_angle_min < normalized_angle < self.hit_angle_max) or \
                       (self.hit_angle_min < normalized_angle - 2 * math.pi < self.hit_angle_max):
                        self.hit_result = 'NEAR_MISS'
                        score_to_report = 50
                        self.message = f"Good Timing! +{score_to_report} Points! (Press R to Reset/Continue)"
                    else:
                        self.hit_result = 'MISS'
                        score_to_report = 0
                        self.message = "MISS! (Press R to Reset/Continue)"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if self.dart_thrown:
                self.reset()
        return score_to_report

    def update(self, dt):
        if not self.dart_thrown:
            self.game_time += dt
        return 0

    def draw(self): # Does not require total_score
        # 1. Background: Carnival Red
        self.screen.fill(CARNIVAL_RED) 
        
        # 2. Target Area: Large Black Rectangle
        pygame.draw.rect(self.screen, BLACK, self.PLAY_AREA_RECT)

        # Draw the target within the play area
        pygame.draw.circle(self.screen, DARK_GRAY, (self.center_x, self.center_y), self.target_radius + 50, 0)
        pygame.draw.circle(self.screen, CARNIVAL_RED, (self.center_x, self.center_y), self.target_radius, 0)
        pygame.draw.circle(self.screen, SPLASH_GREEN, (self.center_x, self.center_y), self.target_radius * 0.5)
        pygame.draw.circle(self.screen, WHITE, (self.center_x, self.center_y), self.bullseye_radius)
        
        # Draw balloons
        for balloon in self.balloons:
            if balloon['hit']:
                # Popped balloon visualization (looks like a deflated ring)
                pygame.draw.circle(self.screen, BLACK, balloon['pos'], balloon['size'] + 3)
                pygame.draw.circle(self.screen, CARNIVAL_RED, balloon['pos'], balloon['size'] - 5)
            else:
                pygame.draw.circle(self.screen, HOOP_BLUE, balloon['pos'], balloon['size'])

        angle = self.game_time * self.rotation_speed
        end_x = self.center_x + self.arm_length * math.cos(angle)
        end_y = self.center_y + self.arm_length * math.sin(angle)
        
        # Aimer/Reticle: Bright Yellow crosshairs
        if not self.dart_thrown:
            pygame.draw.line(self.screen, UI_BRIGHT_YELLOW, (self.center_x, self.center_y), (end_x, end_y), 3)
            # Draw crosshair circle
            pygame.draw.circle(self.screen, UI_BRIGHT_YELLOW, (int(end_x), int(end_y)), 8)
        
        if self.dart_thrown:
            dart_x = self.center_x + self.arm_length * math.cos(angle)
            dart_y = self.center_y + self.arm_length * math.sin(angle)
            color = SPLASH_GREEN if self.hit_result != 'MISS' else CARNIVAL_RED
            pygame.draw.circle(self.screen, color, (int(dart_x), int(dart_y)), 12)
            
        self._draw_message()
        
    def _draw_message(self):
        # Message is drawn over the Red background for high contrast
        text_surf = self.font.render(self.message, True, UI_BRIGHT_YELLOW) 
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, self.PLAY_AREA_RECT.bottom + 20))
        self.screen.blit(text_surf, text_rect)

    def cleanup(self):
        pass


# ------------------------------------------------------------------------------
# 2. HOOP SHOT GAME 
# ------------------------------------------------------------------------------

class SwayObject(pygame.sprite.Sprite):
    """Represents the moving power meter indicator in the Hoop Shot game."""
    def __init__(self, center_x, center_y, amplitude, frequency, pattern, color=CARNIVAL_RED, size=20): 
        super().__init__()
        self.size = size
        self.image = pygame.Surface([size * 10, size], pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect(center=(center_x, center_y))
        self.start_x = center_x
        self.start_y = center_y
        self.amplitude = amplitude
        self.frequency = frequency
        self.pattern = pattern
        self.color = color
        self.time_offset = pygame.time.get_ticks()

    def update(self):
        elapsed_time = pygame.time.get_ticks() - self.time_offset
        time_s = elapsed_time / 1000.0
        angle = time_s * self.frequency * 2 * math.pi
        y_offset = 0

        if self.pattern == 1:
            y_offset = math.sin(angle) * self.amplitude
            
        self.rect.center = (self.start_x, self.start_y + y_offset)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, self.color, (self.size * 5, self.size // 2), self.size // 2)
        return y_offset

class Basketball(pygame.sprite.Sprite):
    """Represents the thrown basketball."""
    def __init__(self, start_x, start_y, arc_type):
        super().__init__()
        self.size = 40
        self.image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, OG_ORANGE, (self.size // 2, self.size // 2), self.size // 2)

        self.rect = self.image.get_rect(center=(start_x, start_y))
        
        self.start_time = pygame.time.get_ticks()
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = SCREEN_WIDTH - PLAY_AREA_MARGIN - 100
        self.target_y = SCREEN_HEIGHT // 2
        self.gravity = 1500.0
        
        # Trajectory parameters based on hit type
        if arc_type == 'swish':
            self.duration = 0.9
            self.initial_vy = -800.0
        elif arc_type == 'overshoot':
            self.duration = 1.0
            self.initial_vy = -1050.0
        elif arc_type == 'undershoot':
            self.duration = 0.7
            self.initial_vy = -500.0
        else:
            self.duration = 1.0
            self.initial_vy = -650.0 # Default miss arc
            
        self.vx = (self.target_x - self.start_x) / self.duration
        self.in_flight = True

    def update(self):
        if not self.in_flight:
            return
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000.0
        
        # Self-destruct after trajectory finishes
        if elapsed_time > self.duration * 1.5:
            self.kill()
            self.in_flight = False
            return

        # Parabolic motion formula
        new_x = self.start_x + self.vx * elapsed_time
        new_y = self.start_y + (self.initial_vy * elapsed_time) + (0.5 * self.gravity * elapsed_time**2)
        
        self.rect.center = (new_x, new_y)
        
        # Check if ball has passed the target area
        if new_x > self.target_x + 100:
            self.kill()
            self.in_flight = False


class HoopShotGame:
    def __init__(self, screen, font, sound_manager):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager
        
        self.PLAY_AREA_RECT = pygame.Rect(
            PLAY_AREA_MARGIN, PLAY_AREA_MARGIN, 
            SCREEN_WIDTH - 2 * PLAY_AREA_MARGIN, 
            SCREEN_HEIGHT - 2 * PLAY_AREA_MARGIN
        )
        self.PLAY_AREA_CENTER_Y = self.PLAY_AREA_RECT.centery
        
        self.reset()

    def reset(self):
        self.shot_result = "Press SPACE to shoot!"
        
        # Coordinates relative to the play area
        self.bar_center_x = self.PLAY_AREA_RECT.left + 80
        self.bar_center_y = self.PLAY_AREA_CENTER_Y
        self.bar_amplitude = self.PLAY_AREA_RECT.height // 2 - 50
        self.zone_height = 50
        
        self.power_meter = SwayObject(
            center_x=self.bar_center_x,
            center_y=self.bar_center_y,
            amplitude=self.bar_amplitude,
            frequency=1.0,
            pattern=1,
            color=UI_BRIGHT_YELLOW, # Bright Yellow aimer
            size=20
        )
        
        self.all_sprites = pygame.sprite.Group(self.power_meter)
        self.shooter_x = self.PLAY_AREA_RECT.left + 150
        self.shooter_y = self.PLAY_AREA_RECT.bottom - 50
        self.perfect_zone_rect = pygame.Rect(0, 0, 0, 0)
        self._randomize_target_zone()

    def _randomize_target_zone(self):
        min_top_y = self.bar_center_y - self.bar_amplitude
        max_top_y = self.bar_center_y + self.bar_amplitude - self.zone_height
        self.perfect_zone_top = random.randint(min_top_y, max_top_y)
        self.perfect_zone_bottom = self.perfect_zone_top + self.zone_height
        self.perfect_zone_rect = pygame.Rect(
            self.bar_center_x - 10, self.perfect_zone_top, 20, self.zone_height
        )

    def _check_shot(self):
        score_to_report = 0
        indicator_y = self.power_meter.rect.centery
        arc_type = 'miss'

        if self.perfect_zone_top <= indicator_y <= self.perfect_zone_bottom:
            score_to_report = 250
            self.shot_result = f"SWISH! Perfect Shot! +{score_to_report} Points!"
            arc_type = 'swish'
            self.sound_manager.play_swish_cheer()
        else:
            zone_center_y = self.perfect_zone_top + (self.zone_height / 2)
            distance = abs(indicator_y - zone_center_y)
            
            if distance < self.zone_height * 2.5:
                self.shot_result = "Near Miss. Try to hit the green zone."
            else:
                self.shot_result = "Way Off! Miss."
            
            score_to_report = 0
            arc_type = random.choice(['overshoot', 'undershoot'])

        new_ball = Basketball(self.shooter_x, self.shooter_y, arc_type)
        self.all_sprites.add(new_ball)
        # Reset the power meter's timing to start a new sweep
        self.power_meter.time_offset = pygame.time.get_ticks() 
        self._randomize_target_zone()
        
        return score_to_report

    def handle_input(self, event):
        score_change = 0
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            score_change = self._check_shot()
        return score_change
    
    def update(self, dt):
        self.all_sprites.update()
        # Clean up basketballs that have finished their trajectory
        for sprite in self.all_sprites:
            if isinstance(sprite, Basketball) and not sprite.in_flight and sprite.alive():
                sprite.kill()
        return 0

    def draw(self): # Does not require total_score
        # Background and Play Area
        self.screen.fill(HOOP_BLUE)
        pygame.draw.rect(self.screen, BLACK, self.PLAY_AREA_RECT)

        # Power Meter Track
        track_rect = pygame.Rect(
            self.power_meter.start_x - 10, self.power_meter.start_y - self.bar_amplitude, 20, self.bar_amplitude * 2
        )
        pygame.draw.rect(self.screen, DARK_GRAY, track_rect, 0, border_radius=5)
        
        # Perfect Zone (Bright Green)
        pygame.draw.rect(self.screen, SPLASH_GREEN, self.perfect_zone_rect, 0, border_radius=5)

        # Shooter
        pygame.draw.circle(self.screen, WHITE, (self.shooter_x, self.shooter_y), 25)
        pygame.draw.circle(self.screen, DARK_GRAY, (self.shooter_x, self.shooter_y), 25, 3)

        # Hoop (drawn near the right edge)
        hoop_center_x = self.PLAY_AREA_RECT.right - 100
        hoop_center_y = self.PLAY_AREA_CENTER_Y
        
        # Backboard
        backboard_rect = (hoop_center_x, hoop_center_y - 75, 10, 150)
        pygame.draw.rect(self.screen, WHITE, backboard_rect)
        
        # Rim
        rim_rect = (hoop_center_x - 80, hoop_center_y - 15, 80, 30)
        pygame.draw.ellipse(self.screen, DARK_GRAY, rim_rect, 8)

        # Net drawing
        net_top_left = (hoop_center_x - 76, hoop_center_y)
        net_top_right = (hoop_center_x - 4, hoop_center_y)
        net_bottom_left = (hoop_center_x - 60, hoop_center_y + 60)
        net_bottom_right = (hoop_center_x - 20, hoop_center_y + 60)
        
        pygame.draw.line(self.screen, WHITE, net_top_left, net_bottom_left, 2)
        pygame.draw.line(self.screen, WHITE, net_top_right, net_bottom_right, 2)
        pygame.draw.line(self.screen, WHITE, net_bottom_left, net_bottom_right, 2)

        self.all_sprites.draw(self.screen)

        # Message display
        msg_text = self.font.render(self.shot_result, True, UI_BRIGHT_YELLOW)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 30))
        
    def cleanup(self):
        self.all_sprites.empty()

# ------------------------------------------------------------------------------
# 3. CLOWN SPLASH GAME 
# ------------------------------------------------------------------------------

def draw_clown_face_centered(surface, clown_size, hit, surface_size):
    """Draws the clown face, changing appearance on hit."""
    surface.fill((0, 0, 0, 0))
    offset = (surface_size - clown_size) // 2
    center = (surface_size // 2, surface_size // 2)
    radius = clown_size // 2
    
    face_color = WHITE if not hit else (200, 200, 200)
    pygame.draw.circle(surface, face_color, center, radius)

    if hit:
        # Splashed look
        pygame.draw.circle(surface, OG_WATER_CYAN, center, radius * 0.6)
        eye_y = offset + clown_size // 3
        pygame.draw.circle(surface, BLACK, (offset + clown_size // 3, eye_y), 4)
        pygame.draw.circle(surface, BLACK, (offset + clown_size - clown_size // 3, eye_y), 4)
        mouth_rect = pygame.Rect(offset + 5, offset + 3 * clown_size // 5, clown_size - 10, clown_size // 3)
        pygame.draw.arc(surface, BLACK, mouth_rect, math.pi * 1.1, math.pi * 1.9, 2)
    else:
        # Happy/Target look
        pygame.draw.circle(surface, CARNIVAL_RED, center, 8)
        smile_rect = pygame.Rect(offset + 5, offset + 5, clown_size - 10, clown_size - 10)
        pygame.draw.arc(surface, CARNIVAL_RED, smile_rect, 0, math.pi, 5)
        eye_y = offset + clown_size // 3
        pygame.draw.circle(surface, BLACK, (offset + clown_size // 3, eye_y), 3)
        pygame.draw.circle(surface, BLACK, (offset + clown_size - clown_size // 3, eye_y), 3)


class Clown(pygame.sprite.Sprite):
    """Target object in the Water Shooter game."""
    def __init__(self, center_x, center_y, size=60):
        super().__init__()
        self.clown_size = size
        self.visual_size = size + 20
        self.image = pygame.Surface([self.visual_size, self.visual_size], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(center_x, center_y))
        self.hit = False
        self.visual_hit = False
        self._draw()

    def _draw(self):
        draw_clown_face_centered(self.image, self.clown_size, self.visual_hit, self.visual_size)

    def mark_hit(self):
        self.hit = True
        return True
    
    def update_visual(self, is_hit_by_stream):
        """Toggles the 'splashed' visual state."""
        if is_hit_by_stream:
            if not self.visual_hit:
                self.visual_hit = True
                self._draw()
        else:
            if self.visual_hit:
                self.visual_hit = False
                self._draw()
    
    def is_hit_visual(self):
        return self.visual_hit
    
    def reset(self):
        self.hit = False
        self.visual_hit = False
        self._draw()


class WaterGun(pygame.sprite.Sprite):
    """Represents the water cannon and the stream of water."""
    def __init__(self, center_x, bottom_y):
        super().__init__()
        self.center_x_base = center_x
        self.current_angle = 0.0
        self.bottom_y = bottom_y
        
        self.current_stream_x = center_x
        self.current_stream_y = bottom_y - STREAM_LENGTH
        
        self.pivot_x = center_x
        self.pivot_y = bottom_y - 10
        
        # Draw the gun barrel (simulated)
        self.barrel_width = 80
        self.barrel_height = 20
        self.image = pygame.Surface([self.barrel_width, self.barrel_height], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.center_x_base, bottom_y - self.barrel_height // 2))
        pygame.draw.rect(self.image, BLACK, (0, 0, self.barrel_width, self.barrel_height), 0, border_radius=5)
        
        self.is_spraying = False
        self.max_stream_width = 20
        self.hit_stream_x = center_x
        # Surface for drawing the stream (must be transparent)
        self.stream_image = pygame.Surface([SCREEN_WIDTH, SCREEN_HEIGHT], pygame.SRCALPHA)
        self.stream_rect = self.stream_image.get_rect(topleft=(0, 0))

    def update_position(self, dt):
        """Updates the swinging position of the water stream."""
        self.current_angle += SWING_SPEED * dt
        swing_angle = math.sin(self.current_angle) * MAX_SWING_ANGLE
        
        # Calculate endpoint of the stream based on angle and length
        self.current_stream_x = self.pivot_x + STREAM_LENGTH * math.sin(swing_angle)
        self.current_stream_y = self.pivot_y - STREAM_LENGTH * math.cos(swing_angle)
        
    def update_stream(self, target_y, water_level_ratio):
        """Redraws the water stream based on current position and water level."""
        self.stream_image.fill((0, 0, 0, 0)) # Clear the previous stream
        
        if self.is_spraying:
            min_width_ratio = 0.2
            current_width_ratio = min_width_ratio + water_level_ratio * (1.0 - min_width_ratio)
            stream_width = max(2, int(self.max_stream_width * current_width_ratio))
            
            # Calculate where the stream hits the target line (clown Y-position)
            dy_target = self.pivot_y - target_y
            dy_total = self.pivot_y - self.current_stream_y
            
            if dy_total <= 0 or dy_target <= 0:
                hit_x = self.pivot_x
            else:
                t = min(1.0, dy_target / dy_total)
                hit_x = self.pivot_x + t * (self.current_stream_x - self.pivot_x)
            
            self.hit_stream_x = hit_x # Save for collision detection
            
            # Add a slight flicker effect to the water color
            flicker_blue = min(255, OG_WATER_CYAN[2] + random.randint(-20, 20))
            water_color = (OG_WATER_CYAN[0], OG_WATER_CYAN[1], flicker_blue)
            
            pygame.draw.line(
                self.stream_image,
                water_color,
                (self.pivot_x, self.pivot_y),
                (self.current_stream_x, self.current_stream_y),
                stream_width
            )
            
    def draw_stream(self, surface):
        if self.is_spraying:
            surface.blit(self.stream_image, self.stream_rect)


class ClownSplashMiniGame:
    def __init__(self, screen, font, sound_manager):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager
        self.small_font = pygame.font.Font(None, 30)
        
        self.PLAY_AREA_RECT = pygame.Rect(
            PLAY_AREA_MARGIN, PLAY_AREA_MARGIN, 
            SCREEN_WIDTH - 2 * PLAY_AREA_MARGIN, 
            SCREEN_HEIGHT - 2 * PLAY_AREA_MARGIN
        )
        self.PLAY_AREA_CENTER_X = self.PLAY_AREA_RECT.centerx
        
        self.reset()

    def reset(self):
        self.message = "Hold **SPACE** to spray water! Splash for points!"
        self.WATER_MAX = 100.0
        self.water_level = self.WATER_MAX
        self.SPRAY_RATE = 40.0
        self.REFILL_RATE = 10.0
        self.COOLDOWN_TIME = 0.5 
        self.last_spray_time = 0.0
        self.last_score_time = 0.0
        
        # Coordinates relative to the play area
        self.clown_target_y = self.PLAY_AREA_RECT.top + 100
        
        self.clown_targets = pygame.sprite.Group()
        self._setup_clowns()
        
        cannon_x = self.PLAY_AREA_CENTER_X
        cannon_y = self.PLAY_AREA_RECT.bottom - 50
        self.water_gun = WaterGun(cannon_x, cannon_y)
        
        self.space_down = False
        self.is_in_cooldown = False
        self.MAX_WATER = self.WATER_MAX

    def _setup_clowns(self):
        self.clown_targets.empty()
        clown_spacing = 150
        num_clowns = 3
        start_x = self.PLAY_AREA_CENTER_X - (num_clowns - 1) * clown_spacing / 2
        
        for i in range(num_clowns):
            x = start_x + (i * clown_spacing)
            clown = Clown(x, self.clown_target_y)
            self.clown_targets.add(clown)

    def handle_input(self, event):
        score_change = 0
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Only allow starting spray if not in cooldown
                if not self.is_in_cooldown:
                    self.space_down = True
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                if self.space_down: 
                    self.space_down = False
                    # When key is released, force cooldown start if not already cooling down
                    if not self.is_in_cooldown:
                        self.last_spray_time = time.time()
                        self.is_in_cooldown = True
                        for clown in self.clown_targets:
                            clown.reset()
                        self.sound_manager.play_water_spray(start=False)
                        self.message = "Cooldown initiated..." # Immediate feedback
                
        return score_change


    def update(self, dt):
        score_to_report = 0
        current_time = time.time()
        self.water_gun.update_position(dt)

        # --- Spraying Logic ---
        should_spray_attempt = self.space_down and not self.is_in_cooldown
        is_spraying_now = False
        
        if should_spray_attempt:
            if self.water_level > 0:
                self.water_level -= self.SPRAY_RATE * dt
                self.water_level = max(0.0, self.water_level)
                is_spraying_now = True
                self.sound_manager.play_water_spray(start=True)
                
                self.message = f"Spraying! Water: {int(self.water_level)}%"

                clowns_being_hit_this_frame = []
                for clown in self.clown_targets:
                    # Check for collision between the stream hit point and the clown's center
                    if abs(clown.rect.centerx - self.water_gun.hit_stream_x) < clown.clown_size / 2:
                        clown.mark_hit()
                        clowns_being_hit_this_frame.append(clown)

                # Score every half second if a clown is being hit
                if clowns_being_hit_this_frame and current_time - self.last_score_time >= HIT_SCORE_INTERVAL:
                    score_to_report = 10
                    self.last_score_time = current_time
                    self.message = f"**BULLSEYE!** Hit ongoing! Water: {int(self.water_level)}%"
                
                # Update clown visual state based on hits this frame
                for clown in self.clown_targets:
                    is_hit = clown in clowns_being_hit_this_frame
                    clown.update_visual(is_hit)


            # FIX: If water runs out while SPACE is held, stop spray, reset clowns, and initiate cooldown
            if self.water_level == 0.0 and is_spraying_now:
                is_spraying_now = False 
                self.last_spray_time = current_time 
                self.is_in_cooldown = True 
                self.sound_manager.play_water_spray(start=False)
                self.message = "Tank **EMPTY**! Refilling & Cooldown..."
                
                for clown in self.clown_targets:
                    clown.reset()

        # --- Cooldown Logic ---
        time_since_spray = current_time - self.last_spray_time
        
        if self.is_in_cooldown:
            if time_since_spray >= self.COOLDOWN_TIME:
                self.is_in_cooldown = False
                if not self.space_down and self.water_level == self.MAX_WATER:
                    self.message = "Tank fully charged. Hold **SPACE** to spray water!"
                elif not self.space_down and self.water_level < self.MAX_WATER:
                    self.message = "Refilling water tank..."
            else:
                remaining_time = self.COOLDOWN_TIME - time_since_spray
                self.message = f"Cooldown: {remaining_time:.1f}s until ready."
        
        # --- Refill Logic ---
        if not is_spraying_now and self.water_level < self.WATER_MAX and not self.is_in_cooldown:
            self.water_level += self.REFILL_RATE * dt
            self.water_level = min(self.WATER_MAX, self.water_level)
            
            if self.water_level == self.MAX_WATER and not self.space_down:
                self.message = "Tank fully charged. Hold **SPACE** to spray water!"
            elif not self.is_in_cooldown:
                self.message = "Refilling water tank..."

        if not is_spraying_now:
            self.sound_manager.play_water_spray(start=False)

        self.water_gun.is_spraying = is_spraying_now
        water_ratio = self.water_level / self.WATER_MAX
        self.water_gun.update_stream(self.clown_target_y, water_ratio)
            
        return score_to_report

    def draw(self): # Does not require total_score
        # Background and Play Area
        self.screen.fill(SPLASH_GREEN)
        pygame.draw.rect(self.screen, BLACK, self.PLAY_AREA_RECT)
        
        # Clown platform
        pygame.draw.rect(self.screen, CARNIVAL_RED, (self.PLAY_AREA_RECT.left, self.clown_target_y + 30, self.PLAY_AREA_RECT.width, 10))
        # Water Gun platform
        pygame.draw.rect(self.screen, CARNIVAL_RED, (self.PLAY_AREA_RECT.left, self.PLAY_AREA_RECT.bottom - 70, self.PLAY_AREA_RECT.width, 70))
        
        # Water Tank (Gauge)
        tank_x, tank_y = self.PLAY_AREA_RECT.left + 20, self.PLAY_AREA_CENTER_X - 100
        tank_width, tank_height = 40, 200
        
        pygame.draw.rect(self.screen, WHITE, (tank_x-3, tank_y-3, tank_width+6, tank_height+6), 3, border_radius=5)
        
        fill_ratio = self.water_level / self.WATER_MAX
        fill_height = int(fill_ratio * tank_height)
        fill_rect = pygame.Rect(
            tank_x,
            tank_y + tank_height - fill_height,
            tank_width,
            fill_height
        )
        pygame.draw.rect(self.screen, OG_WATER_CYAN, fill_rect, 0, border_radius=5)
        
        label = self.small_font.render("WATER", True, BLACK)
        self.screen.blit(label, (tank_x + tank_width // 2 - label.get_width() // 2, tank_y - 25))

        display_message = self.message.replace('**', '').replace('**', '')
        msg_text = self.font.render(display_message, True, UI_BRIGHT_YELLOW)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 30))

        self.water_gun.draw_stream(self.screen)
        self.clown_targets.draw(self.screen)
        self.screen.blit(self.water_gun.image, self.water_gun.rect)

    def cleanup(self):
        self.clown_targets.empty()
        self.sound_manager.play_water_spray(start=False)


# ------------------------------------------------------------------------------
# 4. SHELL GAME
# ------------------------------------------------------------------------------

class Cup(pygame.sprite.Sprite):
    """Represents one of the cups in the Shell Game."""
    def __init__(self, x, y, size=160, has_ball=False):
        super().__init__()
        self.size = size
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.current_x = x
        self.current_y = y
        self.has_ball = has_ball
        self.is_moving = False
        self.is_revealed = False
        self.color = CARNIVAL_RED # Cup color
        
        self.target_x = x
        self.target_y = y
        self.start_time = 0
        self.duration = SHUFFLE_DURATION_MS / 1000.0

        self._draw_cup()

    def _draw_cup(self):
        """Redraws the cup graphic."""
        self.image.fill((0, 0, 0, 0))
        
        # Simple cup shape
        points = [
            (5, self.size),
            (self.size - 5, self.size),
            (self.size - 25, 20),
            (25, 20)
        ]
        pygame.draw.polygon(self.image, self.color, points, 0)
        pygame.draw.polygon(self.image, BLACK, points, 3) # Outline
        
        if self.is_revealed and self.has_ball:
            # Draw the ball underneath when revealed
            pygame.draw.circle(self.image, WHITE, (self.size // 2, self.size - 30), 18)


    def set_target(self, target_x, target_y):
        """Starts the movement animation to a new target position."""
        self.target_x = target_x
        self.target_y = target_y
        self.start_time = time.time()
        self.is_moving = True
        self.duration = SHUFFLE_DURATION_MS / 1000.0

    def update(self):
        """Handles the cup's position during shuffling."""
        if self.is_moving:
            elapsed = time.time() - self.start_time
            progress = min(elapsed / self.duration, 1.0)
            
            # Use smooth step function for a less rigid shuffle animation (parabolic)
            smooth_progress = 0.5 - 0.5 * math.cos(progress * math.pi)
            
            new_x = self.current_x + (self.target_x - self.current_x) * smooth_progress
            new_y = self.current_y

            self.rect.center = (new_x, new_y)

            if progress >= 1.0:
                self.is_moving = False
                self.current_x = self.target_x
                self.current_y = self.target_y

    def reveal(self, should_reveal=True):
        """Toggles the visual state of the cup (up/down)."""
        self.is_revealed = should_reveal
        self._draw_cup()


class ShellGameMiniGame:
    def __init__(self, screen, font, sound_manager):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager
        
        self.PLAY_AREA_RECT = pygame.Rect(
            PLAY_AREA_MARGIN, PLAY_AREA_MARGIN, 
            SCREEN_WIDTH - 2 * PLAY_AREA_MARGIN, 
            SCREEN_HEIGHT - 2 * PLAY_AREA_MARGIN
        )
        self.PLAY_AREA_CENTER_X = self.PLAY_AREA_RECT.centerx
        
        self.reset()

    def reset(self):
        self.state = "START_REVEAL"
        self.shuffle_count = 10
        self.current_shuffle = 0
        self.message = "Get ready to watch closely!"
        self.shuffle_pairs = []
        
        pygame.time.set_timer(SHUFFLE_EVENT, 0) # Stop any existing timer
        
        # Positions relative to the play area
        self.cup_x_positions = [
            self.PLAY_AREA_CENTER_X - 200,
            self.PLAY_AREA_CENTER_X,
            self.PLAY_AREA_CENTER_X + 200
        ]
        self.cup_y = self.PLAY_AREA_RECT.bottom - 100

        self._setup_cups()
        self._initial_reveal_sequence()

    def _setup_cups(self):
        ball_index = random.randint(0, 2)

        self.cups = []
        for i, x_pos in enumerate(self.cup_x_positions):
            cup = Cup(x_pos, self.cup_y, size=160, has_ball=(i == ball_index))
            self.cups.append(cup)
            
        self.all_sprites = pygame.sprite.Group(self.cups)
            
        for cup in self.cups:
            cup.reveal(False)
            cup.is_moving = False


    def _initial_reveal_sequence(self):
        self.state = "START_REVEAL"
        for cup in self.cups:
            if cup.has_ball:
                cup.reveal(True)
            else:
                cup.reveal(False)
        self.message = "Watch the ball!"
        
        # Timer to move to the shuffling phase
        pygame.time.set_timer(SHUFFLE_EVENT, INITIAL_REVEAL_DURATION_MS, 1)


    def _start_shuffling(self):
        for cup in self.cups:
            cup.reveal(False)
            
        self.state = "SHUFFLING"
        self.current_shuffle = 0
        self.shuffle_pairs = self._generate_shuffle_pairs()
        self.message = f"Shuffling {self.shuffle_count} times... Keep your eyes on the ball!"
        
        # Set recurring timer for each shuffle step
        pygame.time.set_timer(SHUFFLE_EVENT, SHUFFLE_DURATION_MS + 100)

    def _generate_shuffle_pairs(self):
        """Generates a sequence of random cup index swaps."""
        pairs = []
        for _ in range(self.shuffle_count):
            indices = random.sample(range(3), 2)
            pairs.append(tuple(indices))
        return pairs

    def _do_one_shuffle(self):
        """Executes one swap step in the shuffle animation."""
        if any(cup.is_moving for cup in self.cups):
            return

        if self.current_shuffle >= len(self.shuffle_pairs):
            # Shuffling complete
            pygame.time.set_timer(SHUFFLE_EVENT, 0)
            self.state = "WAITING_CHOICE"
            self.message = "Where is the ball? Click on a cup!"
            self.sound_manager.play_clown_honk()
            return

        idx1, idx2 = self.shuffle_pairs[self.current_shuffle]
        
        cup1_obj = self.cups[idx1]
        cup2_obj = self.cups[idx2]
        
        # Get current logical positions
        target_x1, target_y1 = cup1_obj.current_x, cup1_obj.current_y
        target_x2, target_y2 = cup2_obj.current_x, cup2_obj.current_y

        # Start the movement animation
        cup1_obj.set_target(target_x2, target_y2)
        cup2_obj.set_target(target_x1, target_y1)
        
        # Swap the actual cup references in the list (important for tracking)
        self.cups[idx1], self.cups[idx2] = self.cups[idx2], self.cups[idx1]
        
        self.current_shuffle += 1

    def _check_choice(self, pos):
        """Checks if the user clicked the correct cup."""
        score_to_report = 0
        
        if self.state != "WAITING_CHOICE":
            return score_to_report
            
        chosen_cup = None
        for cup in self.cups:
            if cup.rect.collidepoint(pos):
                chosen_cup = cup
                break
        
        if chosen_cup:
            self.state = "GAME_OVER"
            
            # Reveal all cups
            for c in self.all_sprites:
                c.reveal(True)
                
            if chosen_cup.has_ball:
                score_to_report = 1000
                self.message = f"CONGRATS! You found the ball! +{score_to_report} Points! (Game resets soon)"
                self.sound_manager.play_fanfare()
            else:
                score_to_report = 0
                self.message = "Too bad! The ball was not there. (Game resets soon)"
            
            # Set timer for automatic game reset
            pygame.time.set_timer(SHUFFLE_EVENT, INITIAL_REVEAL_DURATION_MS, 1)
            
        return score_to_report
        
    def handle_input(self, event):
        score_change = 0
        
        if event.type == SHUFFLE_EVENT:
            if self.state == "START_REVEAL":
                self._start_shuffling()
            elif self.state == "SHUFFLING":
                self._do_one_shuffle()
            elif self.state == "GAME_OVER":
                self.reset()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "WAITING_CHOICE":
                score_change = self._check_choice(event.pos)
                
        return score_change

    def update(self, dt):
        self.all_sprites.update()
        return 0

    def draw(self): # Does not require total_score
        # Full-screen black background
        self.screen.fill(BLACK)
        
        # Table is the main play area (Brown)
        table_rect = pygame.Rect(self.PLAY_AREA_RECT.left, self.PLAY_AREA_RECT.top + 100, self.PLAY_AREA_RECT.width, self.PLAY_AREA_RECT.height - 100)
        pygame.draw.rect(self.screen, OG_BROWN, table_rect)

        msg_text = self.font.render(self.message, True, UI_BRIGHT_YELLOW)
        # TEXT ADJUSTMENT: Moved Y position from 50 to 80
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, 80))
        
        self.all_sprites.draw(self.screen)

    def cleanup(self):
        pygame.time.set_timer(SHUFFLE_EVENT, 0)
        self.all_sprites.empty()


# ==============================================================================
# ARCADE MANAGER (Main Game Loop and Menu Logic)
# ==============================================================================

class ArcadeManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.header_font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 36)
        self.ui_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24) 

        self.sound_manager = SoundManager()
        self.total_score = 0
        self.current_game_score = 0 # Score earned in the current minigame session
        
        # New structure for high scores per game
        self.game_high_scores = {
            STATE_DARTPOP: 0,
            STATE_HOOPSHOT: 0,
            STATE_SPLASH: 0,
            STATE_SHELLGAME: 0
        }

        self.state = STATE_MENU
        
        # Rects for click detection
        self.button_rects = {}
        self.stats_button_rect = pygame.Rect(0, 0, 0, 0) 
        
        self.games = {
            STATE_DARTPOP: DartPopGame(self.screen, self.ui_font, self.sound_manager),
            STATE_HOOPSHOT: HoopShotGame(self.screen, self.ui_font, self.sound_manager),
            STATE_SPLASH: ClownSplashMiniGame(self.screen, self.ui_font, self.sound_manager),
            STATE_SHELLGAME: ShellGameMiniGame(self.screen, self.ui_font, self.sound_manager),
            STATE_PRIZES: PrizeScreen(self.screen, self.header_font, self.sound_manager),
        }
        
        # CHANGE 1: Renamed Water Shooter to Clown Splash
        self.game_names = {
            STATE_DARTPOP: "Dart Pop",
            STATE_HOOPSHOT: "Hoop Shot",
            STATE_SPLASH: "Clown Splash", 
            STATE_SHELLGAME: "Shell Game",
            STATE_PRIZES: "PRIZES",
        }
        
        self.sound_manager.play_background_music()

    def _handle_input(self):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state != STATE_MENU and self.state != STATE_STATS:
                        # 1. Update High Score before leaving game
                        game_state = self.state
                        if game_state in self.game_high_scores and self.current_game_score > self.game_high_scores[game_state]:
                            self.game_high_scores[game_state] = self.current_game_score
                        
                        # 2. Reset session tracking
                        self.current_game_score = 0 
                        
                        # 3. Cleanup and move to menu
                        current_game = self.games[self.state]
                        current_game.cleanup()
                        current_game.reset()
                        self.state = STATE_MENU
                    elif self.state == STATE_MENU:
                        self.running = False
                
                # Check for SPACE exit from Stats Screen
                if self.state == STATE_STATS and event.key == pygame.K_SPACE:
                    self.state = STATE_MENU
            
            if self.state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check main game buttons
                    for game_state, rect in self.button_rects.items():
                        if rect.collidepoint(event.pos):
                            if game_state == STATE_SHELLGAME and self.total_score < SHELL_GAME_UNLOCK_SCORE:
                                pass
                            else:
                                # When entering a new game state:
                                self.state = game_state
                                if game_state != STATE_PRIZES:
                                    self.games[self.state].reset()
                                    self.current_game_score = 0 # Reset session score when entering
                                break
                                
                    # Check Stats Button
                    if self.stats_button_rect.collidepoint(event.pos):
                        self.state = STATE_STATS
            
            elif self.state in self.games:
                score_change = self.games[self.state].handle_input(event)
                if score_change > 0:
                    self.total_score += score_change
                    self.current_game_score += score_change

    def _update_state(self, dt):
        if self.state in self.games and self.state != STATE_PRIZES:
            score_change = self.games[self.state].update(dt)
            if score_change > 0:
                self.total_score += score_change
                self.current_game_score += score_change
            
    def _draw_menu(self):
        # 1. Background: Deep Blue base
        self.screen.fill(MENU_DARK_BLUE)
        
        # 1b. Draw Carnival Stripes (Tent Top effect) - NOW WHITE
        stripe_width = 40
        for i in range(0, SCREEN_WIDTH + stripe_width, stripe_width):
            color = CARNIVAL_RED if (i // stripe_width) % 2 == 0 else WHITE # Changed to WHITE
            # Draw stripes across the whole screen for a dramatic backdrop
            pygame.draw.rect(self.screen, color, (i, 0, stripe_width, SCREEN_HEIGHT))

        # 1c. Draw a dark overlay panel behind buttons for contrast
        overlay_width = 440
        overlay_height = 460
        overlay_rect = pygame.Rect(
            SCREEN_WIDTH//2 - overlay_width//2, 
            100, # Start below the main title
            overlay_width, 
            overlay_height
        )
        # Translucent black overlay
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 150)) # Black with 150 alpha
        self.screen.blit(overlay_surface, overlay_rect.topleft)
        
        # Gold border around the overlay
        pygame.draw.rect(self.screen, CARNIVAL_YELLOW, overlay_rect, 5, border_radius=30)
        
        # 2. Title: Gold Yellow Text
        title_surf = self.title_font.render("JAY'S CARNIVAL ARCADE", True, CARNIVAL_YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surf, title_rect)

        # 3. Stats Button (bottom left corner)
        stats_text = "📊 STATS"
        # STATS BUTTON ADJUSTMENT: X position pushed far left
        stats_button_rect = pygame.Rect(10, SCREEN_HEIGHT - PLAY_AREA_MARGIN - 50, 180, 50) 
        draw_button(self.screen, stats_text, stats_button_rect, DARK_GRAY, WHITE, self.button_font)
        self.stats_button_rect = stats_button_rect # Store rect for click detection

        # --- Button Layout (Shifted UP) ---
        y_start = 140 # Adjusted Y start position (moved up)
        button_height = 60
        button_width = 380
        button_spacing = 12
        
        self.button_rects = {}
        
        # Dart Pop button: Carnival Red
        rect_dart = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, y_start, button_width, button_height)
        draw_button(self.screen, self.game_names[STATE_DARTPOP], rect_dart, CARNIVAL_RED, BLACK, self.button_font)
        self.button_rects[STATE_DARTPOP] = rect_dart
        
        # Hoop Shot button: Bright Blue
        rect_hoop = pygame.Rect(rect_dart.left, rect_dart.bottom + button_spacing, button_width, button_height)
        draw_button(self.screen, self.game_names[STATE_HOOPSHOT], rect_hoop, HOOP_BLUE, WHITE, self.button_font)
        self.button_rects[STATE_HOOPSHOT] = rect_hoop

        # Clown Splash button: Bright Green
        rect_splash = pygame.Rect(rect_hoop.left, rect_hoop.bottom + button_spacing, button_width, button_height)
        draw_button(self.screen, self.game_names[STATE_SPLASH], rect_splash, SPLASH_GREEN, BLACK, self.button_font)
        self.button_rects[STATE_SPLASH] = rect_splash

        # Shell Game button: Gold or Dark Grey (Locked)
        rect_shell = pygame.Rect(rect_splash.left, rect_splash.bottom + button_spacing, button_width, button_height)
        is_locked = self.total_score < SHELL_GAME_UNLOCK_SCORE
        button_text = self.game_names[STATE_SHELLGAME]
        if is_locked:
            button_text = f"Shell Game (Unlock at {SHELL_GAME_UNLOCK_SCORE} pts)"
            
        draw_button(self.screen, button_text, rect_shell, CARNIVAL_YELLOW, BLACK, self.button_font, locked=is_locked)
        self.button_rects[STATE_SHELLGAME] = rect_shell
        
        # PRIZE Button: Bright Yellow
        rect_prize = pygame.Rect(rect_shell.left, rect_shell.bottom + button_spacing, button_width, button_height)
        draw_button(self.screen, self.game_names[STATE_PRIZES], rect_prize, UI_BRIGHT_YELLOW, BLACK, self.header_font)
        self.button_rects[STATE_PRIZES] = rect_prize
        
        # Instruction for ESC
        inst_surf = self.small_font.render("Press ESC to exit Arcade", True, DARK_GRAY)
        self.screen.blit(inst_surf, (SCREEN_WIDTH // 2 - inst_surf.get_width() // 2, SCREEN_HEIGHT - 30))

    def _draw_stats_screen(self):
        """Draws the transparent pop-up displaying scores, now showing high scores per game."""
        
        # Draw a dark, slightly translucent overlay over the existing screen content
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)) # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # CHANGE 2: Stats panel is now 450x350 (was 500x400)
        panel_w, panel_h = 450, 350
        x_offset = -50
        y_offset = -50 
        panel_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - panel_w // 2 + x_offset, 
            SCREEN_HEIGHT // 2 - panel_h // 2 + y_offset, 
            panel_w, panel_h
        )
        # Calculate the new center X for internal alignment
        panel_center_x = panel_rect.left + panel_w // 2

        pygame.draw.rect(self.screen, MENU_DARK_BLUE, panel_rect, 0, border_radius=20)
        pygame.draw.rect(self.screen, CARNIVAL_YELLOW, panel_rect, 5, border_radius=20)

        # Title (centered in panel)
        title_surf = self.header_font.render("ARCADE STATS", True, UI_BRIGHT_YELLOW)
        self.screen.blit(title_surf, title_surf.get_rect(center=(panel_center_x, panel_rect.top + 30)))
        
        # Total Score (centered in panel)
        total_surf = self.button_font.render(f"GRAND TOTAL: {self.total_score} Points", True, WHITE)
        self.screen.blit(total_surf, total_surf.get_rect(center=(panel_center_x, panel_rect.top + 80)))

        # High Scores Header (centered in panel)
        header_surf = self.ui_font.render("--- HIGHEST SCORE PER GAME (Session) ---", True, CARNIVAL_RED)
        self.screen.blit(header_surf, header_surf.get_rect(center=(panel_center_x, panel_rect.top + 130)))

        # List High Scores (centered in panel)
        y_pos = panel_rect.top + 160
        game_states = [STATE_DARTPOP, STATE_HOOPSHOT, STATE_SPLASH, STATE_SHELLGAME]
        
        for game_state in game_states:
            game_name = self.game_names.get(game_state, "Unknown Game")
            high_score = self.game_high_scores.get(game_state, 0)
            
            rank_text = f"{game_name}: {high_score} Points"
            color = WHITE
            
            if high_score > 0:
                color = SPLASH_GREEN 

            score_surf = self.button_font.render(rank_text, True, color)
            self.screen.blit(score_surf, score_surf.get_rect(center=(panel_center_x, y_pos)))
            y_pos += 40
            
        # Exit instruction (centered in panel)
        exit_surf = self.ui_font.render("Press SPACE to return to Menu", True, DARK_GRAY)
        self.screen.blit(exit_surf, exit_surf.get_rect(center=(panel_center_x, panel_rect.bottom - 20)))

    def _draw_game_score(self):
        # UI Readout in top right corner (Game name + Score)
        # Also display current session score
        session_text = f"SESSION: {self.current_game_score}"
        
        # Adjust position slightly for better visibility
        session_surf = self.ui_font.render(session_text, True, UI_BRIGHT_YELLOW)
        self.screen.blit(session_surf, (SCREEN_WIDTH - session_surf.get_width() - 10, 10))
        
        total_text = f"TOTAL: {self.total_score} | ESC to Menu"
        total_surf = self.ui_font.render(total_text, True, UI_BRIGHT_YELLOW)
        self.screen.blit(total_surf, (SCREEN_WIDTH - total_surf.get_width() - 10, 40))


    def run(self):
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            self._handle_input()
            self._update_state(dt) # Call update for game logic (like water gun swing)
            
            if self.state == STATE_MENU:
                self._draw_menu()
            elif self.state == STATE_STATS:
                # Draw the menu screen first, then overlay the stats pop-up
                self._draw_menu() 
                self._draw_stats_screen()
            elif self.state in self.games:
                game = self.games[self.state]
                
                # Draw the game (or prize screen with score included)
                if self.state == STATE_PRIZES:
                    game.draw(self.total_score)
                else:
                    game.draw()
                
                # ONLY draw the floating score UI if not on the Prize screen
                if self.state != STATE_PRIZES:
                    self._draw_game_score()
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == '__main__':
    manager = ArcadeManager()
    manager.run()
    pygame.quit()
    sys.exit()

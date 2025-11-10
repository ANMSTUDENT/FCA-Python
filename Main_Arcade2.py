import pygame
import sys
import time
import random
import math

# --- Global Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Colors (Unified Palette) ---
# Core Carnival Palette: High Contrast Red/Black/Gold/Blue
CARNIVAL_BLACK = (0, 0, 0)         # Deep, solid Black backdrop
CARNIVAL_WHITE = (255, 255, 255)   # White for contrast text
CARNIVAL_GOLD = (255, 215, 0)      # Gold/Yellow for critical elements/scores
CARNIVAL_RED = (200, 40, 40)       # Bright Red for primary background/buttons
CARNIVAL_BLUE = (30, 70, 200)      # Bright Blue for targets/secondary elements
DARK_GRAY = (50, 50, 50)           # Dark Grey for locked buttons
BRIGHT_GREEN = (50, 200, 50)       # For Water Shooter element (Aimer)
WATER_CYAN = (100, 200, 255)       # For water splash

# Score Threshold to unlock the Shell Game
SHELL_GAME_UNLOCK_SCORE = 1000 

# --- Game State Definitions ---
STATE_TITLE = -1           # Main entry screen (Start, Options, Prizes, Exit)
STATE_MENU = 0             # Game selection/Options screen (The Hub)
STATE_DARTPOP = 1
STATE_HOOPSHOT = 2
STATE_SPLASH = 3
STATE_SHELLGAME = 4
STATE_PRIZES = 5           # Prizes display screen

# --- Game-Specific Constants ---
HIT_SCORE_INTERVAL = 0.5
MAX_SWING_ANGLE = math.pi / 4.5
SWING_SPEED = 1.0
STREAM_LENGTH = 450
SHUFFLE_EVENT = pygame.USEREVENT + 1
SHUFFLE_DURATION_MS = 500
INITIAL_REVEAL_DURATION_MS = 1500

# --- Utility Functions ---

def draw_button(screen, text, rect, color, text_color, font, locked=False):
    """Draws a themed rectangular button."""
    
    # Draw background rectangle (Red/Blue/Gold)
    if locked:
        display_color = DARK_GRAY
        text = "LOCKED (Score " + str(SHELL_GAME_UNLOCK_SCORE) + "+)"
    else:
        display_color = color
        
    pygame.draw.rect(screen, display_color, rect, 0, border_radius=15)
    
    # Draw border in Gold/Yellow for visual pop
    pygame.draw.rect(screen, CARNIVAL_GOLD, rect, 3, border_radius=15)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def load_fonts():
    # Attempt to load a bold, sans-serif font
    try:
        font = pygame.font.SysFont('impact', 32, bold=True)
        big_font = pygame.font.SysFont('impact', 80, bold=True)
    except:
        # Fallback to default if 'impact' is not found
        font = pygame.font.Font(None, 32)
        big_font = pygame.font.Font(None, 80)
        
    return font, big_font

# ------------------------------------------------------------------------------
# AUDIO PLACEHOLDERS
# ------------------------------------------------------------------------------

def play_sound(sound_type):
    """Placeholder function for playing sounds."""
    # In a real game, you would load and play actual .wav files here.
    # For now, we will print a message to simulate the audio event.
    
    if sound_type == "calliope":
        print(">> AUDIO: Playing upbeat Calliope/Carnival March loop (BGM)")
    elif sound_type == "dart_pop":
        print(">> AUDIO: Distinct, high-impact 'pop'")
    elif sound_type == "hoop_swish":
        print(">> AUDIO: Satisfying 'swish' followed by short crowd 'cheer'")
    elif sound_type == "win_fanfare":
        print(">> AUDIO: Celebratory, short triumphant fanfare")
    elif sound_type == "water_hiss":
        # This would be a continuous loop during key press
        print(">> AUDIO: High-pitched, steady 'whoosh' runs...")
    elif sound_type == "clown_honk":
        print(">> AUDIO: Quick clown honk signals selection start.")
    elif sound_type == "game_fail":
        print(">> AUDIO: Low-tone buzz or failure sound.")
    else:
        print(f">> AUDIO: Placeholder for {sound_type}")

# ------------------------------------------------------------------------------
# DART POP GAME CLASSES (Modified for UI)
# ------------------------------------------------------------------------------

class DartPopGame:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.target_radius = 200      
        self.arm_length = 150         
        self.target_angle = 3 * math.pi / 2
        self.hit_angle_min = self.target_angle - 0.26
        self.hit_angle_max = self.target_angle + 0.26
        self.rotation_speed = 1.5
        self.reset()
        self.message = "Press SPACE to throw the dart!"

    def generate_balloons(self):
        self.balloons = []
        target_radius = self.arm_length 
        balloon_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        # Using CARNIVAL_BLUE for balloons as per spec
        colors = [CARNIVAL_BLUE] * len(balloon_angles)
        
        for i, angle in enumerate(balloon_angles):
            x = self.center_x + target_radius * math.cos(angle)
            y = self.center_y + target_radius * math.sin(angle)
            size = random.randint(20, 28) # Slightly larger balloons
            color = colors[i]
            self.balloons.append({'pos': (int(x), int(y)), 'size': size, 'color': color, 'hit': False})

    def reset(self):
        self.game_time = 0.0
        self.dart_thrown = False
        self.hit_result = None
        self.last_score_change = 0 
        self.center_x, self.center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.bullseye_radius = 20
        self.rotation_speed = 1.5 * random.choice([1, -1])
        self.generate_balloons()

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
                for balloon in self.balloons:
                    if not balloon['hit']: 
                        dist = math.hypot(dart_x - balloon['pos'][0], dart_y - balloon['pos'][1])
                        if dist < balloon['size']:
                            balloon['hit'] = True
                            hit_balloon = True
                            hit_score += 100 
                            play_sound("dart_pop") # Audio
                if hit_balloon:
                    self.hit_result = 'HIT'
                    self.last_score_change = hit_score
                    self.message = f"POP! +{self.last_score_change} Points! (Press R to Reset/Continue)"
                    score_to_report = self.last_score_change
                else:
                    if (self.hit_angle_min < normalized_angle < self.hit_angle_max) or \
                       (self.hit_angle_min < normalized_angle - 2 * math.pi < self.hit_angle_max):
                        self.hit_result = 'NEAR_MISS'
                        self.last_score_change = 50 
                        self.message = f"Good Timing! +{self.last_score_change} Points! (Press R to Reset/Continue)"
                        score_to_report = self.last_score_change
                    else:
                        self.hit_result = 'MISS'
                        self.last_score_change = 0
                        self.message = "MISS! (Press R to Reset/Continue)"
                        play_sound("game_fail") # Audio
                        score_to_report = 0

        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if self.dart_thrown:
                self.reset()
                self.message = "Press SPACE to throw the dart!"
        return score_to_report

    def update(self, dt):
        if not self.dart_thrown:
            self.game_time += dt
        return 0

    def draw(self):
        # Background: Vibrant Red
        self.screen.fill(CARNIVAL_RED) 
        
        # Target Area: Large Black Rectangle
        target_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 250, 500, 500)
        pygame.draw.rect(self.screen, CARNIVAL_BLACK, target_rect)
        
        # Center target visual 
        pygame.draw.circle(self.screen, DARK_GRAY, (self.center_x, self.center_y), self.target_radius + 50, 0)
        pygame.draw.circle(self.screen, CARNIVAL_RED, (self.center_x, self.center_y), self.target_radius, 0)
        pygame.draw.circle(self.screen, CARNIVAL_BLACK, (self.center_x, self.center_y), self.target_radius * 0.5)
        pygame.draw.circle(self.screen, CARNIVAL_GOLD, (self.center_x, self.center_y), self.bullseye_radius)
        
        for balloon in self.balloons:
            if balloon['hit']:
                # Pop visual: white burst 
                pygame.draw.circle(self.screen, CARNIVAL_WHITE, balloon['pos'], balloon['size'] + 5)
                pygame.draw.circle(self.screen, CARNIVAL_RED, balloon['pos'], balloon['size'] - 10)
            else:
                pygame.draw.circle(self.screen, balloon['color'], balloon['pos'], balloon['size'])

        angle = self.game_time * self.rotation_speed
        end_x = self.center_x + self.arm_length * math.cos(angle)
        end_y = self.center_y + self.arm_length * math.sin(angle)
        
        if not self.dart_thrown:
            # Aimer/Reticle: bright Yellow crosshairs
            pygame.draw.line(self.screen, CARNIVAL_GOLD, (self.center_x, self.center_y), (end_x, end_y), 3)
            pygame.draw.circle(self.screen, CARNIVAL_GOLD, (int(end_x), int(end_y)), 8)
        
        if self.dart_thrown:
            dart_x = self.center_x + self.arm_length * math.cos(angle)
            dart_y = self.center_y + self.arm_length * math.sin(angle)
            color = CARNIVAL_GOLD if self.hit_result != 'MISS' else CARNIVAL_RED
            pygame.draw.circle(self.screen, color, (int(dart_x), int(dart_y)), 12)
            
        self._draw_message()
        
    def _draw_message(self):
        text_surf = self.font.render(self.message, True, CARNIVAL_GOLD)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(text_surf, text_rect)

    def cleanup(self):
        pass

# ------------------------------------------------------------------------------
# HOOP SHOT GAME CLASSES (Modified for UI)
# ------------------------------------------------------------------------------

class SwayObject(pygame.sprite.Sprite):
    def __init__(self, center_x, center_y, amplitude, frequency, pattern, color=CARNIVAL_RED, size=20):
        super().__init__()
        self.image = pygame.Surface([size * 10, size], pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect(center=(center_x, center_y))
        self.start_x = center_x
        self.start_y = center_y
        self.amplitude = amplitude 
        self.frequency = frequency 
        self.pattern = pattern     
        self.color = color
        self.size = size
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
        
        # Aimer/Reticle: bright Yellow crosshairs
        center = (self.size * 5, self.size // 2)
        radius = self.size // 2
        
        # Draw target ring in Gold
        pygame.draw.circle(self.image, CARNIVAL_GOLD, center, radius, 3)
        # Draw crosshairs
        pygame.draw.line(self.image, CARNIVAL_GOLD, (center[0] - radius, center[1]), (center[0] + radius, center[1]), 2)
        pygame.draw.line(self.image, CARNIVAL_GOLD, (center[0], center[1] - radius), (center[0], center[1] + radius), 2)
        
        return y_offset 

class Basketball(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, arc_type): 
        super().__init__()
        self.size = 40 
        self.image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, CARNIVAL_RED, (self.size // 2, self.size // 2), self.size // 2)

        self.rect = self.image.get_rect(center=(start_x, start_y))
        
        self.start_time = pygame.time.get_ticks()
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = SCREEN_WIDTH - 150 
        self.target_y = SCREEN_HEIGHT // 2 
        self.gravity = 1500.0 

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
            self.initial_vy = -650.0 
            
        self.vx = (self.target_x - self.start_x) / self.duration
        self.in_flight = True

    def update(self):
        if not self.in_flight:
            return
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000.0
        if elapsed_time > self.duration * 1.5: 
              self.kill()
              self.in_flight = False
              return

        new_x = self.start_x + self.vx * elapsed_time
        new_y = self.start_y + (self.initial_vy * elapsed_time) + (0.5 * self.gravity * elapsed_time**2)
        
        self.rect.center = (new_x, new_y)
        
        if new_x > self.target_x + 100:
              self.kill() 
              self.in_flight = False


class HoopShotGame:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.reset()

    def reset(self):
        self.shot_result = "Press SPACE to shoot!"
        self.last_score_change = 0
        self.bar_center_x = 100
        self.bar_center_y = SCREEN_HEIGHT // 2
        self.bar_amplitude = 150 
        self.zone_height = 50 
        
        self.power_meter = SwayObject(
            center_x=self.bar_center_x,
            center_y=self.bar_center_y,
            amplitude=self.bar_amplitude, 
            frequency=1.0,           
            pattern=1,               
            color=CARNIVAL_RED,
            size=20
        )
        
        self.all_sprites = pygame.sprite.Group(self.power_meter)
        self.shooter_x = 150 
        self.shooter_y = SCREEN_HEIGHT - 100 
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
            play_sound("hoop_swish") # Audio
        else:
            zone_center_y = self.perfect_zone_top + (self.zone_height / 2)
            distance = abs(indicator_y - zone_center_y)
            
            if distance < self.zone_height * 2.5: 
                self.shot_result = "Near Miss. Try to hit the green zone."
            else:
                self.shot_result = "Way Off! Miss."
                play_sound("game_fail") # Audio
            
            score_to_report = 0
            arc_type = random.choice(['overshoot', 'undershoot'])

        new_ball = Basketball(self.shooter_x, self.shooter_y, arc_type)
        self.all_sprites.add(new_ball) 
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
        for sprite in self.all_sprites:
            if isinstance(sprite, Basketball) and not sprite.in_flight and sprite.alive():
                sprite.kill()
        return 0

    def draw(self):
        # Background: Vibrant Red
        self.screen.fill(CARNIVAL_RED) 

        # Target Area: Large Black Rectangle (The court/back wall)
        target_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 250, 500, 500)
        pygame.draw.rect(self.screen, CARNIVAL_BLACK, target_rect)
        
        # Power Meter Track
        track_rect = pygame.Rect(
            self.power_meter.start_x - 10, self.power_meter.start_y - self.power_meter.amplitude, 20, self.power_meter.amplitude * 2
        )
        pygame.draw.rect(self.screen, DARK_GRAY, track_rect, 0, border_radius=5)
        
        # Perfect Zone (Bright Green)
        perfect_zone_rect_themed = pygame.Rect(
            self.perfect_zone_rect.left, self.perfect_zone_rect.top, 
            self.perfect_zone_rect.width, self.perfect_zone_rect.height
        )
        pygame.draw.rect(self.screen, BRIGHT_GREEN, perfect_zone_rect_themed, 0, border_radius=5)
        pygame.draw.rect(self.screen, CARNIVAL_GOLD, perfect_zone_rect_themed, 2, border_radius=5) # Gold highlight

        # Shooter area
        pygame.draw.circle(self.screen, CARNIVAL_BLUE, (self.shooter_x, self.shooter_y), 30)
        pygame.draw.circle(self.screen, CARNIVAL_GOLD, (self.shooter_x, self.shooter_y), 30, 3)

        hoop_center_x = SCREEN_WIDTH - 150 
        hoop_center_y = SCREEN_HEIGHT // 2 
        
        # Backboard 
        backboard_rect = (hoop_center_x, hoop_center_y - 75, 10, 150)
        pygame.draw.rect(self.screen, CARNIVAL_WHITE, backboard_rect)
        
        # Rim (Bright Blue)
        rim_rect = (hoop_center_x - 80, hoop_center_y - 15, 80, 30)
        pygame.draw.ellipse(self.screen, CARNIVAL_BLUE, rim_rect, 8)

        # Net (White/Gold)
        net_top_left = (hoop_center_x - 76, hoop_center_y)
        net_top_right = (hoop_center_x - 4, hoop_center_y)
        net_bottom_left = (hoop_center_x - 60, hoop_center_y + 60)
        net_bottom_right = (hoop_center_x - 20, hoop_center_y + 60)
        
        pygame.draw.line(self.screen, CARNIVAL_WHITE, net_top_left, net_bottom_left, 2)
        pygame.draw.line(self.screen, CARNIVAL_WHITE, net_top_right, net_bottom_right, 2)
        pygame.draw.line(self.screen, CARNIVAL_GOLD, net_bottom_left, net_bottom_right, 2)

        self.all_sprites.draw(self.screen)

        msg_text = self.font.render(self.shot_result, True, CARNIVAL_GOLD)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 50))
        
    def cleanup(self):
        self.all_sprites.empty()

# ------------------------------------------------------------------------------
# CLOWN SPLASH GAME CLASSES (Modified for UI and Audio Logic)
# ------------------------------------------------------------------------------

def draw_clown_face_centered(surface, clown_size, hit, surface_size):
    surface.fill((0, 0, 0, 0))
    offset = (surface_size - clown_size) // 2
    center = (surface_size // 2, surface_size // 2)
    radius = clown_size // 2
    
    face_color = CARNIVAL_WHITE if not hit else DARK_GRAY
    pygame.draw.circle(surface, face_color, center, radius)

    if hit:
        pygame.draw.circle(surface, WATER_CYAN, center, radius * 0.6)
        # Simplified hit eyes/mouth
        pygame.draw.rect(surface, CARNIVAL_BLACK, (center[0] - 10, center[1] - 5, 20, 10))
    else:
        # Clown features in bright Blue
        pygame.draw.circle(surface, CARNIVAL_BLUE, center, 8) # Nose
        smile_rect = pygame.Rect(offset + 5, offset + 5, clown_size - 10, clown_size - 10)
        pygame.draw.arc(surface, CARNIVAL_RED, smile_rect, 0, math.pi, 5) # Big Smile
        eye_y = offset + clown_size // 3
        pygame.draw.circle(surface, CARNIVAL_BLACK, (offset + clown_size // 3, eye_y), 3)
        pygame.draw.circle(surface, CARNIVAL_BLACK, (offset + clown_size - clown_size // 3, eye_y), 3)


class Clown(pygame.sprite.Sprite):
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
    def __init__(self, center_x, bottom_y):
        super().__init__()
        self.center_x_base = center_x
        self.current_angle = 0.0
        self.bottom_y = bottom_y
        
        self.current_stream_x = center_x
        self.current_stream_y = bottom_y - STREAM_LENGTH
        
        self.pivot_x = center_x
        self.pivot_y = bottom_y - 10
        
        self.barrel_width = 80
        self.barrel_height = 20
        self.image = pygame.Surface([self.barrel_width, self.barrel_height], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.center_x_base, bottom_y - self.barrel_height // 2))
        pygame.draw.rect(self.image, CARNIVAL_BLACK, (0, 0, self.barrel_width, self.barrel_height), 0, border_radius=5)
        
        self.is_spraying = False
        self.max_stream_width = 20
        self.hit_stream_x = center_x
        self.stream_image = pygame.Surface([SCREEN_WIDTH, SCREEN_HEIGHT], pygame.SRCALPHA)
        self.stream_rect = self.stream_image.get_rect(topleft=(0, 0))

    def update_position(self, dt):
        self.current_angle += SWING_SPEED * dt
        swing_angle = math.sin(self.current_angle) * MAX_SWING_ANGLE
        self.current_stream_x = self.pivot_x + STREAM_LENGTH * math.sin(swing_angle)
        self.current_stream_y = self.pivot_y - STREAM_LENGTH * math.cos(swing_angle)
        
    def update_stream(self, target_y, water_level_ratio):
        self.stream_image.fill((0, 0, 0, 0))
        
        if self.is_spraying:
            min_width_ratio = 0.2
            current_width_ratio = min_width_ratio + water_level_ratio * (1.0 - min_width_ratio)
            stream_width = max(2, int(self.max_stream_width * current_width_ratio))
            
            dy_target = self.pivot_y - target_y
            dy_total = self.pivot_y - self.current_stream_y
            
            if dy_total <= 0 or dy_target <= 0:
                hit_x = self.pivot_x
            else:
                t = min(1.0, dy_target / dy_total)
                hit_x = self.pivot_x + t * (self.current_stream_x - self.pivot_x)
            
            self.hit_stream_x = hit_x
            
            flicker_blue = min(255, WATER_CYAN[2] + random.randint(-20, 20))
            water_color = (WATER_CYAN[0], WATER_CYAN[1], flicker_blue)
            
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
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.small_font = pygame.font.Font(None, 30) 
        self.reset()
        self.is_hissing = False # Audio state

    def reset(self):
        self.message = "Hold **SPACE** to spray water! Splash for points!"
        self.WATER_MAX = 100.0
        self.water_level = self.WATER_MAX
        self.SPRAY_RATE = 40.0
        self.REFILL_RATE = 10.0
        self.COOLDOWN_TIME = 0.5
        self.last_spray_time = 0.0
        self.last_score_time = 0.0
        
        self.clown_target_y = 150
        self.clown_targets = pygame.sprite.Group()
        self._setup_clowns()
        
        cannon_x = SCREEN_WIDTH // 2
        cannon_y = SCREEN_HEIGHT - 100
        self.water_gun = WaterGun(cannon_x, cannon_y)
        
        self.space_down = False
        self.is_in_cooldown = False
        self.is_hissing = False 

    def _setup_clowns(self):
        self.clown_targets.empty()
        clown_spacing = 150
        num_clowns = 3
        start_x = SCREEN_WIDTH // 2 - (num_clowns - 1) * clown_spacing / 2
        
        for i in range(num_clowns):
            x = start_x + (i * clown_spacing)
            clown = Clown(x, self.clown_target_y)
            self.clown_targets.add(clown)

    def handle_input(self, event):
        score_change = 0
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.space_down = True
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.space_down = False
                self.last_spray_time = time.time()
                self.is_in_cooldown = True
                self.is_hissing = False # Stop continuous audio
                
                for clown in self.clown_targets:
                    clown.reset()
                self.message = "Refilling water tank (cooldown active)..."
                
        return score_change


    def update(self, dt):
        score_to_report = 0
        current_time = time.time()
        self.water_gun.update_position(dt)

        is_spraying_now = False
        clowns_being_hit_this_frame = []
        
        # 1. Update Cooldown State
        time_since_spray = current_time - self.last_spray_time
        if self.is_in_cooldown and time_since_spray >= self.COOLDOWN_TIME:
            self.is_in_cooldown = False
            
        # 2. Water & Scoring Logic
        if self.space_down and not self.is_in_cooldown and self.water_level > 0:
            
            if not self.is_hissing:
                play_sound("water_hiss") # Start continuous audio
                self.is_hissing = True
            
            self.water_level -= self.SPRAY_RATE * dt
            self.water_level = max(0.0, self.water_level)
            self.message = f"Spraying! Water: {int(self.water_level)}%"
            is_spraying_now = True
            
            # Collision Check
            for clown in self.clown_targets:
                if abs(clown.rect.centerx - self.water_gun.hit_stream_x) < clown.clown_size / 2:
                    clown.mark_hit()
                    clowns_being_hit_this_frame.append(clown)

            # Continuous Scoring Logic
            if clowns_being_hit_this_frame and current_time - self.last_score_time >= HIT_SCORE_INTERVAL:
                score_to_report = 10 
                self.last_score_time = current_time
                self.message = f"**BULLSEYE!** Hit ongoing! Water: {int(self.water_level)}%"
            
        elif self.water_level == 0.0 and self.space_down:
            self.message = "Tank **EMPTY**! Refilling..."
            self.is_hissing = False # Stop audio if tank is empty
            
        # 3. Refill Logic
        if not is_spraying_now and self.water_level < self.WATER_MAX and not self.is_in_cooldown:
            self.water_level += self.REFILL_RATE * dt
            self.water_level = min(self.WATER_MAX, self.water_level)
            
            if self.water_level == self.WATER_MAX and not self.space_down:
                self.message = "Tank fully charged. Hold **SPACE** to spray water!"
            else:
                self.message = "Refilling water tank..."

        # 4. Update Visuals
        self.water_gun.is_spraying = is_spraying_now
        water_ratio = self.water_level / self.WATER_MAX
        self.water_gun.update_stream(self.clown_target_y, water_ratio)

        for clown in self.clown_targets:
            is_hit = clown in clowns_being_hit_this_frame
            clown.update_visual(is_hit)
            
        return score_to_report

    def draw(self):
        # Background: Vibrant Red
        self.screen.fill(CARNIVAL_RED)
        
        # Target Area: Large Black Rectangle
        target_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 0, 500, SCREEN_HEIGHT - 100)
        pygame.draw.rect(self.screen, CARNIVAL_BLACK, target_rect)
        
        # Targets are clowns
        self.clown_targets.draw(self.screen)
        
        # Gun foreground/stand
        pygame.draw.rect(self.screen, CARNIVAL_BLUE, (0, SCREEN_HEIGHT - 70, SCREEN_WIDTH, 70))
        self.water_gun.draw_stream(self.screen)
        self.screen.blit(self.water_gun.image, self.water_gun.rect)
        
        # Water Tank Visual (Gauge)
        tank_x, tank_y = 50, SCREEN_HEIGHT // 2 - 100
        tank_width, tank_height = 40, 200
        
        pygame.draw.rect(self.screen, CARNIVAL_GOLD, (tank_x-3, tank_y-3, tank_width+6, tank_height+6), 3, border_radius=5)
        
        fill_ratio = self.water_level / self.WATER_MAX
        fill_height = int(fill_ratio * tank_height)
        fill_rect = pygame.Rect(
            tank_x,
            tank_y + tank_height - fill_height,
            tank_width,
            fill_height
        )
        pygame.draw.rect(self.screen, WATER_CYAN, fill_rect, 0, border_radius=5)
        
        label = self.small_font.render("WATER", True, CARNIVAL_GOLD)
        self.screen.blit(label, (tank_x + tank_width // 2 - label.get_width() // 2, tank_y - 25))

        display_message = self.message.replace('**', '').replace('**', '')
        msg_text = self.font.render(display_message, True, CARNIVAL_GOLD) 
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 30))

    def cleanup(self):
        self.clown_targets.empty()

# ------------------------------------------------------------------------------
# SHELL GAME CLASSES (Modified for UI and Audio Logic)
# ------------------------------------------------------------------------------

class Cup(pygame.sprite.Sprite):
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
        self.color = CARNIVAL_RED
        
        self.target_x = x
        self.target_y = y
        self.start_time = 0
        self.duration = SHUFFLE_DURATION_MS / 1000.0

        self._draw_cup()

    def _draw_cup(self):
        self.image.fill((0, 0, 0, 0))
        
        points = [
            (5, self.size),
            (self.size - 5, self.size),
            (self.size - 25, 20),
            (25, 20)
        ]
        # Draw cup in CARNIVAL_RED with a Gold border
        pygame.draw.polygon(self.image, CARNIVAL_RED, points, 0)
        pygame.draw.polygon(self.image, CARNIVAL_GOLD, points, 5)
        
        if self.is_revealed and self.has_ball:
            # Draw the ball (White)
            pygame.draw.circle(self.image, CARNIVAL_WHITE, (self.size // 2, self.size - 30), 18) 


    def set_target(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y
        self.start_time = time.time()
        self.is_moving = True
        self.duration = SHUFFLE_DURATION_MS / 1000.0

    def update(self):
        if self.is_moving:
            elapsed = time.time() - self.start_time
            progress = min(elapsed / self.duration, 1.0)
            
            new_x = self.current_x + (self.target_x - self.current_x) * progress
            new_y = self.current_y

            self.rect.center = (new_x, new_y)

            if progress >= 1.0:
                self.is_moving = False
                self.current_x = self.target_x
                self.current_y = self.target_y

    def reveal(self, should_reveal=True):
        self.is_revealed = should_reveal
        self._draw_cup()


class ShellGameMiniGame:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.reset()

    def reset(self):
        self.state = "START_REVEAL"
        self.shuffle_count = 10
        self.current_shuffle = 0
        self.message = "Get ready to watch closely!"
        self.shuffle_pairs = []
        self.last_score_change = 0
        
        pygame.time.set_timer(SHUFFLE_EVENT, 0) 
        
        self.cup_x_positions = [
            SCREEN_WIDTH // 2 - 200,
            SCREEN_WIDTH // 2,
            SCREEN_WIDTH // 2 + 200
        ]

        self._setup_cups()
        self._initial_reveal_sequence()

    def _setup_cups(self):
        center_y = SCREEN_HEIGHT * 0.7
        ball_index = random.randint(0, 2)

        self.cups = []
        for i, x_pos in enumerate(self.cup_x_positions):
            cup = Cup(x_pos, center_y, size=160, has_ball=(i == ball_index)) 
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
        
        pygame.time.set_timer(SHUFFLE_EVENT, INITIAL_REVEAL_DURATION_MS, 1)


    def _start_shuffling(self):
        for cup in self.cups:
            cup.reveal(False)
            
        self.state = "SHUFFLING"
        self.current_shuffle = 0
        self.shuffle_pairs = self._generate_shuffle_pairs()
        self.message = f"Shuffling {self.shuffle_count} times... Keep your eyes on the ball!"
        
        pygame.time.set_timer(SHUFFLE_EVENT, SHUFFLE_DURATION_MS + 100)

    def _do_one_shuffle(self):
        if any(cup.is_moving for cup in self.cups):
            return

        if self.current_shuffle >= len(self.shuffle_pairs):
            pygame.time.set_timer(SHUFFLE_EVENT, 0)
            self.state = "WAITING_CHOICE"
            self.message = "Where is the ball? Click on a cup!"
            play_sound("clown_honk") # Audio: signals selection start
            return

        idx1, idx2 = self.shuffle_pairs[self.current_shuffle]
        
        cup1_obj = self.cups[idx1]
        cup2_obj = self.cups[idx2]
        
        target_x1, target_y1 = cup1_obj.current_x, cup1_obj.current_y
        target_x2, target_y2 = cup2_obj.current_x, cup2_obj.current_y

        cup1_obj.set_target(target_x2, target_y2)
        cup2_obj.set_target(target_x1, target_y1)
        
        self.cups[idx1], self.cups[idx2] = self.cups[idx2], self.cups[idx1]
        
        self.current_shuffle += 1

    def _check_choice(self, pos):
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
            
            for c in self.all_sprites:
                c.reveal(True)
                
            if chosen_cup.has_ball:
                score_to_report = 1000
                self.message = f"CONGRATS! You found the ball! +{score_to_report} Points! (Game resets soon)"
                play_sound("win_fanfare") # Audio: Triumphant fanfare
            else:
                score_to_report = 0
                self.message = "Too bad! The ball was not there. (Game resets soon)"
                play_sound("game_fail") # Audio: Failure
            
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

    def draw(self):
        # Background: Vibrant Red
        self.screen.fill(CARNIVAL_RED)
        
        # Target Area: Large Black Rectangle (The table)
        table_rect = pygame.Rect(SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT * 0.4, 700, SCREEN_HEIGHT * 0.5)
        pygame.draw.rect(self.screen, CARNIVAL_BLACK, table_rect)

        msg_text = self.font.render(self.message, True, CARNIVAL_GOLD)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, 50))
        
        self.all_sprites.draw(self.screen)

    def cleanup(self):
        pygame.time.set_timer(SHUFFLE_EVENT, 0)
        self.all_sprites.empty()

# ------------------------------------------------------------------------------
# PRIZES SCREEN CLASS
# ------------------------------------------------------------------------------

class PrizesScreen:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.reset()
        
    def reset(self):
        pass
        
    def handle_input(self, event):
        return 0
        
    def update(self, dt):
        return 0
        
    def draw(self, total_score):
        self.screen.fill(CARNIVAL_BLACK)
        
        big_font = pygame.font.Font(None, 60)
        title_surf = big_font.render("CARNIVAL PRIZE BOOTH", True, CARNIVAL_GOLD)
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80)))
        
        score_surf = self.font.render(f"YOUR SCORE: {total_score}", True, CARNIVAL_WHITE)
        self.screen.blit(score_surf, score_surf.get_rect(center=(SCREEN_WIDTH // 2, 140)))
        
        prize_list = [
            (100, "Small Keychain (100 Points)", total_score >= 100),
            (500, "Giant Lollipop (500 Points)", total_score >= 500),
            (1000, "Cuddly Teddy Bear (1000 Points)", total_score >= 1000),
            (2000, "Remote Control Car (2000 Points)", total_score >= 2000),
            (5000, "GRAND PRIZE! (5000 Points)", total_score >= 5000)
        ]
        
        y_pos = 220
        for _, prize, unlocked in prize_list:
            color = CARNIVAL_GOLD if unlocked else DARK_GRAY
            status = " [UNLOCKED!]" if unlocked else " [LOCKED]"
            
            prize_surf = self.font.render(prize + status, True, color)
            self.screen.blit(prize_surf, prize_surf.get_rect(center=(SCREEN_WIDTH // 2, y_pos)))
            y_pos += 40

        hint_surf = self.font.render("Press ESC to return to the Title Menu.", True, CARNIVAL_WHITE)
        self.screen.blit(hint_surf, hint_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))

    def cleanup(self):
        pass

# ==============================================================================
# ARCADE MANAGER (Main State Machine)
# ==============================================================================

class ArcadeManager:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Jay's Carnival Arcade")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.font, self.big_font = load_fonts() 

        self.total_score = 0
        self.state = STATE_TITLE
        
        # Start BGM loop
        play_sound("calliope")
        
        self.games = {
            STATE_DARTPOP: DartPopGame(self.screen, self.font),
            STATE_HOOPSHOT: HoopShotGame(self.screen, self.font),
            STATE_SPLASH: ClownSplashMiniGame(self.screen, self.font),
            STATE_SHELLGAME: ShellGameMiniGame(self.screen, self.font),
            STATE_PRIZES: PrizesScreen(self.screen, self.font),
        }
        
        self.game_names = {
            STATE_DARTPOP: "Dart Pop (Red Button)",
            STATE_HOOPSHOT: "Hoop Shot (Blue Button)",
            STATE_SPLASH: "Water Shooter (Green Button)",
            STATE_SHELLGAME: "Shell Game (Gold Button)",
        }
        
        self.short_game_names = {
            STATE_DARTPOP: "Dart Pop",
            STATE_HOOPSHOT: "Hoop Shot",
            STATE_SPLASH: "Water Shooter",
            STATE_SHELLGAME: "Shell Game",
        }
        
        self.game_button_colors = {
            STATE_DARTPOP: CARNIVAL_RED,
            STATE_HOOPSHOT: CARNIVAL_BLUE,
            STATE_SPLASH: BRIGHT_GREEN,
            STATE_SHELLGAME: CARNIVAL_GOLD,
        }
        
        self.button_rects = {}

    def _handle_input(self):
        score_change = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state != STATE_TITLE:
                    if self.state in self.games:
                        # Ensures continuous sounds stop and game state resets before returning to menu
                        self.games[self.state].cleanup() 
                        self.games[self.state].reset()
                    self.state = STATE_TITLE
                else:
                    self.running = False
            
            if self.state == STATE_TITLE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for action, rect in self.button_rects.items():
                        if rect.collidepoint(event.pos):
                            if action == "START":
                                self.state = STATE_MENU
                            elif action == "OPTIONS": # OPTIONS now defaults to the Game Hub
                                self.state = STATE_MENU
                            elif action == "PRIZES":
                                self.state = STATE_PRIZES
                            elif action == "EXIT":
                                self.running = False
                            break
            
            elif self.state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for game_state, rect in self.button_rects.items():
                        if rect.collidepoint(event.pos):
                            is_locked = (game_state == STATE_SHELLGAME and self.total_score < SHELL_GAME_UNLOCK_SCORE)
                            if not is_locked:
                                self.state = game_state
                                self.games[self.state].reset() 
                            break
            
            elif self.state in self.games:
                if event.type == SHUFFLE_EVENT or event.type == pygame.MOUSEBUTTONDOWN or event.type in (pygame.KEYDOWN, pygame.KEYUP):
                    score_change = self.games[self.state].handle_input(event)
                    self.total_score += score_change

    def _update_state(self, dt):
        score_change = 0
        if self.state in self.games:
            score_change = self.games[self.state].update(dt)
            self.total_score += score_change
            
    def _draw_title_menu(self):
        self.screen.fill(CARNIVAL_BLACK)
        
        # Title: "JAY'S CARNIVAL ARCADE" in Large, Gold text
        title_surf = self.big_font.render("JAY'S CARNIVAL ARCADE", True, CARNIVAL_GOLD)
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100)))
        
        y_start = 220
        button_height = 70
        button_width = 450
        
        title_menu_options = {
            "START": "START PLAYING (Game Hub)",
            "PRIZES": "VIEW PRIZES",
            "EXIT": "EXIT GAME",
        }
        # Options button is removed as "START" now leads to the Hub.
        
        self.button_rects = {}
        
        for i, (action, text) in enumerate(title_menu_options.items()):
            rect = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width // 2, 
                y_start + i * (button_height + 20), 
                button_width, 
                button_height
            )
            # Title buttons use CARNIVAL_RED
            draw_button(self.screen, text, rect, CARNIVAL_RED, CARNIVAL_WHITE, self.font)
            self.button_rects[action] = rect
            
        score_surf = self.font.render(f"TOTAL SCORE: {self.total_score}", True, CARNIVAL_WHITE)
        self.screen.blit(score_surf, score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)))

    def _draw_options_menu(self):
        self.screen.fill(CARNIVAL_BLACK)
        
        title_surf = self.big_font.render("GAME SELECTION HUB", True, CARNIVAL_GOLD)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surf, title_rect)
        
        score_surf = self.font.render(f"TOTAL SCORE: {self.total_score}", True, CARNIVAL_WHITE)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(score_surf, score_rect)

        y_start = 200
        button_height = 70
        button_width = 400
        
        self.button_rects = {}

        for i, (game_state, name) in enumerate(self.game_names.items()):
            rect = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width // 2, 
                y_start + i * (button_height + 20), 
                button_width, 
                button_height
            )
            
            is_locked = (game_state == STATE_SHELLGAME and self.total_score < SHELL_GAME_UNLOCK_SCORE)
            
            draw_button(
                self.screen, 
                name, 
                rect, 
                self.game_button_colors[game_state], 
                CARNIVAL_WHITE, 
                self.font,
                locked=is_locked
            )
            self.button_rects[game_state] = rect
            
        menu_hint = self.font.render("Press ESC to return to Title.", True, CARNIVAL_WHITE)
        self.screen.blit(menu_hint, menu_hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)))

    def _draw_game_score(self):
        game_name = self.short_game_names.get(self.state, "ARCADE GAME")
        
        # UI Readout in top corners using high-contrast Yellow (Gold) text
        time_text = f"TIMER: {int(pygame.time.get_ticks() / 1000)}"
        score_text = f"SCORE: {self.total_score}"
        
        time_surf = self.font.render(time_text, True, CARNIVAL_GOLD) 
        score_surf = self.font.render(score_text, True, CARNIVAL_GOLD)
        
        self.screen.blit(time_surf, (10, 10))
        self.screen.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 10, 10))
        
        game_name_surf = self.font.render(game_name, True, CARNIVAL_WHITE)
        game_name_rect = game_name_surf.get_rect(center=(SCREEN_WIDTH // 2, 10))
        self.screen.blit(game_name_surf, game_name_rect)

    def run(self):
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            self._handle_input()
            self._update_state(dt)

            self.screen.fill(CARNIVAL_BLACK)
            
            if self.state == STATE_TITLE:
                self._draw_title_menu()
            elif self.state == STATE_MENU:
                self._draw_options_menu()
            elif self.state == STATE_PRIZES:
                # Pass the score to the Prizes screen for dynamic display
                self.games[STATE_PRIZES].draw(self.total_score) 
            elif self.state in self.games:
                self.games[self.state].draw()
                self._draw_game_score()
            
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    arcade = ArcadeManager()
    arcade.run()

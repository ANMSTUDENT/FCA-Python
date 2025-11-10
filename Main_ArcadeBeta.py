import pygame
import sys
import random
import time
import math

# --- Global Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Colors (Simplified Palette for Beta) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# --- State Definitions ---
STATE_MENU = 0
STATE_DARTPOP = 1
STATE_HOOPSHOT = 2
STATE_SPLASH = 3
STATE_SHELLGAME = 4

# --- Utility Functions (Simplified button drawing) ---
def draw_button(screen, text, rect, color, text_color, font):
    """Draws a simple, unpolished rectangular button."""
    pygame.draw.rect(screen, color, rect, 0)
    pygame.draw.rect(screen, BLACK, rect, 2) # Simple black border
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

# ==============================================================================
# 1. DART POP GAME CLASS (Timing - Circular Sway)
# ==============================================================================

class DartPopGame:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.reset()
        self.message = "Press SPACE to throw the dart!"

    def reset(self):
        self.game_time = 0.0
        self.dart_thrown = False
        self.hit_result = None
        
        # Target properties
        self.center_x, self.center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.target_radius = 200
        self.bullseye_radius = 20
        self.arm_length = 150
        self.rotation_speed = 1.5

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not self.dart_thrown:
                self.dart_thrown = True
                angle = self.game_time * self.rotation_speed
                
                dart_x = self.center_x + self.arm_length * math.cos(angle)
                dart_y = self.center_y + self.arm_length * math.sin(angle)
                
                distance = math.hypot(dart_x - self.center_x, dart_y - self.center_y)
                
                if distance < self.bullseye_radius * 1.5:
                    self.hit_result = 'HIT'
                    self.message = "BULLSEYE! +300 Points! (Press R to Reset)"
                    return 300
                else:
                    self.hit_result = 'MISS'
                    self.message = "MISS! (Press R to Reset)"
                    return 0
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.reset()
            self.message = "Press SPACE to throw the dart!"
            
        return 0

    def update(self, dt):
        if not self.dart_thrown:
            self.game_time += dt 

    def draw(self):
        # 1. Draw Target Board (Simplified)
        pygame.draw.circle(self.screen, BLACK, (self.center_x, self.center_y), self.target_radius, 2) # Outline
        pygame.draw.circle(self.screen, RED, (self.center_x, self.center_y), self.target_radius * 0.5)
        pygame.draw.circle(self.screen, WHITE, (self.center_x, self.center_y), self.bullseye_radius) # Bullseye

        # 2. Draw Rotating Arm/Indicator (Simplified)
        angle = self.game_time * self.rotation_speed
        end_x = self.center_x + self.arm_length * math.cos(angle)
        end_y = self.center_y + self.arm_length * math.sin(angle)
        
        if not self.dart_thrown:
            # Simple arm line
            pygame.draw.line(self.screen, YELLOW, (self.center_x, self.center_y), (end_x, end_y), 3)
            # Simple square dart indicator
            pygame.draw.rect(self.screen, YELLOW, (int(end_x)-5, int(end_y)-5, 10, 10)) 
        
        # 3. Draw Dart Landing Spot 
        if self.dart_thrown:
            color = GREEN if self.hit_result == 'HIT' else RED
            pygame.draw.circle(self.screen, color, (int(end_x), int(end_y)), 10)
        
        # 4. Draw Message
        self._draw_message()
        
    def _draw_message(self):
        text_surf = self.font.render(self.message, True, YELLOW)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(text_surf, text_rect)

# ==============================================================================
# 2. HOOP SHOT GAME CLASS (Timing - Vertical Sway)
# ==============================================================================

class HoopShotGame:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.reset()
        self.message = "Press SPACE to shoot the ball!"

    def reset(self):
        self.game_time = 0.0
        self.shot_taken = False
        self.hit_result = None
        
        self.hoop_x = SCREEN_WIDTH - 150
        self.hoop_y_center = SCREEN_HEIGHT // 2
        self.hoop_size = 80
        
        self.target_y = self.hoop_y_center
        self.target_amplitude = 150
        self.target_speed = 2.0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not self.shot_taken:
                self.shot_taken = True
                
                hoop_top = self.hoop_y_center - self.hoop_size / 2
                hoop_bottom = self.hoop_y_center + self.hoop_size / 2
                
                if hoop_top <= self.target_y <= hoop_bottom:
                    self.hit_result = 'SWISH'
                    self.message = "SWISH! +500 Points! (Press R to Reset)"
                    return 500
                else:
                    self.hit_result = 'MISS'
                    self.message = "Airball! (Press R to Reset)"
                    return 0
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.reset()
            self.message = "Press SPACE to shoot the ball!"
            
        return 0

    def update(self, dt):
        if not self.shot_taken:
            self.game_time += dt
            offset = self.target_amplitude * math.sin(self.game_time * self.target_speed)
            self.target_y = self.hoop_y_center + offset

    def draw(self):
        # 1. Draw Hoop Structure (Simplified)
        pygame.draw.line(self.screen, WHITE, (self.hoop_x - 50, self.hoop_y_center), (self.hoop_x, self.hoop_y_center), 5) # Backboard arm
        pygame.draw.rect(self.screen, RED, (self.hoop_x, self.hoop_y_center - self.hoop_size/2, 5, self.hoop_size), 0) # Hoop zone

        # 2. Draw Moving Target (Simplified)
        target_center = (self.hoop_x - 100, int(self.target_y))
        pygame.draw.rect(self.screen, BLUE, (target_center[0]-15, target_center[1]-15, 30, 30), 0) # Square target

        # 3. Draw Shot Result
        if self.shot_taken:
            ball_pos = (self.hoop_x - 100, int(self.target_y))
            color = GREEN if self.hit_result == 'SWISH' else RED
            pygame.draw.circle(self.screen, color, ball_pos, 25)
        
        # 4. Draw Message
        self._draw_message()
        
    def _draw_message(self):
        text_surf = self.font.render(self.message, True, YELLOW)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(text_surf, text_rect)

# ==============================================================================
# 3. CLOWN SPLASH GAME CLASS (Continuous Input)
# ==============================================================================

class ClownSplashGame:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.reset()
        self.message = "Hold SPACE to shoot the water!"
        self.is_shooting = False

    def reset(self):
        self.target_position = 0
        self.MAX_TARGET_DISTANCE = 400
        self.ACCELERATION_RATE = 150 
        self.DECAY_RATE = 100        
        self.game_over = False

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.is_shooting = True
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            self.is_shooting = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.reset()
            self.message = "Hold SPACE to shoot the water!"
            self.is_shooting = False
            
        return 0

    def update(self, dt):
        score_change = 0
        
        if self.game_over:
            return 0
        
        if self.is_shooting:
            self.target_position += self.ACCELERATION_RATE * dt
            self.message = "WHOOSH! Water Stream Active..."
        else:
            self.target_position -= self.DECAY_RATE * dt

        self.target_position = max(0, min(self.target_position, self.MAX_TARGET_DISTANCE))
        
        if self.target_position >= self.MAX_TARGET_DISTANCE:
            score_change = 500
            self.message = f"CLOWN SPLASH! You Win! +{score_change} Points! (Press R to Reset)"
            self.game_over = True
            self.is_shooting = False

        return score_change

    def draw(self):
        # --- Target Track/Bar (Simplified) ---
        bar_x, bar_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        bar_width, bar_height = 40, self.MAX_TARGET_DISTANCE
        
        # Draw the main track outline
        track_rect = pygame.Rect(bar_x - bar_width // 2, bar_y - bar_height // 2, bar_width, bar_height)
        pygame.draw.rect(self.screen, WHITE, track_rect, 2) # Simple outline
        
        # --- Water Level Indicator ---
        current_water_height = int(self.target_position)
        water_base_y = track_rect.bottom 
        
        water_rect = pygame.Rect(
            track_rect.x, 
            water_base_y - current_water_height, 
            bar_width, 
            current_water_height
        )
        pygame.draw.rect(self.screen, BLUE, water_rect, 0)
        
        # --- Target Zone (Simplified to a square) ---
        target_zone_rect = pygame.Rect(track_rect.x, track_rect.top - 20, bar_width, 20)
        pygame.draw.rect(self.screen, GREEN, target_zone_rect, 0) # Solid green square
        
        # 4. Draw Message
        self._draw_message()
        
    def _draw_message(self):
        text_surf = self.font.render(self.message, True, YELLOW)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(text_surf, text_rect)


# ==============================================================================
# 4. SHELL GAME CLASS (Animation & Logic Tracking)
# ==============================================================================

class ShellCup(pygame.sprite.Sprite):
    def __init__(self, x, y, size=150, has_ball=False):
        super().__init__()
        self.size = size
        # Use a simple surface size
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.original_x = x
        self.original_y = y
        self.has_ball = has_ball
        self.is_moving = False
        self.is_revealed = False
        
        self.target_x = x
        self.duration = 1.0
        self.start_time = 0

        self._draw_cup()

    def _draw_cup(self):
        """Draws the cup as a simple rectangle with an outline (Downgraded)."""
        self.image.fill((0, 0, 0, 0)) # Transparent background
        
        cup_body = pygame.Rect(10, 20, self.size - 20, self.size - 20)
        pygame.draw.rect(self.image, RED, cup_body, 0) # Solid red rectangle
        pygame.draw.rect(self.image, BLACK, cup_body, 3) # Black outline
        
        if self.is_revealed and self.has_ball:
            # Draw ball slightly below the cup
            pygame.draw.circle(self.image, WHITE, (self.size // 2, self.size - 40), 15)

    def set_target(self, target_cup):
        self.target_x = target_cup.original_x
        self.start_time = time.time()
        self.is_moving = True

    def update(self):
        if self.is_moving:
            elapsed = time.time() - self.start_time
            progress = min(elapsed / self.duration, 1.0)
            
            new_x = self.original_x + (self.target_x - self.original_x) * progress
            self.rect.center = (new_x, self.original_y)

            if progress >= 1.0:
                self.is_moving = False
                self.original_x = self.target_x

    def reveal(self):
        self.is_revealed = True
        self._draw_cup()

class ShellGame:
    SHUFFLE_EVENT = pygame.USEREVENT + 1
    
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.reset()
        self.message = "Welcome to the Shell Game! Press R to replay."

    def reset(self):
        self.state = "START" 
        self.shuffle_count = 5 # Reduced shuffle count for faster testing
        self.current_shuffle = 0
        self.shuffle_pairs = []
        self._setup_cups()
        self.message = "Click to start the shuffle."

    def _setup_cups(self):
        center_y = SCREEN_HEIGHT * 0.7
        spacing = 200
        
        pos1_x = SCREEN_WIDTH // 2 - spacing
        pos2_x = SCREEN_WIDTH // 2
        pos3_x = SCREEN_WIDTH // 2 + spacing

        ball_index = random.randint(0, 2)

        self.cup_A = ShellCup(pos1_x, center_y, has_ball=(ball_index == 0))
        self.cup_B = ShellCup(pos2_x, center_y, has_ball=(ball_index == 1))
        self.cup_C = ShellCup(pos3_x, center_y, has_ball=(ball_index == 2))
        
        self.cups = [self.cup_A, self.cup_B, self.cup_C]
        self.all_sprites = pygame.sprite.Group(self.cup_A, self.cup_B, self.cup_C)
        
        pygame.time.set_timer(ShellGame.SHUFFLE_EVENT, 0)

    def _start_shuffling(self):
        self.state = "SHUFFLING"
        self.current_shuffle = 0
        self.shuffle_pairs = self._generate_shuffle_pairs()
        self.message = "Shuffling..."
        pygame.time.set_timer(ShellGame.SHUFFLE_EVENT, 1100) 

    def _generate_shuffle_pairs(self):
        pairs = []
        for _ in range(self.shuffle_count):
            indices = list(range(3))
            random.shuffle(indices)
            pairs.append(tuple(sorted(indices[:2])))
        return pairs

    def _do_one_shuffle(self):
        if self.current_shuffle >= len(self.shuffle_pairs):
            pygame.time.set_timer(ShellGame.SHUFFLE_EVENT, 0)
            self.state = "WAITING_CHOICE"
            self.message = "Where is the ball? Click on a cup!"
            return

        idx1, idx2 = self.shuffle_pairs[self.current_shuffle]
        cup1 = self.cups[idx1]
        cup2 = self.cups[idx2]

        temp_x1, temp_x2 = cup1.original_x, cup2.original_x 

        cup1.set_target(cup2)
        cup2.set_target(cup1) 

        cup1.original_x = temp_x2
        cup2.original_x = temp_x1

        self.current_shuffle += 1

    def _check_choice(self, pos):
        score_change = 0
        for cup in self.cups:
            if cup.rect.collidepoint(pos):
                self.state = "GAME_OVER"
                
                for c in self.cups:
                    c.reveal()
                
                if cup.has_ball:
                    score_change = 1000
                    self.message = f"CONGRATS! You found the ball! +{score_change} Points! (Press R to Reset)"
                else:
                    self.message = "Too bad! The ball was not there. (Press R to Reset)"
                
                # IMPORTANT BETA UX CHANGE: Do not auto-reset, require R keypress
                pygame.time.set_timer(ShellGame.SHUFFLE_EVENT, 0)
                return score_change
        return 0

    def handle_input(self, event):
        score_change = 0
        if event.type == ShellGame.SHUFFLE_EVENT:
            if self.state == "SHUFFLING":
                self._do_one_shuffle()
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.reset()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "START":
                self._start_shuffling()
            elif self.state == "WAITING_CHOICE":
                score_change = self._check_choice(event.pos)
        
        return score_change

    def update(self, dt):
        self.all_sprites.update()
        return 0

    def draw(self):
        # Draw the table (Simple Brown background)
        table_rect = pygame.Rect(0, SCREEN_HEIGHT * 0.5, SCREEN_WIDTH, SCREEN_HEIGHT * 0.5)
        pygame.draw.rect(self.screen, (100, 50, 0), table_rect) # Simple brown

        self.all_sprites.draw(self.screen)
        self._draw_message()
        
    def _draw_message(self):
        text_surf = self.font.render(self.message, True, YELLOW)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(text_surf, text_rect)


# ==============================================================================
# 5. ARCADE MANAGER (Main State Machine)
# ==============================================================================

class ArcadeManager:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Arcade Beta Prototype")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 40)

        self.total_score = 0
        self.state = STATE_MENU
        
        self.games = {
            STATE_DARTPOP: DartPopGame(self.screen, self.font),
            STATE_HOOPSHOT: HoopShotGame(self.screen, self.font),
            STATE_SPLASH: ClownSplashGame(self.screen, self.font),
            STATE_SHELLGAME: ShellGame(self.screen, self.font),
        }
        
        self.game_names = {
            STATE_DARTPOP: "1. Dart Pop",
            STATE_HOOPSHOT: "2. Hoop Shot",
            STATE_SPLASH: "3. Clown Splash",
            STATE_SHELLGAME: "4. Shell Game",
        }
        
        self.button_rects = {}

    def _handle_input(self):
        score_change = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state != STATE_MENU:
                    self.games[self.state].reset()
                    self.state = STATE_MENU
                else:
                    self.running = False
            
            if self.state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for game_state, rect in self.button_rects.items():
                        if rect.collidepoint(event.pos):
                            self.state = game_state
                            break
            
            elif self.state in self.games:
                score_change = self.games[self.state].handle_input(event)
                self.total_score += score_change

    def _update_state(self, dt):
        score_change = 0
        if self.state in self.games:
            score_change = self.games[self.state].update(dt)
            self.total_score += score_change
            
        return score_change

    def _draw_menu(self):
        # SIMPLIFIED MENU DRAWING for Beta
        title_surf = self.font.render("ARCADE BETA PROTOTYPE", True, YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surf, title_rect)
        
        score_surf = self.font.render(f"SCORE: {self.total_score}", True, WHITE)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(score_surf, score_rect)

        y_start = 220
        button_height = 60
        button_width = 300
        
        self.button_rects = {}

        for i, (game_state, name) in enumerate(self.game_names.items()):
            rect = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width // 2, 
                y_start + i * (button_height + 20), 
                button_width, 
                button_height
            )
            # Use simple white box button
            draw_button(self.screen, name, rect, WHITE, BLACK, self.font)
            self.button_rects[game_state] = rect
            
        exit_surf = self.font.render("Press ESC to quit.", True, WHITE)
        exit_rect = exit_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(exit_surf, exit_rect)

    def _draw_game_score(self):
        score_surf = self.font.render(f"Total Score: {self.total_score} | ESC to Menu", True, YELLOW)
        self.screen.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 10, 10))

    def run(self):
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            self._handle_input()
            self._update_state(dt)

            self.screen.fill(BLACK) 
            
            if self.state == STATE_MENU:
                self._draw_menu()
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

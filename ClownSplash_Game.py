import pygame
import sys
import time

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GREEN = (50, 200, 50)      # Target color
BLACK = (20, 20, 20)       # Background/Outline
YELLOW = (255, 255, 0)     # Text color
CYAN = (0, 150, 255)       # Water color
RED = (200, 50, 50)        # Clown/Success color
FPS = 60                   # Target frame rate

# --- Game Manager Class ---
class ClownSplashGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Clown Splash Mini-Game")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)

        # Game State
        self.score = 0
        self.message = "Hold SPACE to shoot!"
        
        # Continuous Input Mechanics
        self.is_shooting = False
        self.target_position = 0   # Current progress (0 to MAX_DISTANCE)
        self.MAX_TARGET_DISTANCE = 400
        # ACCELERATION_RATE is pixels advanced per second
        self.ACCELERATION_RATE = 150 
        self.DECAY_RATE = 100 
        
        self.last_time = time.time()


    def _handle_input(self):
        # Handle QUIT event only
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
    
    def _update_game_logic(self, dt):
        """
        Implements the continuous press mechanic using Delta Time (dt).
        This ensures movement is consistent regardless of FPS.
        """
        
        # Check current key states (Continuous check, not event-based)
        keys = pygame.key.get_pressed()
        self.is_shooting = keys[pygame.K_SPACE]

        # 1. ACCELERATION (KEY_PRESSED)
        if self.is_shooting:
            # Increase position based on acceleration rate * time elapsed (dt)
            self.target_position += self.ACCELERATION_RATE * dt
            
            # Update the message to show the action
            self.message = "WHOOSH! Water Stream Active..."
        
        # 2. DECAY (KEY_RELEASED)
        else:
            # Decrease position based on decay rate * time elapsed (dt)
            self.target_position -= self.DECAY_RATE * dt

        # 3. BOUND CHECKING
        # Ensure position does not fall below zero or exceed maximum
        self.target_position = max(0, min(self.target_position, self.MAX_TARGET_DISTANCE))
        
        # 4. WIN CONDITION CHECK
        if self.target_position >= self.MAX_TARGET_DISTANCE:
            self.score += 500
            self.message = f"CLOWN SPLASH! You Win! Score: {self.score}"
            # Reset for next round
            self.target_position = 0
            # Optional: Short pause to acknowledge win
            pygame.time.wait(500)
            
            return "GAME_WIN"

        return "GAME_IN_PROGRESS"


    def _draw_ui(self):
        """Draws the target track, water level, and UI elements."""
        
        # --- Target Track/Bar ---
        bar_x, bar_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        bar_width, bar_height = 40, self.MAX_TARGET_DISTANCE
        
        # Draw the main track (Black background)
        track_rect = pygame.Rect(bar_x - bar_width // 2, bar_y - bar_height // 2, bar_width, bar_height)
        pygame.draw.rect(self.screen, BLACK, track_rect, 0, border_radius=5)
        
        # --- Water Level Indicator ---
        # Current height is based on current position
        current_water_height = int(self.target_position)
        
        # Position of the base of the water bar
        water_base_y = track_rect.bottom 
        
        # Draw the moving CYAN water bar
        water_rect = pygame.Rect(
            track_rect.x, 
            water_base_y - current_water_height, # Start Y moves up as height increases
            bar_width, 
            current_water_height
        )
        pygame.draw.rect(self.screen, CYAN, water_rect, 0)
        
        # --- Target Zone (Clown/Bell) ---
        # Draw the target zone at the top
        target_zone_rect = pygame.Rect(track_rect.x, track_rect.top - 20, bar_width, 20)
        pygame.draw.rect(self.screen, GREEN, target_zone_rect, 0, border_radius=5)
        
        # Draw a simple Clown/Target image indicator
        pygame.draw.circle(self.screen, RED, (target_zone_rect.centerx, target_zone_rect.centery), 15)

        # --- Draw Score and Message ---
        score_text = self.font.render(f"SCORE: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (10, 10))

        msg_text = self.font.render(self.message, True, YELLOW)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 50))


    def run(self):
        while self.running:
            self._handle_input()
            
            # --- CALCULATE DT ---
            # Use real time to calculate delta time (time elapsed since last frame)
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = current_time
            
            # --- UPDATE ---
            self._update_game_logic(dt)

            # --- DRAW ---
            self.screen.fill(BLACK) # Use black for contrast
            self._draw_ui()
            
            # Update the full display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ClownSplashGame()
    game.run()

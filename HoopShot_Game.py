import pygame
import math
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLUE = (50, 150, 255)      # Main background color
DARK_BLUE = (25, 75, 125)  # Backboard/Rim color
GREEN = (50, 200, 50)      # Target success zone
RED = (200, 50, 50)        # Power bar indicator
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
FPS = 60

# --- SwayObject Class (Vertical Power Meter) ---
class SwayObject(pygame.sprite.Sprite):
    """
    Manages the aiming reticle's movement using a sine wave derived from
    real-world time (get_ticks), ensuring speed is constant regardless of FPS.
    """
    def __init__(self, center_x, center_y, amplitude, frequency, pattern, color=RED, size=20):
        super().__init__()
        self.image = pygame.Surface([size * 10, size], pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0)) # Fully transparent background
        self.rect = self.image.get_rect()
        self.start_x = center_x
        self.start_y = center_y
        self.rect.center = (center_x, center_y)

        self.amplitude = amplitude # Max distance from center
        self.frequency = frequency # Speed of oscillation
        self.pattern = pattern     # 1: Vertical (Power Bar), 2: Circular
        self.color = color
        self.size = size
        self.bar_height = size * 20

        # CRITICAL: Store the creation time for frame-rate independence
        self.time_offset = pygame.time.get_ticks()

    def update(self):
        """Calculates new vertical position based on elapsed time."""
        
        # 1. RETRIEVE FRAME-RATE INDEPENDENT TIME
        elapsed_time = pygame.time.get_ticks() - self.time_offset
        time_s = elapsed_time / 1000.0

        # 2. CALCULATE ANGLE BASED ON TIME
        angle = time_s * self.frequency * 2 * math.pi

        y_offset = 0

        # 3. APPLY TRIGONOMETRY FOR VERTICAL OSCILLATION
        if self.pattern == 1:
            # Pattern 1: Vertical Sway for Power Bar
            # This moves the center point up and down
            y_offset = math.sin(angle) * self.amplitude 
        
        # 4. UPDATE POSITION
        self.rect.center = (self.start_x, self.start_y + y_offset)
        
        # Draw the indicator (a line or circle) onto the bar
        self.image.fill((0, 0, 0, 0)) # Clear previous drawing

        # Draw the power indicator as a small circle
        pygame.draw.circle(self.image, self.color, (self.size * 5, self.size // 2), self.size // 2)

        # Return the offset value (useful for scoring)
        return y_offset 

# --- Game Manager Class ---
class HoopGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Hoop Shot Mini-Game")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)

        # Game State
        self.score = 0
        self.shot_result = "Press SPACE to shoot!"

        # Create Power Meter (Vertical Sway)
        bar_center_x = 100
        bar_center_y = SCREEN_HEIGHT // 2
        # Amplitude is half the total movement distance. 200 amplitude means 400 pixels total movement.
        self.power_meter = SwayObject(
            center_x=bar_center_x,
            center_y=bar_center_y,
            amplitude=150,      # Moves 150 pixels up and 150 down (300 total)
            frequency=1.0,      # One cycle (full up-down) per second (fast timing challenge)
            pattern=1,          # Vertical movement
            color=RED,
            size=20
        )
        self.all_sprites = pygame.sprite.Group(self.power_meter)
        
        # Define the perfect shot zone (Green Zone)
        # This zone is relative to the amplitude of 150
        self.perfect_zone_top = bar_center_y - 100
        self.perfect_zone_bottom = bar_center_y - 50 # This creates a 50 pixel success window
        self.perfect_zone_rect = pygame.Rect(
            bar_center_x - 10, self.perfect_zone_top, 20, self.perfect_zone_bottom - self.perfect_zone_top
        )


    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._check_shot()
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def _check_shot(self):
        """Checks if the power meter is in the success zone when shot."""
        
        # CRITICAL: Check the indicator's vertical center position
        indicator_y = self.power_meter.rect.centery
        
        # Check if the indicator is within the success zone
        if self.perfect_zone_top <= indicator_y <= self.perfect_zone_bottom:
            self.score += 250
            self.shot_result = f"SWISH! Perfect Shot! Score: {self.score}"
        elif self.power_meter.rect.centery < self.perfect_zone_top or self.power_meter.rect.centery > self.perfect_zone_bottom + 100:
            self.shot_result = "TOO WEAK OR TOO STRONG! Miss."
        else:
            self.shot_result = "Near Miss. Try to hit the green zone."
        
        # Reset the power meter's timer to start a new oscillation cycle
        self.power_meter.time_offset = pygame.time.get_ticks()

    def _draw_ui(self):
        """Draws the basketball scene and the power meter bar."""
        
        # 1. Draw Power Meter Track (the target bar)
        track_rect = pygame.Rect(
            self.power_meter.start_x - 10, 
            self.power_meter.start_y - self.power_meter.amplitude, 
            20, 
            self.power_meter.amplitude * 2
        )
        pygame.draw.rect(self.screen, DARK_BLUE, track_rect, 0, border_radius=5)
        
        # 2. Draw Success Zone (The Green Target)
        pygame.draw.rect(self.screen, GREEN, self.perfect_zone_rect, 0, border_radius=5)

        # 3. Draw Basketball Hoop (Simple Visual)
        hoop_x, hoop_y = SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2
        pygame.draw.rect(self.screen, WHITE, (hoop_x, hoop_y - 150, 10, 300)) # Backboard
        pygame.draw.circle(self.screen, RED, (hoop_x, hoop_y), 50, 10) # Rim

        # 4. Draw Score and Message
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

        msg_text = self.font.render(self.shot_result, True, YELLOW)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 50))


    def run(self):
        while self.running:
            self._handle_input()
            
            # --- UPDATE ---
            self.all_sprites.update()

            # --- DRAW ---
            self.screen.fill(BLUE) # Carnival Blue background
            self._draw_ui()
            self.all_sprites.draw(self.screen)
            
            # Update the full display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = HoopGame()
    game.run()

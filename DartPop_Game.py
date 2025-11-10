import pygame
import math
import sys
import time

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
RED = (200, 50, 50)
BLACK = (20, 20, 20)
YELLOW = (255, 255, 0)
BLUE = (50, 150, 255)
WHITE = (255, 255, 255)
FPS = 60 # Set to 60 for stability, but the SwayObject will be rate-independent

# --- SwayObject Class (The Core Feasibility Element) ---
class SwayObject(pygame.sprite.Sprite):
    """
    Manages the aiming reticle's movement using a sine wave derived from
    real-world time (get_ticks), making the speed constant regardless of FPS.
    """
    def __init__(self, center_x, center_y, amplitude, frequency, pattern, color=YELLOW, size=30):
        super().__init__()
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0)) # Fully transparent background
        self.rect = self.image.get_rect()
        self.start_x = center_x
        self.start_y = center_y
        self.rect.center = (center_x, center_y)

        self.amplitude = amplitude # Max distance from center
        self.frequency = frequency # Speed of oscillation (cycles per second)
        self.pattern = pattern     # 1: Vertical, 2: Circular (Dart Pop)
        self.color = color
        self.size = size

        # CRITICAL: Store the creation time for frame-rate independence
        self.time_offset = pygame.time.get_ticks()

    def update(self):
        """Calculates new position based on elapsed time."""
        
        # 1. RETRIEVE FRAME-RATE INDEPENDENT TIME
        # Elapsed time is the time since the object was created (in milliseconds)
        elapsed_time = pygame.time.get_ticks() - self.time_offset
        # Convert to seconds for math functions
        time_s = elapsed_time / 1000.0

        # 2. CALCULATE ANGLE BASED ON TIME
        # Angle increases linearly with time and frequency (cycles per second)
        angle = time_s * self.frequency * 2 * math.pi

        x_offset = 0
        y_offset = 0

        # 3. APPLY TRIGONOMETRY FOR OSCILLATION
        if self.pattern == 2:
            # Pattern 2: Circular Sway for Dart Aim (Dart Pop)
            x_offset = math.cos(angle) * self.amplitude
            y_offset = math.sin(angle) * self.amplitude
        elif self.pattern == 1:
            # Pattern 1: Vertical Sway (Used for the future Hoop Shot power bar)
            y_offset = math.sin(angle) * self.amplitude
            x_offset = 0

        # 4. UPDATE POSITION
        self.rect.center = (self.start_x + x_offset, self.start_y + y_offset)
        
        # Draw the crosshairs onto the image surface (cleared each frame by Surface.fill)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.line(self.image, self.color, (self.size // 2, 0), (self.size // 2, self.size), 2)
        pygame.draw.line(self.image, self.color, (0, self.size // 2), (self.size, self.size // 2), 2)


# --- Game Manager Class ---
class DartGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Dart Pop Mini-Game")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)

        # Game State
        self.score = 0
        self.aimer_shot_position = None
        self.message = "Press SPACE to throw!"

        # Create Sway Object (Circular Aim for Dart Pop)
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        # Amplitude (how far it moves), Frequency (how fast it moves)
        self.aimer = SwayObject(
            center_x=center_x,
            center_y=center_y,
            amplitude=150,      # Moves 150 pixels from the center
            frequency=0.5,      # Half a cycle (spin) per second (slow)
            pattern=2,          # Circular movement
            color=YELLOW,
            size=40
        )
        self.all_sprites = pygame.sprite.Group(self.aimer)
        self.target = pygame.Rect(center_x - 10, center_y - 10, 20, 20) # Center point target

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._check_hit()
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def _check_hit(self):
        """Checks the position of the aimer at the moment of key press."""
        # Get the current position of the aimer
        self.aimer_shot_position = self.aimer.rect.center
        
        # Check if the shot position overlaps with the tiny target center
        if self.target.collidepoint(self.aimer_shot_position):
            self.score += 100
            self.message = f"HIT! Score: {self.score}"
        else:
            self.message = "MISS! Try again."
        
        # Reset the aimer position slightly to show the shot occurred
        self.aimer.time_offset = pygame.time.get_ticks()

    def _draw_ui(self):
        """Draws scores, instructions, and the central target."""
        # Draw the main target area (Black square background)
        pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 200, 400, 400), border_radius=10)
        
        # Draw the target center (White Dot)
        pygame.draw.circle(self.screen, WHITE, self.target.center, 5)

        # Draw Score and Message
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        msg_text = self.font.render(self.message, True, YELLOW)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 50))


    def run(self):
        while self.running:
            self._handle_input()
            
            # --- UPDATE ---
            self.all_sprites.update()

            # --- DRAW ---
            self.screen.fill(RED) # Carnival Red background
            self._draw_ui()
            self.all_sprites.draw(self.screen)
            
            # Update the full display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = DartGame()
    game.run()

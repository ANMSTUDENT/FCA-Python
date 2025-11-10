import pygame
import sys
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
YELLOW = (255, 255, 0)     # Text color
BROWN = (139, 69, 19)      # Table color
RED = (200, 50, 50)        # Cup color
WHITE = (255, 255, 255)    # Ball color
FPS = 60                   # Target frame rate
SHUFFLE_EVENT = pygame.USEREVENT + 1 # Custom event for shuffle timer
SHUFFLE_DURATION_MS = 1000 # Time for one shuffle swap animation

# --- Cup Object Class ---
class Cup(pygame.sprite.Sprite):
    def __init__(self, x, y, size=150, has_ball=False):
        super().__init__()
        self.size = size
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.original_x = x # Used for target position during animation
        self.original_y = y
        self.has_ball = has_ball
        self.is_moving = False
        self.is_revealed = False
        self.color = RED
        
        # Animation properties
        self.target_x = x
        self.target_y = y
        self.start_time = 0
        self.duration = SHUFFLE_DURATION_MS / 1000.0 # Duration in seconds

        self._draw_cup()

    def _draw_cup(self):
        """Draws the cup as a simple, open U-shape."""
        self.image.fill((0, 0, 0, 0)) # Transparent background
        
        # Draw the main cup shape (simple trapezoid)
        points = [
            (5, self.size),
            (self.size - 5, self.size),
            (self.size - 25, 20),
            (25, 20)
        ]
        pygame.draw.polygon(self.image, self.color, points, 0)
        
        # Draw the ball if revealed (for win/loss display)
        if self.is_revealed and self.has_ball:
            # Draw ball slightly below the cup
            pygame.draw.circle(self.image, WHITE, (self.size // 2, self.size - 40), 15)

    def set_target(self, target_cup):
        """Sets up the animation parameters to move towards the target cup's position."""
        self.target_x = target_cup.rect.centerx
        self.target_y = target_cup.rect.centery
        self.start_time = time.time()
        self.is_moving = True

    def update(self):
        """Handles smooth movement animation."""
        if self.is_moving:
            elapsed = time.time() - self.start_time
            progress = min(elapsed / self.duration, 1.0) # Progress from 0 to 1
            
            # Use smooth step function for acceleration/deceleration (optional polish)
            # smooth_progress = progress * progress * (3 - 2 * progress) 
            smooth_progress = progress 

            # Interpolate position
            new_x = self.original_x + (self.target_x - self.original_x) * smooth_progress
            new_y = self.original_y # Y position stays constant

            self.rect.center = (new_x, new_y)

            if progress >= 1.0:
                self.is_moving = False
                # Update the original position to the new resting spot
                self.original_x = self.target_x
                self.original_y = self.target_y

    def reveal(self):
        """Reveals if the ball is under the cup."""
        self.is_revealed = True
        self._draw_cup()

# --- Game Manager Class ---
class ShellGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Shell Game Mini-Game")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)

        self.score = 0
        self.state = "START" # START, SHUFFLING, WAITING_CHOICE, GAME_OVER
        self.shuffle_count = 10 # Total number of swaps to perform
        self.current_shuffle = 0
        self.message = "Welcome to the Shell Game! Click to start."
        self.shuffle_pairs = []

        self._setup_cups()

    def _setup_cups(self):
        """Initializes the three cups with the ball under a random one."""
        center_y = SCREEN_HEIGHT * 0.7
        spacing = 200
        
        # Cup positions
        pos1_x = SCREEN_WIDTH // 2 - spacing
        pos2_x = SCREEN_WIDTH // 2
        pos3_x = SCREEN_WIDTH // 2 + spacing

        # Randomly choose which cup has the ball (0, 1, or 2)
        ball_index = random.randint(0, 2)

        self.cup_A = Cup(pos1_x, center_y, has_ball=(ball_index == 0))
        self.cup_B = Cup(pos2_x, center_y, has_ball=(ball_index == 1))
        self.cup_C = Cup(pos3_x, center_y, has_ball=(ball_index == 2))
        
        # Store cups in a list for easy indexing and swapping
        self.cups = [self.cup_A, self.cup_B, self.cup_C]
        self.all_sprites = pygame.sprite.Group(self.cup_A, self.cup_B, self.cup_C)
        
        self.cup_positions = {
            pos1_x: self.cup_A,
            pos2_x: self.cup_B,
            pos3_x: self.cup_C
        }


    def _start_shuffling(self):
        """Initiates the shuffling sequence."""
        self.state = "SHUFFLING"
        self.current_shuffle = 0
        self.shuffle_pairs = self._generate_shuffle_pairs()
        self.message = "Shuffling..."
        # Start the timer to trigger the SHUFFLE_EVENT repeatedly
        pygame.time.set_timer(SHUFFLE_EVENT, SHUFFLE_DURATION_MS + 100) # Slightly longer than animation

    def _generate_shuffle_pairs(self):
        """Generates a list of random (index A, index B) pairs for swapping."""
        pairs = []
        for _ in range(self.shuffle_count):
            indices = list(range(3))
            random.shuffle(indices)
            # Take the first two distinct indices
            pair = tuple(sorted(indices[:2]))
            pairs.append(pair)
        return pairs

    def _do_one_shuffle(self):
        """Performs one swap animation and updates the internal ball tracking."""
        if self.current_shuffle >= len(self.shuffle_pairs):
            # Shuffling complete
            pygame.time.set_timer(SHUFFLE_EVENT, 0) # Stop the timer
            self.state = "WAITING_CHOICE"
            self.message = "Where is the ball? Click on a cup!"
            return

        idx1, idx2 = self.shuffle_pairs[self.current_shuffle]
        cup1 = self.cups[idx1]
        cup2 = self.cups[idx2]

        # 1. Start the animation swap: Cup 1 moves to Cup 2's position and vice versa
        # Temporarily store target coordinates
        temp_x1, temp_x2 = cup1.original_x, cup2.original_x 

        # Set cup 1 to move to cup 2's original position
        cup1.set_target(cup2)
        # Set cup 2 to move to cup 1's previous position
        cup2.set_target(cup1) 

        # 2. CRITICAL: Update the internal original positions immediately for next swap logic
        # Swap the internal tracking of resting positions
        cup1.original_x = temp_x2
        cup2.original_x = temp_x1

        self.current_shuffle += 1

    def _check_choice(self, pos):
        """Checks if the player's mouse click hit the correct cup."""
        for cup in self.cups:
            if cup.rect.collidepoint(pos):
                cup.reveal() # Reveal the chosen cup
                self.state = "GAME_OVER"
                
                # Reveal the rest of the cups for clarity
                for c in self.cups:
                    c.reveal()
                
                if cup.has_ball:
                    self.score += 1000
                    self.message = f"CONGRATS! You found the ball! Score: {self.score}"
                else:
                    self.message = "Too bad! The ball was not there."
                
                # Transition to allow replay
                pygame.time.set_timer(SHUFFLE_EVENT, 1500, 1) # Wait 1.5 seconds then allow restart
                return

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            
            if event.type == SHUFFLE_EVENT:
                if self.state == "SHUFFLING":
                    self._do_one_shuffle()
                elif self.state == "GAME_OVER":
                    self.state = "START"
                    self._setup_cups()
                    self.message = "Play again? Click to start."
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "START":
                    self._start_shuffling()
                elif self.state == "WAITING_CHOICE":
                    self._check_choice(event.pos)

    def _draw_ui(self):
        """Draws the table, score, and message."""
        
        # Draw the table (bottom half of screen)
        table_rect = pygame.Rect(0, SCREEN_HEIGHT * 0.5, SCREEN_WIDTH, SCREEN_HEIGHT * 0.5)
        pygame.draw.rect(self.screen, BROWN, table_rect)

        # Draw Score and Message
        score_text = self.font.render(f"SCORE: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (10, 10))

        msg_text = self.font.render(self.message, True, YELLOW)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, 50))


    def run(self):
        while self.running:
            self._handle_input()
            
            # --- UPDATE ---
            self.all_sprites.update()

            # --- DRAW ---
            self.screen.fill(BLACK) 
            self._draw_ui()
            self.all_sprites.draw(self.screen)
            
            # Update the full display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ShellGame()
    game.run()

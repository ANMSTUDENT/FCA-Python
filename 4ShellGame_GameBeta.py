import pygame
import sys
import time
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
RED = (200, 50, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60
SHUFFLE_EVENT = pygame.USEREVENT + 1
SHUFFLE_DURATION_MS = 500
INITIAL_REVEAL_DURATION_MS = 1500

class Cup(pygame.sprite.Sprite):
    def __init__(self, x, y, size=150, has_ball=False):
        super().__init__()
        self.size = size
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.current_x = x
        self.current_y = y
        self.has_ball = has_ball
        self.is_moving = False
        self.is_revealed = False
        self.color = RED
        
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
        pygame.draw.polygon(self.image, self.color, points, 0)
        
        if self.is_revealed and self.has_ball:
            pygame.draw.circle(self.image, WHITE, (self.size // 2, self.size - 40), 15)

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

class ShellGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Shell Game Mini-Game")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)

        self.score = 0
        self.state = "START_REVEAL"
        self.shuffle_count = 10
        self.current_shuffle = 0
        self.message = "Get ready to watch closely!"
        self.shuffle_pairs = []
        
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
            cup = Cup(x_pos, center_y, has_ball=(i == ball_index))
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
        self.message = "Watch the ball!"
        
        pygame.time.set_timer(SHUFFLE_EVENT, INITIAL_REVEAL_DURATION_MS, 1)


    def _start_shuffling(self):
        for cup in self.cups:
            cup.reveal(False)
            
        self.state = "SHUFFLING"
        self.current_shuffle = 0
        self.shuffle_pairs = self._generate_shuffle_pairs()
        self.message = "Shuffling... Keep your eyes on the ball!"
        
        pygame.time.set_timer(SHUFFLE_EVENT, SHUFFLE_DURATION_MS + 100)

    def _generate_shuffle_pairs(self):
        pairs = []
        for _ in range(self.shuffle_count):
            indices = random.sample(range(3), 2)
            pairs.append(tuple(indices))
        return pairs

    def _do_one_shuffle(self):
        if any(cup.is_moving for cup in self.cups):
            return

        if self.current_shuffle >= len(self.shuffle_pairs):
            pygame.time.set_timer(SHUFFLE_EVENT, 0)
            self.state = "WAITING_CHOICE"
            self.message = "Where is the ball? Click on a cup!"
            return

        idx1, idx2 = self.shuffle_pairs[self.current_shuffle]
        cup1 = self.cups[idx1]
        cup2 = self.cups[idx2]

        target_x1, target_y1 = cup1.current_x, cup1.current_y
        target_x2, target_y2 = cup2.current_x, cup2.current_y

        cup1.set_target(target_x2, target_y2)
        cup2.set_target(target_x1, target_y1)

        self.cups[idx1], self.cups[idx2] = self.cups[idx2], self.cups[idx1]

        self.current_shuffle += 1

    def _check_choice(self, pos):
        if self.state != "WAITING_CHOICE":
            return
            
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
                self.score += 1000
                self.message = f"CONGRATS! You found the ball! Score: {self.score}"
            else:
                self.message = "Too bad! The ball was not there."
            
            pygame.time.set_timer(SHUFFLE_EVENT, 1500, 1)
            return

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            
            if event.type == SHUFFLE_EVENT:
                if self.state == "START_REVEAL":
                    self._start_shuffling()
                elif self.state == "SHUFFLING":
                    self._do_one_shuffle()
                elif self.state == "GAME_OVER":
                    self._setup_cups()
                    self._initial_reveal_sequence()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "WAITING_CHOICE":
                    self._check_choice(event.pos)

    def _draw_ui(self):
        self.screen.fill(BLACK)
        
        table_rect = pygame.Rect(0, SCREEN_HEIGHT * 0.5, SCREEN_WIDTH, SCREEN_HEIGHT * 0.5)
        pygame.draw.rect(self.screen, BROWN, table_rect)

        score_text = self.font.render(f"SCORE: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (10, 10))

        msg_text = self.font.render(self.message, True, YELLOW)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, 50))


    def run(self):
        while self.running:
            self._handle_input()
            
            self.all_sprites.update()

            self._draw_ui()
            
            self.all_sprites.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ShellGame()
    game.run()

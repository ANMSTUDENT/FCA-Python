import pygame
import sys
import random
import time
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 180, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (150, 0, 150)
ORANGE = (255, 165, 0)
GRAY = (50, 50, 50)

class DartPopGame:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.total_score = 0
        self.target_radius = 200      
        self.arm_length = 150         
        
        self.target_angle = 3 * math.pi / 2
        
        self.hit_angle_min = self.target_angle - 0.26
        self.hit_angle_max = self.target_angle + 0.26
        
        self.reset()
        self.message = "Press SPACE to throw the dart!"

    def generate_balloons(self):
        """Generates 4 balloons spaced out along the dart's circular path."""
        self.balloons = []
        
        target_radius = self.arm_length 
        
        
        balloon_angles = [
            0,                     
            math.pi / 2,           
            math.pi,               
            3 * math.pi / 2        
        ]
        
        colors = [RED, BLUE, YELLOW, PURPLE] 
        
        for i, angle in enumerate(balloon_angles):
            
            x = self.center_x + target_radius * math.cos(angle)
            y = self.center_y + target_radius * math.sin(angle)
            
            size = random.randint(18, 25)
            
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
                            
                
                if hit_balloon:
                    self.hit_result = 'HIT'
                    self.last_score_change = hit_score
                    self.message = f"POP! +{self.last_score_change} Points! (Press R to Reset)"
                    
                else:
                    
                    
                    if (self.hit_angle_min < normalized_angle < self.hit_angle_max) or \
                       (self.hit_angle_min < normalized_angle - 2 * math.pi < self.hit_angle_max):
                        
                        self.hit_result = 'NEAR_MISS'
                        self.last_score_change = 50 
                        self.message = f"Good Timing! +{self.last_score_change} Points! (Press R to Reset)"
                    else:
                        self.hit_result = 'MISS'
                        self.last_score_change = 0
                        self.message = "MISS! (Press R to Reset)"


        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if self.dart_thrown:
                self.total_score += self.last_score_change
                
                all_popped = all(b['hit'] for b in self.balloons)
                
                self.reset()
                
                if all_popped and self.last_score_change > 0:
                     self.message = f"Perfect Round! Total Score: {self.total_score}. Press SPACE to throw again!"
                else:
                     self.message = "Press SPACE to throw the dart!"
                
        return 0

    def update(self, dt):
        if not self.dart_thrown:
            self.game_time += dt

    def draw(self):
        
        pygame.draw.circle(self.screen, GRAY, (self.center_x, self.center_y), self.target_radius + 50, 0) 
        
        
        pygame.draw.circle(self.screen, ORANGE, (self.center_x, self.center_y), self.target_radius, 0)
        
        
        pygame.draw.circle(self.screen, GREEN, (self.center_x, self.center_y), self.target_radius * 0.5)
        
        
        pygame.draw.circle(self.screen, WHITE, (self.center_x, self.center_y), self.bullseye_radius)
        
        
        for balloon in self.balloons:
            if balloon['hit']:
                
                pygame.draw.circle(self.screen, BLACK, balloon['pos'], balloon['size'] + 3)
                pygame.draw.circle(self.screen, RED, balloon['pos'], balloon['size'] - 5)
            else:
                
                pygame.draw.circle(self.screen, balloon['color'], balloon['pos'], balloon['size'])

        
        
        angle = self.game_time * self.rotation_speed
        
        end_x = self.center_x + self.arm_length * math.cos(angle)
        end_y = self.center_y + self.arm_length * math.sin(angle)
        
        if not self.dart_thrown:
            
            pygame.draw.line(self.screen, YELLOW, (self.center_x, self.center_y), (end_x, end_y), 3)
            
            pygame.draw.circle(self.screen, YELLOW, (int(end_x), int(end_y)), 8)
        
        
        if self.dart_thrown:
            
            dart_x = self.center_x + self.arm_length * math.cos(angle)
            dart_y = self.center_y + self.arm_length * math.sin(angle)

            color = GREEN if self.hit_result != 'MISS' else RED
            
            pygame.draw.circle(self.screen, color, (int(dart_x), int(dart_y)), 12)
        
        
        self._draw_message()
        self._draw_score()
        
    def _draw_message(self):
        text_surf = self.font.render(self.message, True, YELLOW)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(text_surf, text_rect)

    def _draw_score(self):
        score_surf = self.font.render(f"SCORE: {self.total_score} | ESC to Quit", True, WHITE)
        self.screen.blit(score_surf, (10, 10))

def run_game():
    pygame.init()
    pygame.display.set_caption("Dart Pop Game Test")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 40)
    
    game = DartPopGame(screen, font)
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            game.handle_input(event)

        game.update(dt)

        screen.fill(BLACK)
        game.draw()
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()

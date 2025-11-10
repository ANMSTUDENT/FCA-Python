import pygame
import math
import sys
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLUE = (50, 150, 255)
DARK_BLUE = (25, 75, 125)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 140, 0)
FPS = 60

class SwayObject(pygame.sprite.Sprite):
    def __init__(self, center_x, center_y, amplitude, frequency, pattern, color=RED, size=20):
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
        pygame.draw.circle(self.image, self.color, (self.size * 5, self.size // 2), self.size // 2)

        return y_offset 


class Basketball(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, arc_type): 
        super().__init__()
        self.size = 40 
        self.image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, ORANGE, (self.size // 2, self.size // 2), self.size // 2)

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


class HoopGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Hoop Shot Mini-Game")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)

        self.score = 0
        self.shot_result = "Press SPACE to shoot!"

        self.bar_center_x = 100
        self.bar_center_y = SCREEN_HEIGHT // 2
        self.bar_amplitude = 150 
        
        self.power_meter = SwayObject(
            center_x=self.bar_center_x,
            center_y=self.bar_center_y,
            amplitude=self.bar_amplitude, 
            frequency=1.0,           
            pattern=1,               
            color=RED,
            size=20
        )

        self.all_sprites = pygame.sprite.Group(self.power_meter)
        
        self.shooter_x = 150 
        self.shooter_y = SCREEN_HEIGHT - 100 

        self.zone_height = 50 
        self.perfect_zone_top = 0
        self.perfect_zone_bottom = 0
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
        
        indicator_y = self.power_meter.rect.centery
        
        is_success = False
        arc_type = 'miss' 

        if self.perfect_zone_top <= indicator_y <= self.perfect_zone_bottom:
            self.score += 250
            self.shot_result = f"SWISH! Perfect Shot! Score: {self.score}"
            is_success = True
            arc_type = 'swish'
        else:
            zone_center_y = self.perfect_zone_top + (self.zone_height / 2)
            distance = abs(indicator_y - zone_center_y)
            
            if distance < self.zone_height * 2.5: 
                self.shot_result = "Near Miss. Try to hit the green zone."
            else:
                self.shot_result = "Way Off! Miss."
            
            arc_type = random.choice(['overshoot', 'undershoot'])

        new_ball = Basketball(self.shooter_x, self.shooter_y, arc_type)
        self.all_sprites.add(new_ball) 

        self.power_meter.time_offset = pygame.time.get_ticks()
        self._randomize_target_zone()

    def _draw_ui(self):
        
        track_rect = pygame.Rect(
            self.power_meter.start_x - 10, 
            self.power_meter.start_y - self.power_meter.amplitude, 
            20, 
            self.power_meter.amplitude * 2
        )
        pygame.draw.rect(self.screen, DARK_BLUE, track_rect, 0, border_radius=5)
        
        pygame.draw.rect(self.screen, GREEN, self.perfect_zone_rect, 0, border_radius=5)

        pygame.draw.circle(self.screen, WHITE, (self.shooter_x, self.shooter_y), 25)
        pygame.draw.circle(self.screen, DARK_BLUE, (self.shooter_x, self.shooter_y), 25, 3)

        hoop_center_x = SCREEN_WIDTH - 150 
        hoop_center_y = SCREEN_HEIGHT // 2 
        
        backboard_rect = (hoop_center_x, hoop_center_y - 75, 10, 150)
        pygame.draw.rect(self.screen, WHITE, backboard_rect)
        
        rim_rect = (hoop_center_x - 80, hoop_center_y - 15, 80, 30)
        pygame.draw.ellipse(self.screen, DARK_BLUE, rim_rect, 8)

        net_top_left = (hoop_center_x - 76, hoop_center_y)
        net_top_right = (hoop_center_x - 4, hoop_center_y)
        net_bottom_left = (hoop_center_x - 60, hoop_center_y + 60)
        net_bottom_right = (hoop_center_x - 20, hoop_center_y + 60)
        
        pygame.draw.line(self.screen, WHITE, net_top_left, net_bottom_left, 2)
        pygame.draw.line(self.screen, WHITE, net_top_right, net_bottom_right, 2)
        pygame.draw.line(self.screen, WHITE, net_bottom_left, net_bottom_right, 2)

        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

        msg_text = self.font.render(self.shot_result, True, YELLOW)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 50))


    def run(self):
        while self.running:
            self._handle_input()
            
            self.all_sprites.update()

            self.screen.fill(BLUE) 
            self._draw_ui()
            self.all_sprites.draw(self.screen)
            
            pygame.display.flip()
            
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = HoopGame()
    game.run()

import pygame
import sys
import time
import random
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CARNIVAL_RED = (200, 50, 50)
CARNIVAL_BLUE = (0, 150, 255)
WATER_CYAN = (100, 200, 255)
GOLD = (255, 215, 0)
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
FPS = 60
HIT_SCORE_INTERVAL = 0.5
MAX_SWING_ANGLE = math.pi / 4.5
SWING_SPEED = 1.0
STREAM_LENGTH = 450

def draw_clown_face_centered(surface, clown_size, hit, surface_size):
    surface.fill((0, 0, 0, 0))
    offset = (surface_size - clown_size) // 2
    center = (surface_size // 2, surface_size // 2)
    radius = clown_size // 2
    
    face_color = WHITE if not hit else (200, 200, 200)
    pygame.draw.circle(surface, face_color, center, radius)

    if hit:
        pygame.draw.circle(surface, WATER_CYAN, center, radius * 0.6)
        eye_y = offset + clown_size // 3
        pygame.draw.circle(surface, BLACK, (offset + clown_size // 3, eye_y), 4)
        pygame.draw.circle(surface, BLACK, (offset + clown_size - clown_size // 3, eye_y), 4)
        mouth_rect = pygame.Rect(offset + 5, offset + 3 * clown_size // 5, clown_size - 10, clown_size // 3)
        pygame.draw.arc(surface, BLACK, mouth_rect, math.pi * 1.1, math.pi * 1.9, 2)
    else:
        pygame.draw.circle(surface, CARNIVAL_RED, center, 8)
        smile_rect = pygame.Rect(offset + 5, offset + 5, clown_size - 10, clown_size - 10)
        pygame.draw.arc(surface, CARNIVAL_RED, smile_rect, 0, math.pi, 5)
        eye_y = offset + clown_size // 3
        pygame.draw.circle(surface, BLACK, (offset + clown_size // 3, eye_y), 3)
        pygame.draw.circle(surface, BLACK, (offset + clown_size - clown_size // 3, eye_y), 3)


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
        pygame.draw.rect(self.image, BLACK, (0, 0, self.barrel_width, self.barrel_height), 0, border_radius=5)
        
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

class ClownSplashGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Clown Splash Dunk Tank - Endless Mode")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 30)

        self.score = 0
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

    def _setup_clowns(self: 'ClownSplashGame'):
        clown_spacing = 150
        num_clowns = 3
        start_x = SCREEN_WIDTH // 2 - (num_clowns - 1) * clown_spacing / 2
        
        for i in range(num_clowns):
            x = start_x + (i * clown_spacing)
            clown = Clown(x, self.clown_target_y)
            self.clown_targets.add(clown)

    def _handle_input(self: 'ClownSplashGame'):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.space_down = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.space_down = False
                    self.last_spray_time = time.time()
                    self.is_in_cooldown = True
                    
                    for clown in self.clown_targets:
                        clown.reset()
                    self.message = "Refilling water tank (cooldown active)..."


    def _update_game_logic(self: 'ClownSplashGame', dt):
        
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
                self.score += 10
                self.last_score_time = current_time
                self.message = f"**BULLSEYE!** Hit ongoing! Water: {int(self.water_level)}%"
            
        elif self.water_level == 0.0 and self.space_down:
            self.message = "Tank **EMPTY**! Refilling..."
            
        # 3. Refill Logic (Refills if not spraying AND past cooldown)
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

        # NEW VISUAL LOGIC: Only the clown being hit right now gets the visual splash
        if is_spraying_now:
            for clown in self.clown_targets:
                is_hit = clown in clowns_being_hit_this_frame
                clown.update_visual(is_hit)
        else:
            pass

    def _draw_ui(self: 'ClownSplashGame'):
        self.screen.fill(CARNIVAL_BLUE)
        pygame.draw.rect(self.screen, CARNIVAL_RED, (0, self.clown_target_y + 30, SCREEN_WIDTH, 10))
        pygame.draw.rect(self.screen, CARNIVAL_RED, (0, SCREEN_HEIGHT - 70, SCREEN_WIDTH, 70))
        
        # Water Tank Visual (Gauge)
        tank_x, tank_y = 50, SCREEN_HEIGHT // 2 - 100
        tank_width, tank_height = 40, 200
        
        pygame.draw.rect(self.screen, BLACK, (tank_x-3, tank_y-3, tank_width+6, tank_height+6), 3, border_radius=5)
        
        fill_ratio = self.water_level / self.WATER_MAX
        fill_height = int(fill_ratio * tank_height)
        fill_rect = pygame.Rect(
            tank_x,
            tank_y + tank_height - fill_height,
            tank_width,
            fill_height
        )
        pygame.draw.rect(self.screen, WATER_CYAN, fill_rect, 0, border_radius=5)
        
        label = self.small_font.render("WATER", True, BLACK)
        self.screen.blit(label, (tank_x + tank_width // 2 - label.get_width() // 2, tank_y - 25))

        score_text = self.font.render(f"SCORE: {self.score}", True, GOLD)
        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

        display_message = self.message.replace('**', '').replace('**', '')
        msg_text = self.small_font.render(display_message, True, GOLD)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 30))

    def run(self: 'ClownSplashGame'):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self._handle_input()
            self._update_game_logic(dt)
            
            # DRAW
            self._draw_ui()
            
            self.water_gun.draw_stream(self.screen)
            self.clown_targets.draw(self.screen)
            self.screen.blit(self.water_gun.image, self.water_gun.rect)
            
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ClownSplashGame()
    game.run()

# Carnival Games Beta
# Jayce McGibbon
# 12/11/2025

import pygame
import sys
import time
import random
import math

# Core display configuration: screen size and frame timing
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Unified color palette: consistent carnival-themed colors used across all games
# Use these named tuples to keep visual language consistent and make tweaks easy.
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
BLUE = (50, 150, 255)
DARK_BLUE = (25, 75, 125)
PURPLE = (150, 0, 150)
ORANGE = (255, 140, 0)
GRAY = (50, 50, 50)
CARNIVAL_RED = RED
CARNIVAL_BLUE = (0, 150, 255)
WATER_CYAN = (100, 200, 255)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)

# Game state identifiers: used by ArcadeManager to switch modes
STATE_MENU = 0
STATE_DARTPOP = 1
STATE_HOOPSHOT = 2
STATE_SPLASH = 3
STATE_SHELLGAME = 4

# Gameplay tuning constants: quick-to-change knobs for balancing
HIT_SCORE_INTERVAL = 0.5       # seconds between continuous scoring ticks in splash
MAX_SWING_ANGLE = math.pi / 4.5
SWING_SPEED = 1.0
STREAM_LENGTH = 450

# Event identifiers and durations (kept for extensibility)
SHUFFLE_EVENT = pygame.USEREVENT + 1
SHUFFLE_DURATION_MS = 500
INITIAL_REVEAL_DURATION_MS = 1500


# draw_button: draws a simple rectangular button with text (menu UI)
def draw_button(screen, text, rect, color, text_color, font):
    pygame.draw.rect(screen, color, rect, 0)
    pygame.draw.rect(screen, BLACK, rect, 2)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


# DartPopGame: manages the dart-and-balloons mini-game (timing + aim)
class DartPopGame:
    # __init__: initialize game state and visual parameters
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.target_radius = 200
        self.arm_length = 150
        self.target_angle = 3 * math.pi / 2
        self.hit_angle_min = self.target_angle - 0.26
        self.hit_angle_max = self.target_angle + 0.26
        self.reset()
        self.message = "Press SPACE to throw the dart!"

    # generate_balloons: place balloons around the rotating arm; colors follow palette
    def generate_balloons(self):
        self.balloons = []
        target_radius = self.arm_length
        balloon_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        colors = [RED, BLUE, YELLOW, PURPLE]
        for i, angle in enumerate(balloon_angles):
            x = self.center_x + target_radius * math.cos(angle)
            y = self.center_y + target_radius * math.sin(angle)
            size = random.randint(18, 25)
            color = colors[i]
            self.balloons.append({'pos': (int(x), int(y)), 'size': size, 'color': color, 'hit': False})

    # reset: reset internal game variables for a fresh round
    def reset(self):
        self.game_time = 0.0
        self.dart_thrown = False
        self.hit_result = None
        self.last_score_change = 0
        self.center_x, self.center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.bullseye_radius = 20
        self.rotation_speed = 1.5 * random.choice([1, -1])
        self.generate_balloons()

    # handle_input: process events and return score gained (if any)
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
                        score_to_report = 0

        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if self.dart_thrown:
                all_popped = all(b['hit'] for b in self.balloons)
                if all_popped and self.last_score_change > 0:
                    self.reset()
                    self.message = f"Perfect Round! Press SPACE to throw again!"
                else:
                    self.reset()
                    self.message = "Press SPACE to throw the dart!"
        return score_to_report

    # update: advance game time when dart not thrown
    def update(self, dt):
        if not self.dart_thrown:
            self.game_time += dt
        return 0

    # draw: render the target, balloons, arm, and dart (visuals use unified palette)
    def draw(self):
        self.screen.fill(BLACK)
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

    # _draw_message: render the game's status message in header area
    def _draw_message(self):
        text_surf = self.font.render(self.message, True, YELLOW)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(text_surf, text_rect)

    # cleanup: placeholder for any teardown
    def cleanup(self):
        pass


# SwayObject: vertical sway indicator used as a power meter (visual helper)
class SwayObject(pygame.sprite.Sprite):
    # __init__: configure sway parameters and visuals
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

    # update: compute current vertical offset and redraw indicator
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


# Basketball: simple projectile representing a thrown ball (trajectory tuned by arc type)
class Basketball(pygame.sprite.Sprite):
    # __init__: set up ball visual and trajectory parameters
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

    # update: move ball along a parabolic arc and remove when off-screen
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


# HoopShotGame: manages the hoop-shot mini-game (power meter + arc)
class HoopShotGame:
    # __init__: initialize visuals, sprites, and zone
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.reset()

    # reset: prepare meter, sprites, and target zone
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
            color=RED,
            size=20
        )

        self.all_sprites = pygame.sprite.Group(self.power_meter)
        self.shooter_x = 150
        self.shooter_y = SCREEN_HEIGHT - 100
        self.perfect_zone_rect = pygame.Rect(0, 0, 0, 0)
        self._randomize_target_zone()

    # _randomize_target_zone: position the green scoring band
    def _randomize_target_zone(self):
        min_top_y = self.bar_center_y - self.bar_amplitude
        max_top_y = self.bar_center_y + self.bar_amplitude - self.zone_height
        self.perfect_zone_top = random.randint(min_top_y, max_top_y)
        self.perfect_zone_bottom = self.perfect_zone_top + self.zone_height
        self.perfect_zone_rect = pygame.Rect(
            self.bar_center_x - 10, self.perfect_zone_top, 20, self.zone_height
        )

    # _check_shot: evaluate shot quality and spawn a basketball arc
    def _check_shot(self):
        score_to_report = 0
        indicator_y = self.power_meter.rect.centery
        arc_type = 'miss'

        if self.perfect_zone_top <= indicator_y <= self.perfect_zone_bottom:
            score_to_report = 250
            self.shot_result = f"SWISH! Perfect Shot! +{score_to_report} Points!"
            arc_type = 'swish'
        else:
            zone_center_y = self.perfect_zone_top + (self.zone_height / 2)
            distance = abs(indicator_y - zone_center_y)

            if distance < self.zone_height * 2.5:
                self.shot_result = "Near Miss. Try to hit the green zone."
            else:
                self.shot_result = "Way Off! Miss."

            score_to_report = 0
            arc_type = random.choice(['overshoot', 'undershoot'])

        new_ball = Basketball(self.shooter_x, self.shooter_y, arc_type)
        self.all_sprites.add(new_ball)
        self.power_meter.time_offset = pygame.time.get_ticks()
        self._randomize_target_zone()

        return score_to_report

    # handle_input: respond to player input and return score
    def handle_input(self, event):
        score_change = 0
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            score_change = self._check_shot()
        return score_change

    # update: update sprites and cleanup finished balls
    def update(self, dt):
        self.all_sprites.update()
        for sprite in self.all_sprites:
            if isinstance(sprite, Basketball) and not sprite.in_flight and sprite.alive():
                sprite.kill()
        return 0

    # draw: render meter, zone, shooter, hoop, and sprites using consistent colors
    def draw(self):
        self.screen.fill(BLUE)

        track_rect = pygame.Rect(
            self.power_meter.start_x - 10, self.power_meter.start_y - self.power_meter.amplitude, 20, self.power_meter.amplitude * 2
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

        self.all_sprites.draw(self.screen)

        msg_text = self.font.render(self.shot_result, True, YELLOW)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 50))

    # cleanup: clear sprites
    def cleanup(self):
        self.all_sprites.empty()


# draw_clown_face_centered: helper draws a clown face; used by Clown sprite (visual consistency)
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


# Clown: sprite representing a target clown face in the splash game
class Clown(pygame.sprite.Sprite):
    # __init__: create visual surface and initial state
    def __init__(self, center_x, center_y, size=60):
        super().__init__()
        self.clown_size = size
        self.visual_size = size + 20
        self.image = pygame.Surface([self.visual_size, self.visual_size], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(center_x, center_y))
        self.hit = False
        self.visual_hit = False
        self._draw()

    # _draw: render the clown visual using draw_clown_face_centered helper
    def _draw(self):
        draw_clown_face_centered(self.image, self.clown_size, self.visual_hit, self.visual_size)

    # mark_hit: record a hit for scoring logic
    def mark_hit(self):
        self.hit = True
        return True

    # update_visual: toggle visual hit based on stream collision
    def update_visual(self, is_hit_by_stream):
        if is_hit_by_stream:
            if not self.visual_hit:
                self.visual_hit = True
                self._draw()
        else:
            if self.visual_hit:
                self.visual_hit = False
                self._draw()

    # is_hit_visual: report whether currently shown as hit
    def is_hit_visual(self):
        return self.visual_hit

    # reset: clear hit state and redraw
    def reset(self):
        self.hit = False
        self.visual_hit = False
        self._draw()


# WaterGun: manages stream aiming, position, and rendering (key feature in ClownSplash)
class WaterGun(pygame.sprite.Sprite):
    # __init__: set pivot, visuals, and stream buffering surface
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

    # update_position: swing the gun pivot and compute stream target coordinates (uses SWING_SPEED)
    def update_position(self, dt):
        self.current_angle += SWING_SPEED * dt
        swing_angle = math.sin(self.current_angle) * MAX_SWING_ANGLE
        self.current_stream_x = self.pivot_x + STREAM_LENGTH * math.sin(swing_angle)
        self.current_stream_y = self.pivot_y - STREAM_LENGTH * math.cos(swing_angle)

    # update_stream: draw stream into an offscreen surface and compute hit x (visual + collision)
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

    # draw_stream: blit the buffered stream onto the main surface
    def draw_stream(self, surface):
        if self.is_spraying:
            surface.blit(self.stream_image, self.stream_rect)


# ClownSplashMiniGame: manages water, clowns, scoring, and visuals (aim + sustain mechanics)
class ClownSplashMiniGame:
    # __init__: configure fonts and reset state
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.small_font = pygame.font.Font(None, 30)
        self.reset()

    # reset: set water, rates, clowns, and gun to initial values
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

    # _setup_clowns: create a row of clown targets
    def _setup_clowns(self):
        self.clown_targets.empty()
        clown_spacing = 150
        num_clowns = 3
        start_x = SCREEN_WIDTH // 2 - (num_clowns - 1) * clown_spacing / 2

        for i in range(num_clowns):
            x = start_x + (i * clown_spacing)
            clown = Clown(x, self.clown_target_y)
            self.clown_targets.add(clown)

    # handle_input: track SPACE press/releases and manage cooldown start
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

                for clown in self.clown_targets:
                    clown.reset()
                self.message = "Refilling water tank (cooldown active)..."

        return score_change

    # update: main game loop logic for spraying, refill, cooldown, scoring
    def update(self, dt):
        score_to_report = 0
        current_time = time.time()
        self.water_gun.update_position(dt)

        is_spraying_now = False
        clowns_being_hit_this_frame = []

        time_since_spray = current_time - self.last_spray_time
        if self.is_in_cooldown and time_since_spray >= self.COOLDOWN_TIME:
            self.is_in_cooldown = False

        if self.space_down and not self.is_in_cooldown and self.water_level > 0:
            self.water_level -= self.SPRAY_RATE * dt
            self.water_level = max(0.0, self.water_level)
            self.message = f"Spraying! Water: {int(self.water_level)}%"
            is_spraying_now = True

            for clown in self.clown_targets:
                if abs(clown.rect.centerx - self.water_gun.hit_stream_x) < clown.clown_size / 2:
                    clown.mark_hit()
                    clowns_being_hit_this_frame.append(clown)

            if clowns_being_hit_this_frame and current_time - self.last_score_time >= HIT_SCORE_INTERVAL:
                score_to_report = 10
                self.last_score_time = current_time
                self.message = f"**BULLSEYE!** Hit ongoing! Water: {int(self.water_level)}%"

        elif self.water_level == 0.0 and self.space_down:
            self.message = "Tank **EMPTY**! Refilling..."

        if not is_spraying_now and self.water_level < self.WATER_MAX and not self.is_in_cooldown:
            self.water_level += self.REFILL_RATE * dt
            self.water_level = min(self.WATER_MAX, self.water_level)

            if self.water_level == self.WATER_MAX and not self.space_down:
                self.message = "Tank fully charged. Hold **SPACE** to spray water!"
            else:
                self.message = "Refilling water tank..."

        self.water_gun.is_spraying = is_spraying_now
        water_ratio = self.water_level / self.WATER_MAX
        self.water_gun.update_stream(self.clown_target_y, water_ratio)

        for clown in self.clown_targets:
            is_hit = clown in clowns_being_hit_this_frame
            clown.update_visual(is_hit)

        return score_to_report

    # draw: render background, tank gauge, message, stream, and clowns
    def draw(self):
        self.screen.fill(CARNIVAL_BLUE)
        pygame.draw.rect(self.screen, CARNIVAL_RED, (0, self.clown_target_y + 30, SCREEN_WIDTH, 10))
        pygame.draw.rect(self.screen, CARNIVAL_RED, (0, SCREEN_HEIGHT - 70, SCREEN_WIDTH, 70))

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

        display_message = self.message.replace('**', '').replace('**', '')
        msg_text = self.font.render(display_message, True, GOLD)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 30))

        self.water_gun.draw_stream(self.screen)
        self.clown_targets.draw(self.screen)
        self.screen.blit(self.water_gun.image, self.water_gun.rect)

    # cleanup: clear clown group resources
    def cleanup(self):
        self.clown_targets.empty()


# ShellGamePlaceholder: minimal placeholder for removed shell game (keeps menu option stable)
class ShellGamePlaceholder:
    # __init__: set messages and reset
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.message = "SHELL GAME (temporarily removed in this beta)."
        self.sub_message = "Thanks for testing — the full Shell Game will be added soon."
        self.reset()

    # reset: set show time (placeholder)
    def reset(self):
        self.show_time = time.time()

    # handle_input: placeholder input handler
    def handle_input(self, event):
        return 0

    # update: no dynamic game logic
    def update(self, dt):
        return 0

    # draw: display placeholder messages
    def draw(self):
        self.screen.fill(BLACK)
        title = self.font.render("SHELL GAME - TEMPORARILY REMOVED", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        sub = self.font.render(self.sub_message, True, WHITE)
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        note = self.font.render("Press ESC to return to the Menu.", True, GOLD)
        self.screen.blit(note, (SCREEN_WIDTH // 2 - note.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    # cleanup: no teardown required
    def cleanup(self):
        pass


# ArcadeManager: top-level state machine managing menu and games (central coordinator)
class ArcadeManager:
    # __init__: initialize Pygame, fonts, games, and menu data
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("The Carnival Arcade")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Font used for most UI; change here to affect all text sizes.
        self.font = pygame.font.Font(None, 32)

        self.total_score = 0
        self.state = STATE_MENU

        # Instantiate game modules; each exposes handle_input/update/draw/cleanup
        self.games = {
            STATE_DARTPOP: DartPopGame(self.screen, self.font),
            STATE_HOOPSHOT: HoopShotGame(self.screen, self.font),
            STATE_SPLASH: ClownSplashMiniGame(self.screen, self.font),
            STATE_SHELLGAME: ShellGamePlaceholder(self.screen, self.font),
        }

        # Menu and header labels (short and long forms)
        self.game_names = {
            STATE_DARTPOP: "1. Dart Pop (Timing/Balloons)",
            STATE_HOOPSHOT: "2. Hoop Shot (Timing/Sway)",
            STATE_SPLASH: "3. Clown Splash (Aim/Spray)",
            STATE_SHELLGAME: "4. Shell Game (Watch Closely)",
        }

        self.short_game_names = {
            STATE_DARTPOP: "Dart Pop",
            STATE_HOOPSHOT: "Hoop Shot",
            STATE_SPLASH: "Clown Splash",
            STATE_SHELLGAME: "Shell Game",
        }

        self.button_rects = {}

    # _handle_input: global event loop and dispatch to current game or menu
    def _handle_input(self):
        score_change = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state != STATE_MENU:
                    current_game = self.games[self.state]
                    try:
                        current_game.cleanup()
                        current_game.reset()
                    except Exception:
                        pass
                    self.state = STATE_MENU
                else:
                    self.running = False

            if self.state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for game_state, rect in self.button_rects.items():
                        if rect.collidepoint(event.pos):
                            self.state = game_state
                            try:
                                self.games[self.state].reset()
                            except Exception:
                                pass
                            break

            elif self.state in self.games:
                if event.type == SHUFFLE_EVENT or event.type == pygame.MOUSEBUTTONDOWN or event.type in (pygame.KEYDOWN, pygame.KEYUP):
                    score_change = self.games[self.state].handle_input(event)
                    self.total_score += score_change

    # _update_state: update current game and accumulate score
    def _update_state(self, dt):
        score_change = 0
        if self.state in self.games:
            score_change = self.games[self.state].update(dt)
            self.total_score += score_change

    # _draw_menu: render main menu with buttons and total score
    def _draw_menu(self):
        self.screen.fill(BLACK)
        title_surf = self.font.render("THE CARNIVAL ARCADE", True, YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surf, title_rect)

        score_surf = self.font.render(f"TOTAL SCORE: {self.total_score}", True, WHITE)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(score_surf, score_rect)

        y_start = 220
        button_height = 60
        button_width = 400

        self.button_rects = {}

        for i, (game_state, name) in enumerate(self.game_names.items()):
            rect = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width // 2,
                y_start + i * (button_height + 20),
                button_width,
                button_height
            )
            draw_button(self.screen, name, rect, WHITE, BLACK, self.font)
            self.button_rects[game_state] = rect

        exit_surf = self.font.render("Press ESC to quit.", True, WHITE)
        exit_rect = exit_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(exit_surf, exit_rect)

    # _draw_game_score: render compact in-game header with game name and quick control hint
    def _draw_game_score(self):
        game_name = self.short_game_names.get(self.state, "ARCADE GAME")
        score_surf = self.font.render(f"{game_name} | ESC to Menu", True, GOLD)
        self.screen.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 10, 10))

    # run: main loop for the arcade manager (drives input/update/draw)
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

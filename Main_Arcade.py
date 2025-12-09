import pygame
import sys
import time
import random
import math
from typing import List

# --- Global Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
SHELL_GAME_UNLOCK_SCORE = 500
PLAY_AREA_MARGIN = 50

# --- Colors (Carnival palette) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (80, 80, 80)

CARNIVAL_RED = (200, 50, 50)
CARNIVAL_YELLOW = (255, 215, 0)
HOOP_BLUE = (0, 150, 255)
SPLASH_GREEN = (50, 200, 50)
UI_BRIGHT_YELLOW = (255, 255, 0)
MENU_DARK_BLUE = (10, 10, 40)

OG_ORANGE = (255, 140, 0)
OG_BROWN = (139, 69, 19)
OG_WATER_CYAN = (100, 200, 255)

# --- Game States ---
STATE_MENU = 0
STATE_DARTPOP = 1
STATE_HOOPSHOT = 2
STATE_SPLASH = 3
STATE_SHELLGAME = 4
STATE_PRIZES = 5
STATE_STATS = 6

# --- Game constants ---
HIT_SCORE_INTERVAL = 0.5
MAX_SWING_ANGLE = math.pi / 4.5
SWING_SPEED = 1.0
STREAM_LENGTH = 450

SHUFFLE_EVENT = pygame.USEREVENT + 1
SHUFFLE_DURATION_MS = 500
INITIAL_REVEAL_DURATION_MS = 1500

# --- Prize list ---
PRIZES = [
    {"name": "Teddy Bear", "cost": 500, "icon": "🧸"},
    {"name": "Mini Robot", "cost": 1500, "icon": "🤖"},
    {"name": "Giant Lollipop", "cost": 2500, "icon": "🍭"},
    {"name": "VR Headset", "cost": 5000, "icon": "👓"},
    {"name": "Electric Scooter", "cost": 10000, "icon": "🛴"},
    {"name": "New Car", "cost": 50000, "icon": "🚗"},
]

# --- Utility functions ---


def safe_font(name=None, size=24, bold=False):
    """Return a pygame Font object with fallbacks."""
    try:
        if name:
            return pygame.font.SysFont(name, size, bold=bold)
        else:
            return pygame.font.Font(None, size)
    except Exception:
        return pygame.font.Font(pygame.font.get_default_font(), size)


def wrap_text(font: pygame.font.Font, text: str, max_width: int) -> List[str]:
    """Wrap text to fit max_width using the provided font; returns list of lines."""
    words = text.split(' ')
    lines = []
    if not words:
        return ['']
    current_line = words[0]
    for w in words[1:]:
        test_line = current_line + ' ' + w
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = w
    lines.append(current_line)
    return lines


def draw_button(surface, text, rect, color, text_color, font, locked=False):
    """Draw a stylized carnival button (background, border, label)."""
    base_color = DARK_GRAY if locked else color

    base_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    # subtle vertical gradient
    for y in range(rect.height):
        t = y / rect.height
        r = int(base_color[0] * (0.9 + 0.1 * (1 - t)))
        g = int(base_color[1] * (0.9 + 0.1 * (1 - t)))
        b = int(base_color[2] * (0.9 + 0.1 * (1 - t)))
        pygame.draw.line(base_surf, (r, g, b), (0, y), (rect.width, y))
    surface.blit(base_surf, rect.topleft)

    # drop shadow
    shadow_rect = rect.move(4, 4)
    shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    shadow_surf.fill((0, 0, 0, 80))
    surface.blit(shadow_surf, shadow_rect.topleft)

    # border
    border_color = CARNIVAL_YELLOW if not locked else BLACK
    pygame.draw.rect(surface, border_color, rect, 3, border_radius=15)

    # label
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


# --- Pygame initialization ---
pygame.init()
try:
    pygame.mixer.init()
except Exception:
    # audio is optional; continue without sound if init fails
    pass

pygame.display.set_caption("Jay's Carnival Arcade - Upgraded")


class SoundManager:
    """Minimal sound manager that simulates audio events if not using real files."""
    def __init__(self):
        self.is_spraying = False

    def play_background_music(self):
        # placeholder for background music
        pass

    def play_pop(self):
        print("AUDIO: POP!")

    def play_swish_cheer(self):
        print("AUDIO: SWISH! CHEER!")

    def play_fanfare(self):
        print("AUDIO: Congratulations Fanfare!")

    def play_water_spray(self, start=True):
        # track spray state to avoid repeated start/stop prints
        if start and not self.is_spraying:
            self.is_spraying = True
        elif not start and self.is_spraying:
            self.is_spraying = False

    def play_clown_honk(self):
        print("AUDIO: HONK!")


# Prize screen: displays available prizes and whether the player qualifies
class PrizeScreen:
    def __init__(self, screen, font, sound_manager):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager
        self.small_font = safe_font(size=20)
        self.prize_font = safe_font(size=32)
        self.reset()

    def reset(self):
        # no per-instance state required beyond fonts and screen
        pass

    def handle_input(self, event):
        return 0

    def update(self, dt):
        return 0

    def draw(self, total_score):
        # Draw prize list with unlock status
        self.screen.fill(MENU_DARK_BLUE)
        title_surf = self.font.render("CARNIVAL PRIZE CENTER", True, CARNIVAL_YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_surf, title_rect)

        score_surf = self.prize_font.render(f"YOUR SCORE: {total_score}", True, UI_BRIGHT_YELLOW)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 110))
        self.screen.blit(score_surf, score_rect)

        y_start = 180
        item_height = 60

        for i, prize in enumerate(PRIZES):
            y_pos = y_start + i * (item_height + 10)
            is_unlocked = total_score >= prize['cost']
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 350, y_pos, 700, item_height)
            bg_color = DARK_GRAY if not is_unlocked else (30, 30, 30)
            pygame.draw.rect(self.screen, bg_color, rect, 0, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)

            icon_text = prize.get('icon', '?')
            try:
                icon_surf = self.prize_font.render(icon_text, True, WHITE)
            except Exception:
                icon_surf = self.prize_font.render("?", True, WHITE)
            if icon_surf.get_width() > 64:
                icon_surf = self.prize_font.render(prize['name'][0], True, WHITE)
            self.screen.blit(icon_surf, (rect.left + 20, rect.centery - icon_surf.get_height() // 2))

            name_color = WHITE if is_unlocked else DARK_GRAY
            name_surf = self.prize_font.render(prize['name'], True, name_color)
            self.screen.blit(name_surf, (rect.left + 80, rect.centery - name_surf.get_height() // 2))

            if is_unlocked:
                unlocked_surf = self.small_font.render("UNLOCKED!", True, SPLASH_GREEN)
                self.screen.blit(unlocked_surf, (rect.left + 80 + name_surf.get_width() + 10, rect.centery - unlocked_surf.get_height() // 2))

            cost_color = UI_BRIGHT_YELLOW if is_unlocked else CARNIVAL_RED
            cost_text = "CLAIMED" if is_unlocked else f"{prize['cost']} Points"
            cost_surf = self.prize_font.render(cost_text, True, cost_color)
            self.screen.blit(cost_surf, (rect.right - cost_surf.get_width() - 20, rect.centery - cost_surf.get_height() // 2))

        inst_surf = self.small_font.render("Press ESC to return to the Main Menu.", True, DARK_GRAY)
        self.screen.blit(inst_surf, (SCREEN_WIDTH // 2 - inst_surf.get_width() // 2, SCREEN_HEIGHT - 30))

    def cleanup(self):
        pass


# Dart Pop mini-game: rotating reticle, pop balloons for points
class DartPopGame:
    def __init__(self, screen, font, sound_manager):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager

        self.PLAY_AREA_RECT = pygame.Rect(
            PLAY_AREA_MARGIN, PLAY_AREA_MARGIN,
            SCREEN_WIDTH - 2 * PLAY_AREA_MARGIN,
            SCREEN_HEIGHT - 2 * PLAY_AREA_MARGIN
        )
        self.center_x = self.PLAY_AREA_RECT.centerx
        self.center_y = self.PLAY_AREA_RECT.centery

        self.target_radius = int(self.PLAY_AREA_RECT.width // 2 * 0.7)
        self.arm_length = int(self.target_radius * 0.75)
        self.target_angle = 3 * math.pi / 2
        self.hit_angle_min = self.target_angle - 0.26
        self.hit_angle_max = self.target_angle + 0.26

        self.reticle_mode = 'circle'  # 'circle' or 'figure8'
        self.reset()
        self.message = "Press SPACE to throw the dart! (Press F to toggle reticle mode)"

    def generate_balloons(self):
        # position balloons around target center
        self.balloons = []
        balloon_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        color = HOOP_BLUE
        for angle in balloon_angles:
            x = self.center_x + self.arm_length * math.cos(angle)
            y = self.center_y + self.arm_length * math.sin(angle)
            size = random.randint(18, 25)
            self.balloons.append({'pos': (int(x), int(y)), 'size': size, 'color': color, 'hit': False})

    def reset(self):
        # reset per-round state
        self.game_time = 0.0
        self.dart_thrown = False
        self.hit_result = None
        self.bullseye_radius = 20
        self.rotation_speed = max(0.7, min(2.2, 1.5 * random.choice([1, -1])))
        self.generate_balloons()
        self.message = "Press SPACE to throw the dart! (Press F to toggle reticle mode)"

    def _reticle_pos(self, t):
        """Compute reticle position based on selected motion pattern."""
        if self.reticle_mode == 'figure8':
            ax = self.arm_length
            ay = int(self.arm_length * 0.6)
            x = self.center_x + ax * math.sin(t)
            y = self.center_y + ay * math.sin(2 * t) * 0.5
            return x, y
        else:
            x = self.center_x + self.arm_length * math.cos(t)
            y = self.center_y + self.arm_length * math.sin(t)
            return x, y

    def handle_input(self, event):
        score_to_report = 0
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not self.dart_thrown:
                self.dart_thrown = True
                t = self.game_time * self.rotation_speed
                dart_x, dart_y = self._reticle_pos(t)
                hit_balloon = False
                hit_score = 0

                for balloon in self.balloons:
                    if not balloon['hit']:
                        dist = math.hypot(dart_x - balloon['pos'][0], dart_y - balloon['pos'][1])
                        if dist < balloon['size']:
                            balloon['hit'] = True
                            hit_balloon = True
                            hit_score += 100
                            self.sound_manager.play_pop()

                if hit_balloon:
                    self.hit_result = 'HIT'
                    score_to_report = hit_score
                    self.message = f"POP! +{score_to_report} Points! (Press R to Reset/Continue)"
                else:
                    normalized_angle = (t) % (2 * math.pi)
                    if (self.hit_angle_min < normalized_angle < self.hit_angle_max) or \
                       (self.hit_angle_min < normalized_angle - 2 * math.pi < self.hit_angle_max):
                        self.hit_result = 'NEAR_MISS'
                        score_to_report = 50
                        self.message = f"Good Timing! +{score_to_report} Points! (Press R to Reset/Continue)"
                    else:
                        self.hit_result = 'MISS'
                        score_to_report = 0
                        self.message = "MISS! (Press R to Reset/Continue)"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if self.dart_thrown:
                self.reset()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            # toggle reticle motion mode
            if self.reticle_mode == 'circle':
                self.reticle_mode = 'figure8'
                self.message = "Reticle: FIGURE-8 mode (Press F to toggle)"
            else:
                self.reticle_mode = 'circle'
                self.message = "Reticle: CIRCULAR mode (Press F to toggle)"

        return score_to_report

    def update(self, dt):
        # advance reticle when dart not thrown
        if not self.dart_thrown:
            self.game_time += dt
        return 0

    def draw(self):
        # main playfield rendering
        self.screen.fill(CARNIVAL_RED)
        pygame.draw.rect(self.screen, BLACK, self.PLAY_AREA_RECT)

        pygame.draw.circle(self.screen, DARK_GRAY, (self.center_x, self.center_y), self.target_radius + 50, 0)
        pygame.draw.circle(self.screen, CARNIVAL_RED, (self.center_x, self.center_y), self.target_radius, 0)
        pygame.draw.circle(self.screen, SPLASH_GREEN, (self.center_x, self.center_y), int(self.target_radius * 0.5))
        pygame.draw.circle(self.screen, WHITE, (self.center_x, self.center_y), self.bullseye_radius)

        for balloon in self.balloons:
            if balloon['hit']:
                pygame.draw.circle(self.screen, BLACK, balloon['pos'], balloon['size'] + 3)
                pygame.draw.circle(self.screen, CARNIVAL_RED, balloon['pos'], balloon['size'] - 5)
            else:
                pygame.draw.circle(self.screen, HOOP_BLUE, balloon['pos'], balloon['size'])

        t = self.game_time * self.rotation_speed
        end_x, end_y = self._reticle_pos(t)

        # small reticle marker; thrown dart is larger
        if not self.dart_thrown:
            pygame.draw.circle(self.screen, UI_BRIGHT_YELLOW, (int(end_x), int(end_y)), 8)

        if self.dart_thrown:
            dart_x, dart_y = self._reticle_pos(t)
            color = SPLASH_GREEN if self.hit_result != 'MISS' else CARNIVAL_RED
            pygame.draw.circle(self.screen, color, (int(dart_x), int(dart_y)), 12)

        self._draw_message()

    def _draw_message(self):
        # render wrapped message text beneath play area
        max_w = SCREEN_WIDTH - 40
        lines = wrap_text(self.font, self.message, max_w)
        y = self.PLAY_AREA_RECT.bottom + 8
        for line in lines:
            surf = self.font.render(line, True, UI_BRIGHT_YELLOW)
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))
            y += surf.get_height() + 2

    def cleanup(self):
        pass


# Hoop Shot: power meter timing and thrown basketball arc
class SwayObject(pygame.sprite.Sprite):
    """Vertical oscillating indicator used for power timing."""
    def __init__(self, center_x, center_y, amplitude, frequency, pattern, color=CARNIVAL_RED, size=20):
        super().__init__()
        self.size = size
        self.image = pygame.Surface([size * 10, size], pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect(center=(int(center_x), int(center_y)))
        self.start_x = int(center_x)
        self.start_y = int(center_y)
        self.amplitude = amplitude
        self.frequency = frequency
        self.pattern = pattern
        self.color = color
        self.time_offset = pygame.time.get_ticks()

    def update(self):
        elapsed_time = pygame.time.get_ticks() - self.time_offset
        time_s = elapsed_time / 1000.0
        angle = time_s * self.frequency * 2 * math.pi
        y_offset = 0
        if self.pattern == 1:
            y_offset = math.sin(angle) * self.amplitude
        self.rect.center = (self.start_x, int(self.start_y + y_offset))
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, self.color, (self.size * 5, self.size // 2), self.size // 2)
        return y_offset


class Basketball(pygame.sprite.Sprite):
    """Projectile with parabolic arc that disappears off-screen."""
    def __init__(self, start_x, start_y, arc_type, speed_multiplier=1.0):
        super().__init__()
        self.size = 40
        self.image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, OG_ORANGE, (self.size // 2, self.size // 2), self.size // 2)

        self.rect = self.image.get_rect(center=(int(start_x), int(start_y)))

        self.start_time = pygame.time.get_ticks()
        self.start_x = float(start_x)
        self.start_y = float(start_y)
        self.target_x = float(SCREEN_WIDTH - PLAY_AREA_MARGIN - 100)
        self.target_y = float(SCREEN_HEIGHT // 2)
        self.gravity = 1500.0

        if arc_type == 'swish':
            self.duration = max(0.55, 0.9 / speed_multiplier)
            self.initial_vy = -800.0 * speed_multiplier
        elif arc_type == 'overshoot':
            self.duration = max(0.5, 1.0 / speed_multiplier)
            self.initial_vy = -1050.0 * speed_multiplier
        elif arc_type == 'undershoot':
            self.duration = max(0.45, 0.7 / speed_multiplier)
            self.initial_vy = -500.0 * speed_multiplier
        else:
            self.duration = max(0.6, 1.0 / speed_multiplier)
            self.initial_vy = -650.0 * speed_multiplier

        self.vx = (self.target_x - self.start_x) / max(0.001, self.duration)
        self.in_flight = True

    def update(self):
        if not self.in_flight:
            return
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000.0

        if elapsed_time > self.duration * 1.6:
            try:
                self.kill()
            except Exception:
                pass
            self.in_flight = False
            return

        new_x = self.start_x + self.vx * elapsed_time
        new_y = self.start_y + (self.initial_vy * elapsed_time) + (0.5 * self.gravity * elapsed_time**2)

        self.rect.center = (int(new_x), int(new_y))

        if new_x > self.target_x + 140:
            try:
                self.kill()
            except Exception:
                pass
            self.in_flight = False


class HoopShotGame:
    """Power-timing mini-game: hit the green zone to score a SWISH."""
    def __init__(self, screen, font, sound_manager):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager

        self.PLAY_AREA_RECT = pygame.Rect(
            PLAY_AREA_MARGIN, PLAY_AREA_MARGIN,
            SCREEN_WIDTH - 2 * PLAY_AREA_MARGIN,
            SCREEN_HEIGHT - 2 * PLAY_AREA_MARGIN
        )
        self.PLAY_AREA_CENTER_Y = self.PLAY_AREA_RECT.centery

        self.reset()

    def reset(self):
        # initialize combo, meter and shooter position
        self.shot_result = "Press SPACE to shoot!"
        self.swish_combo = 0
        self.combo_max = 6
        self.base_speed_multiplier = 1.0

        self.bar_center_x = self.PLAY_AREA_RECT.left + 80
        self.bar_center_y = self.PLAY_AREA_CENTER_Y
        self.bar_amplitude = self.PLAY_AREA_RECT.height // 2 - 50
        self.zone_height = 50

        freq = 1.0 + (self.swish_combo * 0.15)
        freq = min(freq, 2.5)

       	self.power_meter = SwayObject(
            center_x=self.bar_center_x,
            center_y=self.bar_center_y,
            amplitude=self.bar_amplitude,
            frequency=freq,
            pattern=1,
            color=UI_BRIGHT_YELLOW,
            size=20
        )

        self.all_sprites = pygame.sprite.Group(self.power_meter)
        self.shooter_x = self.PLAY_AREA_RECT.left + 150
        self.shooter_y = self.PLAY_AREA_RECT.bottom - 50
        self.perfect_zone_rect = pygame.Rect(0, 0, 0, 0)
        self._randomize_target_zone()

    def _randomize_target_zone(self):
        # choose a vertical perfect zone for timing
        min_top_y = self.bar_center_y - self.bar_amplitude
        max_top_y = self.bar_center_y + self.bar_amplitude - self.zone_height
        self.perfect_zone_top = random.randint(int(min_top_y), int(max_top_y))
        self.perfect_zone_bottom = self.perfect_zone_top + self.zone_height
        self.perfect_zone_rect = pygame.Rect(
            int(self.bar_center_x - 10), int(self.perfect_zone_top), 20, self.zone_height
        )

    def _check_shot(self):
        # evaluate indicator position and spawn a basketball arc
        score_to_report = 0
        indicator_y = self.power_meter.rect.centery
        arc_type = 'miss'

        speed_multiplier = 1.0 + (self.swish_combo * 0.10)
        speed_multiplier = min(speed_multiplier, 1.7)

        self.power_meter.frequency = 1.0 + (self.swish_combo * 0.15)
        self.power_meter.frequency = min(self.power_meter.frequency, 2.5)

        if self.perfect_zone_top <= indicator_y <= self.perfect_zone_bottom:
            score_to_report = 250
            self.shot_result = f"SWISH! Perfect Shot! +{score_to_report} Points!"
            arc_type = 'swish'
            self.sound_manager.play_swish_cheer()
            self.swish_combo = min(self.combo_max, self.swish_combo + 1)
        else:
            zone_center_y = self.perfect_zone_top + (self.zone_height / 2)
            distance = abs(indicator_y - zone_center_y)
            if distance < self.zone_height * 2.5:
                self.shot_result = "Near Miss. Try to hit the green zone."
            else:
                self.shot_result = "Way Off! Miss."

            score_to_report = 0
            arc_type = random.choice(['overshoot', 'undershoot'])
            self.swish_combo = 0

        new_ball = Basketball(self.shooter_x, self.shooter_y, arc_type, speed_multiplier=speed_multiplier)
        self.all_sprites.add(new_ball)

        self.power_meter.time_offset = pygame.time.get_ticks()
        self._randomize_target_zone()

        return score_to_report

    def handle_input(self, event):
        score_change = 0
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            score_change = self._check_shot()
        return score_change

    def update(self, dt):
        self.all_sprites.update()
        # remove finished basketball sprites
        for sprite in list(self.all_sprites):
            if isinstance(sprite, Basketball) and not sprite.in_flight and sprite.alive():
                try:
                    sprite.kill()
                except Exception:
                    pass
        return 0

    def draw(self):
        # render playfield, power track, shooter and hoop
        self.screen.fill(HOOP_BLUE)
        pygame.draw.rect(self.screen, BLACK, self.PLAY_AREA_RECT)

        track_rect = pygame.Rect(
            int(self.power_meter.start_x - 10), int(self.power_meter.start_y - self.bar_amplitude), 20, int(self.bar_amplitude * 2)
        )
        pygame.draw.rect(self.screen, DARK_GRAY, track_rect, 0, border_radius=5)
        pygame.draw.rect(self.screen, SPLASH_GREEN, self.perfect_zone_rect, 0, border_radius=5)

        pygame.draw.circle(self.screen, WHITE, (int(self.shooter_x), int(self.shooter_y)), 25)
        pygame.draw.circle(self.screen, DARK_GRAY, (int(self.shooter_x), int(self.shooter_y)), 25, 3)

        hoop_center_x = self.PLAY_AREA_RECT.right - 100
        hoop_center_y = self.PLAY_AREA_CENTER_Y

        backboard_rect = (hoop_center_x, hoop_center_y - 75, 10, 150)
        pygame.draw.rect(self.screen, WHITE, backboard_rect)

        rim_rect = (hoop_center_x - 80, hoop_center_y - 15, 80, 30)
        pygame.draw.ellipse(self.screen, DARK_GRAY, rim_rect, 8)

        # subtle front rim stroke so the front lip reads as a distinct line
        front_rim_rect = (hoop_center_x - 76, hoop_center_y - 8, 72, 18)
        pygame.draw.ellipse(self.screen, DARK_GRAY, front_rim_rect, 6)

        # net geometry (fix: draw right-side net line properly)
        net_top_left = (hoop_center_x - 76, hoop_center_y)
        net_top_right = (hoop_center_x - 4, hoop_center_y)
        net_bottom_left = (hoop_center_x - 60, hoop_center_y + 60)
        net_bottom_right = (hoop_center_x - 20, hoop_center_y + 60)

        pygame.draw.line(self.screen, WHITE, net_top_left, net_bottom_left, 2)
        pygame.draw.line(self.screen, WHITE, net_top_right, net_bottom_right, 2)
        pygame.draw.line(self.screen, WHITE, net_bottom_left, net_bottom_right, 2)

        self.all_sprites.draw(self.screen)

        combo_text = f"Combo: {self.swish_combo}"
        combo_surf = self.font.render(combo_text, True, UI_BRIGHT_YELLOW)
        self.screen.blit(combo_surf, (20, 20))

        # render shot result lines from bottom up
        msg_lines = wrap_text(self.font, self.shot_result, SCREEN_WIDTH // 2)
        y = SCREEN_HEIGHT - 30
        for line in reversed(msg_lines):
            surf = self.font.render(line, True, UI_BRIGHT_YELLOW)
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y - surf.get_height()))
            y -= surf.get_height() + 2

    def cleanup(self):
        self.all_sprites.empty()


# Clown face renderer helper (used by Clown sprite)
def draw_clown_face_centered(surface, clown_size, hit, surface_size):
    """Draw a simple clown face, different when hit."""
    surface.fill((0, 0, 0, 0))
    offset = (surface_size - clown_size) // 2
    center = (surface_size // 2, surface_size // 2)
    radius = clown_size // 2

    face_color = WHITE if not hit else (200, 200, 200)
    pygame.draw.circle(surface, face_color, center, radius)

    if hit:
        pygame.draw.circle(surface, OG_WATER_CYAN, center, int(radius * 0.6))
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
    """Sprite representing a clown target that can be visually 'hit' by the stream."""
    def __init__(self, center_x, center_y, size=60):
        super().__init__()
        self.clown_size = int(size)
        self.visual_size = self.clown_size + 20
        self.image = pygame.Surface([self.visual_size, self.visual_size], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(center_x), int(center_y)))
        self.hit = False
        self.visual_hit = False
        self._draw()

    def _draw(self):
        draw_clown_face_centered(self.image, self.clown_size, self.visual_hit, self.visual_size)

    def mark_hit(self):
        self.hit = True
        return True

    def update_visual(self, is_hit_by_stream):
        # flip visual state only when changed to avoid excessive redraws
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
    """Water cannon that computes stream path and draws stream + particles."""
    def __init__(self, center_x, bottom_y):
        super().__init__()
        self.center_x_base = int(center_x)
        self.current_angle = 0.0
        self.bottom_y = int(bottom_y)

        self.current_stream_x = float(center_x)
        self.current_stream_y = float(bottom_y - STREAM_LENGTH)

        self.pivot_x = int(center_x)
        self.pivot_y = int(bottom_y - 10)

        self.barrel_width = 100
        self.barrel_height = 24
        self.image = pygame.Surface([self.barrel_width, self.barrel_height], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.center_x_base, bottom_y - self.barrel_height // 2))
        pygame.draw.rect(self.image, (30, 30, 30), (0, 0, self.barrel_width, self.barrel_height), 0, border_radius=6)
        pygame.draw.rect(self.image, CARNIVAL_YELLOW, (6, 6, self.barrel_width - 12, self.barrel_height - 12), 2, border_radius=5)

        self.is_spraying = False
        self.max_stream_width = 25
        self.hit_stream_x = float(center_x)

        # full-screen stream surface for easy blitting and alpha blending
        self.stream_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.stream_rect = self.stream_image.get_rect(topleft=(0, 0))

        self.particles = []

    def update_position(self, dt):
        # swing the cannon's stream endpoint
        self.current_angle += SWING_SPEED * dt
        swing_angle = math.sin(self.current_angle) * MAX_SWING_ANGLE

        self.current_stream_x = self.pivot_x + STREAM_LENGTH * math.sin(swing_angle)
        self.current_stream_y = self.pivot_y - STREAM_LENGTH * math.cos(swing_angle)

    def update_stream(self, target_y, water_level_ratio):
        """Redraw stream based on current pivot->endpoint and water level (controls width)."""
        self.stream_image.fill((0, 0, 0, 0))

        if self.is_spraying:
            min_width_ratio = 0.25
            current_width_ratio = min_width_ratio + water_level_ratio * (1.0 - min_width_ratio)
            stream_width = max(2, int(self.max_stream_width * current_width_ratio))

            # compute horizontal intersection x (hit point) along pivot->endpoint according to target_y
            dy_target = (self.pivot_y - target_y)
            dy_total = (self.pivot_y - self.current_stream_y)
            if abs(dy_total) < 1e-3 or abs(dy_target) < 1e-3:
                hit_x = float(self.pivot_x)
            else:
                t = max(0.0, min(1.0, dy_target / dy_total))
                hit_x = float(self.pivot_x + t * (self.current_stream_x - self.pivot_x))

            self.hit_stream_x = hit_x

            flicker_blue = min(255, max(140, OG_WATER_CYAN[2] + random.randint(-20, 20)))
            water_color = (OG_WATER_CYAN[0], OG_WATER_CYAN[1], flicker_blue, 200)

            # core stream line and glow
            pygame.draw.line(
                self.stream_image,
                water_color,
                (int(self.pivot_x), int(self.pivot_y)),
                (int(self.current_stream_x), int(self.current_stream_y)),
                stream_width
            )

            glow_color = (OG_WATER_CYAN[0], OG_WATER_CYAN[1], flicker_blue, 60)
            for i in range(1, 4):
                pygame.draw.line(
                    self.stream_image,
                    glow_color,
                    (int(self.pivot_x), int(self.pivot_y)),
                    (int(self.current_stream_x), int(self.current_stream_y)),
                    max(1, stream_width + i * 3)
                )

            # spawn droplets along the stream
            for i in range(6):
                frac = random.random()
                px = int(self.pivot_x + (self.current_stream_x - self.pivot_x) * frac + random.uniform(-6, 6))
                py = int(self.pivot_y + (self.current_stream_y - self.pivot_y) * frac + random.uniform(-6, 6))
                size = random.randint(2, 5)
                life = random.uniform(0.35, 0.9)
                self.particles.append({'x': px, 'y': py, 'size': size, 'life': life, 'age': 0.0, 'vy': random.uniform(20, 80)})

        # update particle positions and draw them
        for p in list(self.particles):
            p['age'] += 1.0 / FPS
            if p['age'] >= p['life']:
                try:
                    self.particles.remove(p)
                except ValueError:
                    pass
                continue
            alpha = int(255 * (1.0 - (p['age'] / p['life'])))
            p['y'] += p.get('vy', 30) * (1.0 / FPS)
            pygame.draw.circle(self.stream_image, (OG_WATER_CYAN[0], OG_WATER_CYAN[1], OG_WATER_CYAN[2], alpha), (int(p['x']), int(p['y'])), p['size'])

    def draw_stream(self, surface):
        # blit stream surface if spraying or particles exist
        if self.is_spraying or self.particles:
            surface.blit(self.stream_image, self.stream_rect)


class ClownSplashMiniGame:
    """Water-shooting mini-game: hold SPACE to spray and hit clown targets for points."""
    def __init__(self, screen, font, sound_manager):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager
        self.small_font = safe_font(size=20)

        self.PLAY_AREA_RECT = pygame.Rect(
            PLAY_AREA_MARGIN, PLAY_AREA_MARGIN,
            SCREEN_WIDTH - 2 * PLAY_AREA_MARGIN,
            SCREEN_HEIGHT - 2 * PLAY_AREA_MARGIN
        )
        self.PLAY_AREA_CENTER_X = self.PLAY_AREA_RECT.centerx

        self.reset()

    def reset(self):
        # tank and timing parameters; smaller WATER_MAX with tuned rates
        self.message = "Hold SPACE to spray water! Splash for points!"
        self.WATER_MAX = 25.0
        self.water_level = self.WATER_MAX
        self.SPRAY_RATE = 10.0
        self.REFILL_RATE = 1.25
        self.COOLDOWN_TIME = 0.7
        self.last_spray_time = 0.0
        self.last_score_time = 0.0

        self.start_threshold_ratio = 0.5
        self.spray_charge_time = 0.12
        self.space_held_since = None

        self.clown_target_y = self.PLAY_AREA_RECT.top + 100
        self.clown_targets = pygame.sprite.Group()
        self._setup_clowns()

        cannon_x = self.PLAY_AREA_CENTER_X
        cannon_y = self.PLAY_AREA_RECT.bottom - 50
        self.water_gun = WaterGun(cannon_x, cannon_y)

        self.space_down = False
        self.is_in_cooldown = False
        self.MAX_WATER = self.WATER_MAX
        self.last_attempt_spray_time = 0.0

        # tank UI placement
        self.tank_x = self.PLAY_AREA_RECT.left + 20
        self.tank_width = 40
        self.tank_height = 200
        self.tank_y = self.PLAY_AREA_RECT.bottom - self.tank_height - 80

    def _setup_clowns(self):
        # create three static clown targets centered horizontally
        self.clown_targets.empty()
        clown_spacing = 150
        num_clowns = 3
        start_x = self.PLAY_AREA_CENTER_X - (num_clowns - 1) * clown_spacing / 2

        for i in range(num_clowns):
            x = int(start_x + (i * clown_spacing))
            clown = Clown(x, self.clown_target_y)
            self.clown_targets.add(clown)

    def handle_input(self, event):
        score_change = 0

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # begin a hold attempt, respecting cooldown
                if not self.is_in_cooldown:
                    self.space_down = True
                    if self.space_held_since is None:
                        self.space_held_since = time.time()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                if self.space_down:
                    self.space_down = False
                    self.space_held_since = None
                    # if spraying was active when released, enter cooldown and reset clowns
                    if not self.is_in_cooldown and self.water_gun.is_spraying:
                        self.last_spray_time = time.time()
                        self.is_in_cooldown = True
                        for clown in self.clown_targets:
                            clown.reset()
                        self.sound_manager.play_water_spray(start=False)
                        self.message = "Cooldown initiated..."
        return score_change

    def update(self, dt):
        score_to_report = 0
        current_time = time.time()
        self.water_gun.update_position(dt)

        should_spray_attempt = self.space_down and not self.is_in_cooldown
        is_spraying_now = False

        if should_spray_attempt:
            # check minimum water to start spraying
            if self.water_level < (self.WATER_MAX * self.start_threshold_ratio):
                self.message = f"Tank needs {int(self.start_threshold_ratio * 100)}% to start spraying!"
                self.sound_manager.play_water_spray(start=False)
                self.water_gun.is_spraying = False
            else:
                held = (self.space_held_since is not None) and (current_time - self.space_held_since >= self.spray_charge_time)
                if held and (current_time - self.last_attempt_spray_time > 0.06):
                    self.last_attempt_spray_time = current_time
                    if self.water_level > 0:
                        # consume water while spraying
                        self.water_level -= self.SPRAY_RATE * dt
                        self.water_level = max(0.0, self.water_level)
                        is_spraying_now = True
                        self.sound_manager.play_water_spray(start=True)
                        self.message = f"Spraying! Water: {int(self.water_level)}%"

                        clowns_being_hit_this_frame = []
                        for clown in self.clown_targets:
                            if abs(clown.rect.centerx - self.water_gun.hit_stream_x) < (clown.clown_size // 2 + 6):
                                clown.mark_hit()
                                clowns_being_hit_this_frame.append(clown)

                        # award points periodically while holding on target
                        if clowns_being_hit_this_frame and current_time - self.last_score_time >= HIT_SCORE_INTERVAL:
                            score_to_report = 10
                            self.last_score_time = current_time
                            self.message = f"BULLSEYE! +{score_to_report} (Water: {int(self.water_level)}%)"

                        for clown in self.clown_targets:
                            is_hit = clown in clowns_being_hit_this_frame
                            clown.update_visual(is_hit)

                    # force cooldown if tank empties while spraying
                    if self.water_level == 0.0 and is_spraying_now:
                        is_spraying_now = False
                        self.last_spray_time = current_time
                        self.is_in_cooldown = True
                        self.sound_manager.play_water_spray(start=False)
                        self.message = "Tank EMPTY! Refilling & Cooldown..."
                        for clown in self.clown_targets:
                            clown.reset()

        # cooldown handling
        time_since_spray = current_time - self.last_spray_time
        if self.is_in_cooldown:
            if time_since_spray >= self.COOLDOWN_TIME:
                self.is_in_cooldown = False
                if not self.space_down and self.water_level == self.MAX_WATER:
                    self.message = "Tank fully charged. Hold SPACE to spray water!"
                elif not self.space_down and self.water_level < self.MAX_WATER:
                    self.message = "Refilling water tank..."
            else:
                remaining_time = self.COOLDOWN_TIME - time_since_spray
                self.message = f"Cooldown: {remaining_time:.1f}s until ready."

        # refill when appropriate
        if not is_spraying_now and self.water_level < self.WATER_MAX and not self.is_in_cooldown:
            self.water_level += self.REFILL_RATE * dt
            self.water_level = min(self.WATER_MAX, self.water_level)

            if self.water_level == self.MAX_WATER and not self.space_down:
                self.message = "Tank fully charged. Hold SPACE to spray water!"
            elif not self.is_in_cooldown:
                self.message = "Refilling water tank..."

        if not is_spraying_now:
            self.sound_manager.play_water_spray(start=False)

        self.water_gun.is_spraying = is_spraying_now
        water_ratio = self.water_level / self.WATER_MAX
        self.water_gun.update_stream(self.clown_target_y, water_ratio)

        return score_to_report

    def draw(self):
        # draw playfield, tank UI, clowns and stream
        self.screen.fill(SPLASH_GREEN)
        pygame.draw.rect(self.screen, BLACK, self.PLAY_AREA_RECT)

        pygame.draw.rect(self.screen, CARNIVAL_RED, (self.PLAY_AREA_RECT.left, self.clown_target_y + 30, self.PLAY_AREA_RECT.width, 10))
        pygame.draw.rect(self.screen, CARNIVAL_RED, (self.PLAY_AREA_RECT.left, self.PLAY_AREA_RECT.bottom - 70, self.PLAY_AREA_RECT.width, 70))

        tank_x, tank_y = self.tank_x, self.tank_y
        tank_width, tank_height = self.tank_width, self.tank_height

        # tank border
        pygame.draw.rect(self.screen, WHITE, (tank_x-4, tank_y-4, tank_width+8, tank_height+8), 3, border_radius=6)

        # gradient water fill
        fill_ratio = self.water_level / self.WATER_MAX
        fill_height = int(fill_ratio * tank_height)
        for i in range(fill_height):
            t = i / max(1, fill_height)
            r = int(OG_WATER_CYAN[0] * (0.6 + 0.4 * t))
            g = int(OG_WATER_CYAN[1] * (0.6 + 0.4 * t))
            b = int(OG_WATER_CYAN[2] * (0.6 + 0.4 * t))
            pygame.draw.line(self.screen, (r, g, b), (tank_x, tank_y + tank_height - i), (tank_x + tank_width - 1, tank_y + tank_height - i))

        pygame.draw.rect(self.screen, DARK_GRAY, (tank_x, tank_y, tank_width, tank_height), 3, border_radius=6)

        threshold_y = tank_y + tank_height - int(self.start_threshold_ratio * tank_height)
        pygame.draw.line(self.screen, CARNIVAL_YELLOW, (tank_x - 6, threshold_y), (tank_x + tank_width + 6, threshold_y), 2)
        label = self.small_font.render("WATER", True, BLACK)
        self.screen.blit(label, (tank_x + tank_width // 2 - label.get_width() // 2, tank_y - 26))

        # message with wrapping
        display_message = self.message.replace('**', '')
        max_w = SCREEN_WIDTH - 40
        lines = wrap_text(self.font, display_message, max_w)
        y = SCREEN_HEIGHT - 30 - (len(lines) - 1) * (self.font.get_linesize() // 1)
        for line in lines:
            msg_text = self.font.render(line, True, UI_BRIGHT_YELLOW)
            self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, y))
            y += msg_text.get_height() + 2

        # draw stream and clowns and cannon
        self.water_gun.draw_stream(self.screen)
        self.clown_targets.draw(self.screen)
        self.screen.blit(self.water_gun.image, self.water_gun.rect)

    def cleanup(self):
        # clear sprites and ensure spray sound ended
        self.clown_targets.empty()
        self.sound_manager.play_water_spray(start=False)


# Shell Game: three cups shuffled with a hidden ball
class Cup(pygame.sprite.Sprite):
    """Cup sprite that can move smoothly between positions and reveal a hidden ball."""
    def __init__(self, x, y, size=160, has_ball=False):
        super().__init__()
        self.size = int(size)
        self.image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.current_x = float(x)
        self.current_y = float(y)
        self.has_ball = bool(has_ball)
        self.is_moving = False
        self.is_revealed = False
        self.color = CARNIVAL_RED

        self.target_x = float(x)
        self.target_y = float(y)
        self.start_time = 0.0
        self.duration = SHUFFLE_DURATION_MS / 1000.0

        self._draw_cup()

    def _draw_cup(self):
        # draw simple cup shape; show ball if revealed
        self.image.fill((0, 0, 0, 0))
        points = [
            (5, self.size),
            (self.size - 5, self.size),
            (self.size - 25, 20),
            (25, 20)
        ]
        pygame.draw.polygon(self.image, self.color, points, 0)
        pygame.draw.polygon(self.image, BLACK, points, 3)
        if self.is_revealed and self.has_ball:
            pygame.draw.circle(self.image, WHITE, (self.size // 2, self.size - 30), 18)

    def set_target(self, target_x, target_y):
        # animate movement to a new center x
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        self.start_time = time.time()
        self.is_moving = True
        self.duration = SHUFFLE_DURATION_MS / 1000.0

    def update(self):
        # ease movement from current_x to target_x
        if self.is_moving:
            elapsed = time.time() - self.start_time
            progress = min(elapsed / self.duration, 1.0)
            smooth_progress = 0.5 - 0.5 * math.cos(progress * math.pi)
            new_x = self.current_x + (self.target_x - self.current_x) * smooth_progress
            new_y = self.current_y
            self.rect.center = (int(new_x), int(new_y))
            if progress >= 1.0:
                self.is_moving = False
                self.current_x = self.target_x
                self.current_y = self.target_y

    def reveal(self, should_reveal=True):
        self.is_revealed = bool(should_reveal)
        self._draw_cup()


class ShellGameMiniGame:
    """Classic shell game: watch an initial reveal, then cups shuffle; click to choose."""
    def __init__(self, screen, font, sound_manager):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager

        self.PLAY_AREA_RECT = pygame.Rect(
            PLAY_AREA_MARGIN, PLAY_AREA_MARGIN,
            SCREEN_WIDTH - 2 * PLAY_AREA_MARGIN,
            SCREEN_HEIGHT - 2 * PLAY_AREA_MARGIN
        )
        self.PLAY_AREA_CENTER_X = self.PLAY_AREA_RECT.centerx

        self.reset()

    def reset(self):
        # initialize shuffle state and cup positions
        self.state = "START_REVEAL"
        self.shuffle_count = 10
        self.current_shuffle = 0
        self.message = "Get ready to watch closely!"
        self.shuffle_pairs = []

        pygame.time.set_timer(SHUFFLE_EVENT, 0)

        self.cup_x_positions = [
            self.PLAY_AREA_CENTER_X - 200,
            self.PLAY_AREA_CENTER_X,
            self.PLAY_AREA_CENTER_X + 200
        ]
        self.cup_y = self.PLAY_AREA_RECT.bottom - 100

        self._setup_cups()
        self._initial_reveal_sequence()

    def _setup_cups(self):
        # place three cups and hide the ball under a random one
        ball_index = random.randint(0, 2)

        self.cups = []
        for i, x_pos in enumerate(self.cup_x_positions):
            cup = Cup(x_pos, self.cup_y, size=160, has_ball=(i == ball_index))
            self.cups.append(cup)

        self.all_sprites = pygame.sprite.Group(self.cups)

        for cup in self.cups:
            cup.reveal(False)
            cup.is_moving = False

    def _initial_reveal_sequence(self):
        # briefly reveal the ball location, then schedule shuffling
        self.state = "START_REVEAL"
        for cup in self.cups:
            if cup.has_ball:
                cup.reveal(True)
            else:
                cup.reveal(False)
        self.message = "Watch the ball!"
        pygame.time.set_timer(SHUFFLE_EVENT, INITIAL_REVEAL_DURATION_MS, 1)

    def _start_shuffling(self):
        # prepare shuffle sequence (random pair swaps)
        for cup in self.cups:
            cup.reveal(False)

        self.state = "SHUFFLING"
        self.current_shuffle = 0
        self.shuffle_pairs = self._generate_shuffle_pairs()
        self.message = f"Shuffling {self.shuffle_count} times... Keep your eyes on the ball!"
        pygame.time.set_timer(SHUFFLE_EVENT, SHUFFLE_DURATION_MS + 100)

    def _generate_shuffle_pairs(self):
        # generate a list of index pairs to swap
        pairs = []
        for _ in range(self.shuffle_count):
            indices = random.sample(range(3), 2)
            pairs.append(tuple(indices))
        return pairs

    def _do_one_shuffle(self):
        # if cups stationary, perform one swap and animate
        if any(cup.is_moving for cup in self.cups):
            return

        if self.current_shuffle >= len(self.shuffle_pairs):
            pygame.time.set_timer(SHUFFLE_EVENT, 0)
            self.state = "WAITING_CHOICE"
            self.message = "Where is the ball? Click on a cup!"
            self.sound_manager.play_clown_honk()
            return

        idx1, idx2 = self.shuffle_pairs[self.current_shuffle]
        cup1_obj = self.cups[idx1]
        cup2_obj = self.cups[idx2]
        target_x1, target_y1 = cup1_obj.current_x, cup1_obj.current_y
        target_x2, target_y2 = cup2_obj.current_x, cup2_obj.current_y
        cup1_obj.set_target(target_x2, target_y2)
        cup2_obj.set_target(target_x1, target_y1)
        self.cups[idx1], self.cups[idx2] = self.cups[idx2], self.cups[idx1]
        self.current_shuffle += 1

    def _check_choice(self, pos):
        # determine which cup player clicked and reveal results
        score_to_report = 0
        if self.state != "WAITING_CHOICE":
            return score_to_report

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
                score_to_report = 1000
                self.message = f"CONGRATS! You found the ball! +{score_to_report} Points! (Game resets soon)"
                self.sound_manager.play_fanfare()
            else:
                score_to_report = 0
                self.message = "Too bad! The ball was not there. (Game resets soon)"

            pygame.time.set_timer(SHUFFLE_EVENT, INITIAL_REVEAL_DURATION_MS, 1)

        return score_to_report

    def handle_input(self, event):
        score_change = 0

        if event.type == SHUFFLE_EVENT:
            if self.state == "START_REVEAL":
                self._start_shuffling()
            elif self.state == "SHUFFLING":
                self._do_one_shuffle()
            elif self.state == "GAME_OVER":
                self.reset()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "WAITING_CHOICE":
                score_change = self._check_choice(event.pos)

        return score_change

    def update(self, dt):
        self.all_sprites.update()
        return 0

    def draw(self):
        # table and cups
        self.screen.fill(BLACK)
        table_rect = pygame.Rect(self.PLAY_AREA_RECT.left, self.PLAY_AREA_RECT.top + 100, self.PLAY_AREA_RECT.width, self.PLAY_AREA_RECT.height - 100)
        pygame.draw.rect(self.screen, OG_BROWN, table_rect)

        msg_text = self.font.render(self.message, True, UI_BRIGHT_YELLOW)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, 80))

        self.all_sprites.draw(self.screen)

    def cleanup(self):
        # stop timers and clear sprites
        pygame.time.set_timer(SHUFFLE_EVENT, 0)
        self.all_sprites.empty()


# Arcade manager: main loop, menu and game switching
class ArcadeManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # fonts used through UI
        self.title_font = safe_font(size=56)
        self.header_font = safe_font(size=36)
        self.button_font = safe_font(size=28)
        self.ui_font = safe_font(size=22)
        self.small_font = safe_font(size=18)

        self.sound_manager = SoundManager()
        self.total_score = 0
        self.current_game_score = 0

        self.game_high_scores = {
            STATE_DARTPOP: 0,
            STATE_HOOPSHOT: 0,
            STATE_SPLASH: 0,
            STATE_SHELLGAME: 0
        }

        self.state = STATE_MENU
        self.button_rects = {}
        self.stats_button_rect = pygame.Rect(0, 0, 0, 0)

        # instantiate game modules once and reset when entering them
        self.games = {
            STATE_DARTPOP: DartPopGame(self.screen, self.ui_font, self.sound_manager),
            STATE_HOOPSHOT: HoopShotGame(self.screen, self.ui_font, self.sound_manager),
            STATE_SPLASH: ClownSplashMiniGame(self.screen, self.ui_font, self.sound_manager),
            STATE_SHELLGAME: ShellGameMiniGame(self.screen, self.ui_font, self.sound_manager),
            STATE_PRIZES: PrizeScreen(self.screen, self.header_font, self.sound_manager),
        }

        self.game_names = {
            STATE_DARTPOP: "Dart Pop",
            STATE_HOOPSHOT: "Hoop Shot",
            STATE_SPLASH: "Clown Splash",
            STATE_SHELLGAME: "Shell Game",
            STATE_PRIZES: "PRIZES",
        }

        self.sound_manager.play_background_music()

    def _handle_input(self):
        # central event loop: handle quitting, menu navigation and delegating to active game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # pressing ESC returns to menu (or exits if already on menu)
                    if self.state != STATE_MENU and self.state != STATE_STATS:
                        game_state = self.state
                        if game_state in self.game_high_scores and self.current_game_score > self.game_high_scores[game_state]:
                            self.game_high_scores[game_state] = self.current_game_score

                        self.current_game_score = 0
                        current_game = self.games[self.state]
                        current_game.cleanup()
                        current_game.reset()
                        self.state = STATE_MENU
                    elif self.state == STATE_MENU:
                        self.running = False

                if self.state == STATE_STATS and event.key == pygame.K_SPACE:
                    self.state = STATE_MENU

            if self.state == STATE_MENU:
                # menu mouse interactions: start games or open stats
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for game_state, rect in self.button_rects.items():
                        if rect.collidepoint(event.pos):
                            if game_state == STATE_SHELLGAME and self.total_score < SHELL_GAME_UNLOCK_SCORE:
                                # locked, ignore click
                                pass
                            else:
                                self.state = game_state
                                if game_state != STATE_PRIZES:
                                    self.games[self.state].reset()
                                    self.current_game_score = 0
                                break

                    if self.stats_button_rect.collidepoint(event.pos):
                        self.state = STATE_STATS

            elif self.state in self.games:
                # forward events to active game and add scores returned by handlers
                score_change = self.games[self.state].handle_input(event)
                if score_change > 0:
                    self.total_score += score_change
                    self.current_game_score += score_change

    def _update_state(self, dt):
        # update current game if not the prize screen
        if self.state in self.games and self.state != STATE_PRIZES:
            score_change = self.games[self.state].update(dt)
            if score_change > 0:
                self.total_score += score_change
                self.current_game_score += score_change

    def _draw_menu(self):
        # draw main menu with stylized stripe background and game buttons
        self.screen.fill(MENU_DARK_BLUE)

        stripe_width = 40
        for i in range(0, SCREEN_WIDTH + stripe_width, stripe_width):
            color = CARNIVAL_RED if (i // stripe_width) % 2 == 0 else WHITE
            pygame.draw.rect(self.screen, color, (i, 0, stripe_width, SCREEN_HEIGHT))

        overlay_width = 440
        overlay_height = 460
        overlay_rect = pygame.Rect(
            SCREEN_WIDTH//2 - overlay_width//2,
            100,
            overlay_width,
            overlay_height
        )
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 150))
        self.screen.blit(overlay_surface, overlay_rect.topleft)
        pygame.draw.rect(self.screen, CARNIVAL_YELLOW, overlay_rect, 5, border_radius=30)

        title_surf = self.title_font.render("JAY'S CARNIVAL ARCADE", True, CARNIVAL_YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surf, title_rect)

        stats_text = "📊 STATS"
        stats_button_rect = pygame.Rect(10, SCREEN_HEIGHT - PLAY_AREA_MARGIN - 50, 180, 50)
        draw_button(self.screen, stats_text, stats_button_rect, DARK_GRAY, WHITE, self.button_font)
        self.stats_button_rect = stats_button_rect

        y_start = 140
        button_height = 60
        button_width = 380
        button_spacing = 12

        self.button_rects = {}

        rect_dart = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, y_start, button_width, button_height)
        draw_button(self.screen, self.game_names[STATE_DARTPOP], rect_dart, CARNIVAL_RED, BLACK, self.button_font)
        self.button_rects[STATE_DARTPOP] = rect_dart

        rect_hoop = pygame.Rect(rect_dart.left, rect_dart.bottom + button_spacing, button_width, button_height)
        draw_button(self.screen, self.game_names[STATE_HOOPSHOT], rect_hoop, HOOP_BLUE, WHITE, self.button_font)
        self.button_rects[STATE_HOOPSHOT] = rect_hoop

        rect_splash = pygame.Rect(rect_hoop.left, rect_hoop.bottom + button_spacing, button_width, button_height)
        draw_button(self.screen, self.game_names[STATE_SPLASH], rect_splash, SPLASH_GREEN, BLACK, self.button_font)
        self.button_rects[STATE_SPLASH] = rect_splash

        rect_shell = pygame.Rect(rect_splash.left, rect_splash.bottom + button_spacing, button_width, button_height)
        is_locked = self.total_score < SHELL_GAME_UNLOCK_SCORE
        button_text = self.game_names[STATE_SHELLGAME]
        if is_locked:
            button_text = f"Shell Game (Unlock at {SHELL_GAME_UNLOCK_SCORE} pts)"
        draw_button(self.screen, button_text, rect_shell, CARNIVAL_YELLOW, BLACK, self.button_font, locked=is_locked)
        self.button_rects[STATE_SHELLGAME] = rect_shell

        rect_prize = pygame.Rect(rect_shell.left, rect_shell.bottom + button_spacing, button_width, button_height)
        draw_button(self.screen, self.game_names[STATE_PRIZES], rect_prize, UI_BRIGHT_YELLOW, BLACK, self.header_font)
        self.button_rects[STATE_PRIZES] = rect_prize

        inst_surf = self.small_font.render("Press ESC to exit Arcade", True, DARK_GRAY)
        self.screen.blit(inst_surf, (SCREEN_WIDTH // 2 - inst_surf.get_width() // 2, SCREEN_HEIGHT - 30))

    def _draw_stats_screen(self):
        # overlay with recent session stats and highest per-game values
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        panel_w, panel_h = 450, 350
        x_offset = -50
        y_offset = -50
        panel_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - panel_w // 2 + x_offset,
            SCREEN_HEIGHT // 2 - panel_h // 2 + y_offset,
            panel_w, panel_h
        )
        panel_center_x = panel_rect.left + panel_w // 2

        pygame.draw.rect(self.screen, MENU_DARK_BLUE, panel_rect, 0, border_radius=20)
        pygame.draw.rect(self.screen, CARNIVAL_YELLOW, panel_rect, 5, border_radius=20)

        title_surf = self.header_font.render("ARCADE STATS", True, UI_BRIGHT_YELLOW)
        self.screen.blit(title_surf, title_surf.get_rect(center=(panel_center_x, panel_rect.top + 30)))

        total_surf = self.button_font.render(f"GRAND TOTAL: {self.total_score} Points", True, WHITE)
        self.screen.blit(total_surf, total_surf.get_rect(center=(panel_center_x, panel_rect.top + 80)))

        header_surf = self.ui_font.render("--- HIGHEST SCORE PER GAME (Session) ---", True, CARNIVAL_RED)
        self.screen.blit(header_surf, header_surf.get_rect(center=(panel_center_x, panel_rect.top + 130)))

        y_pos = panel_rect.top + 160
        game_states = [STATE_DARTPOP, STATE_HOOPSHOT, STATE_SPLASH, STATE_SHELLGAME]

        for game_state in game_states:
            game_name = self.game_names.get(game_state, "Unknown Game")
            high_score = self.game_high_scores.get(game_state, 0)
            rank_text = f"{game_name}: {high_score} Points"
            color = SPLASH_GREEN if high_score > 0 else WHITE
            score_surf = self.button_font.render(rank_text, True, color)
            self.screen.blit(score_surf, score_surf.get_rect(center=(panel_center_x, y_pos)))
            y_pos += 40

        exit_surf = self.ui_font.render("Press SPACE to return to Menu", True, DARK_GRAY)
        self.screen.blit(exit_surf, exit_surf.get_rect(center=(panel_center_x, panel_rect.bottom - 20)))

    def _draw_game_score(self):
        # small HUD showing current session and total score
        session_text = f"SESSION: {self.current_game_score}"
        session_surf = self.ui_font.render(session_text, True, UI_BRIGHT_YELLOW)
        self.screen.blit(session_surf, (SCREEN_WIDTH - session_surf.get_width() - 10, 10))

        total_text = f"TOTAL: {self.total_score} | ESC to Menu"
        total_surf = self.ui_font.render(total_text, True, UI_BRIGHT_YELLOW)
        self.screen.blit(total_surf, (SCREEN_WIDTH - total_surf.get_width() - 10, 40))

    def run(self):
        # main loop: handle input, update and draw current state
        last_time = time.time()

        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            self._handle_input()
            self._update_state(dt)

            if self.state == STATE_MENU:
                self._draw_menu()
            elif self.state == STATE_STATS:
                self._draw_menu()
                self._draw_stats_screen()
            elif self.state in self.games:
                game = self.games[self.state]
                if self.state == STATE_PRIZES:
                    game.draw(self.total_score)
                else:
                    game.draw()
                if self.state != STATE_PRIZES:
                    self._draw_game_score()

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    manager = ArcadeManager()
    manager.run()
    pygame.quit()
    sys.exit()

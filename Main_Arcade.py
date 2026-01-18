# FCA Jay's Carnival Arcade 
# Jayce McGibbon 
# 01/12/2026 
# This comprehensive arcade simulation integrates a variety of classic carnival challenges, including physics-based projectile mechanics and probability-driven logic, to provide a multifaceted interactive experience. (Juicemind version not recommended, use .exe version for performance, resolution fix, and audio support.)

#MODULE IMPORTS
import pygame
import sys
import time
import random
import math
import json
import os
from typing import List, Optional, Tuple

# RESOURCE PATH FUNCTIONALITY
def resource_path(relative_path):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# COLOUR PALETTE
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# UNLOCK THRESHOLDS
WHACK_GAME_UNLOCK_SCORE = 500
SHELL_GAME_UNLOCK_SCORE = 1500

PLAY_AREA_MARGIN = 50
UI_PADDING = 12
BUTTON_SPACING = 12

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (80, 80, 80)

CARNIVAL_RED = (200, 50, 50)
CARNIVAL_YELLOW = (255, 215, 0)
HOOP_BLUE = (0, 150, 255)
SPLASH_GREEN = (50, 200, 50)

UI_PLAYFUL = (150, 220, 255)
MENU_DARK_BLUE = (10, 10, 40)
OG_ORANGE = (255, 140, 0)
OG_BROWN = (139, 69, 19)
OG_WATER_CYAN = (100, 200, 255)

# STATE ENUM
STATE_MENU = 0
STATE_DARTPOP = 1
STATE_HOOPSHOT = 2
STATE_SPLASH = 3
STATE_SHELLGAME = 4
STATE_PRIZES = 5
STATE_STATS = 6
STATE_WHACK = 7
STATE_SETTINGS = 8

# GAME CONSTANTS
HIT_SCORE_INTERVAL = 0.5
MAX_SWING_ANGLE = math.pi / 4.5
SWING_SPEED = 1.0
STREAM_LENGTH = 450

SHUFFLE_EVENT = pygame.USEREVENT + 1
SHUFFLE_DURATION_MS = 500
INITIAL_REVEAL_DURATION_MS = 1500

SCORES_FILE = "arcade_high_scores.json"
PRIZE_STATE_FILE = "arcade_prize_state.json"
UNLOCK_STATE_FILE = "arcade_unlocks.json"

# PRIZE DATA
PRIZES = [
    {"id": "car", "name": "New Car", "cost": 50000},
    {"id": "scooter", "name": "Electric Scooter", "cost": 10000},
    {"id": "sword", "name": "Shiny Sword", "cost": 12000},
    {"id": "vr", "name": "VR Headset", "cost": 5000},
    {"id": "robot", "name": "Mini Robot", "cost": 1500},
    {"id": "nerf", "name": "Colored Nerf Gun", "cost": 3200},
    {"id": "lollipop", "name": "Giant Lollipop", "cost": 2500},
    {"id": "teddy", "name": "Teddy Bear", "cost": 500},
]

# SCORE ECONOMY
SCORE_SCALE_GLOBAL = 0.4

DARTPOP_BALLOON_SCORE = int(100 * SCORE_SCALE_GLOBAL)
DARTPOP_NEAR_MISS_SCORE = int(50 * SCORE_SCALE_GLOBAL)

HOOPSHOT_SWISH_BASE = int(250 * SCORE_SCALE_GLOBAL)
HOOPSHOT_SWISH_MAX_BONUS = 0.5

SHELLGAME_WIN_SCORE = int(1000 * SCORE_SCALE_GLOBAL)

WHACK_HIT_SCORE = int(75 * SCORE_SCALE_GLOBAL)

SPLASH_BULLSEYE_SCORE = max(1, int(10 * SCORE_SCALE_GLOBAL))

# ACCESSIBILITY DEFAULTS
ACCESSIBILITY_OPTIONS = {
    "mute": False,
    "monochrome": False,
    "slow_game": False,
    "reticle_alt": False,
}

# ATOMIC JSON WRITE
def atomic_write_json(path: str, data):
    try:
        dirpath = os.path.dirname(path) or "."
        tmp_path = os.path.join(dirpath, f".{os.path.basename(path)}.tmp")
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        os.replace(tmp_path, path)
    except Exception:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception:
            pass

# SAFE FONT LOADER
def safe_font(name=None, size=24, bold=False):
    try:
        if name:
            return pygame.font.SysFont(name, size, bold=bold)
        else:
            return pygame.font.SysFont(None, size, bold=bold)
    except Exception:
        return pygame.font.Font(pygame.font.get_default_font(), size)

# TEXT WRAPPING UTILITY
def wrap_text(font: pygame.font.Font, text: str, max_width: int) -> List[str]:
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

# ROUNDED BOX DRAWING
def draw_rounded_box(surface: pygame.Surface, rect: pygame.Rect,
                     fill_color: Optional[tuple] = None,
                     border_color: Optional[tuple] = None,
                     border_thickness: int = 0,
                     radius: int = 12):
    bt = max(0, int(border_thickness))
    radius = max(0, int(radius))
    if fill_color is not None:
        try:
            pygame.draw.rect(surface, fill_color, rect, 0, border_radius=radius)
        except Exception:
            pygame.draw.rect(surface, fill_color, rect)
    if border_color is not None and bt > 0:
        try:
            pygame.draw.rect(surface, border_color, rect, bt, border_radius=radius)
        except Exception:
            pygame.draw.rect(surface, border_color, rect, bt)

# BUTTON RENDERER
def draw_button(surface, text, rect, color, text_color, font, locked=False, hover=False):
    base_color = DARK_GRAY if locked else color

    if hover and not locked:
        base_color = tuple(min(255, int(c * 1.08 + 8)) for c in base_color)

    border_thickness = max(2, min(6, rect.height // 12))
    radius = max(8, rect.height // 3)

    shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 0))

    try:
        pygame.draw.rect(shadow, (0, 0, 0, 60), (4, 4, rect.width - 4, rect.height - 4), 0, border_radius=radius)
    except TypeError:
        pygame.draw.rect(shadow, (0, 0, 0, 60), (4, 4, rect.width - 4, rect.height - 4))

    surface.blit(shadow, rect.topleft)

    draw_rounded_box(surface, rect, fill_color=base_color,
                     border_color=CARNIVAL_YELLOW if not locked else BLACK,
                     border_thickness=border_thickness, radius=radius)

    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(rect.left + rect.width // 2, rect.top + rect.height // 2))

    surface.blit(text_surface, text_rect)

# PYGAME INIT
pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass
pygame.display.set_caption("Jay's Carnival Arcade")

import os
from typing import Optional

# PYGAME AVAILABILITY FLAG
try:
    import pygame
    _HAVE_PYGAME = True
except Exception:
    pygame = None
    _HAVE_PYGAME = False

# SOUND MANAGER CLASS
class SoundManager:
    # SOUND MANAGER INITIALIZER
    def __init__(self, sound_folder: str = ".", mute: Optional[bool] = None):
        try:
            default_mute = ACCESSIBILITY_OPTIONS.get("mute", False)
        except Exception:
            default_mute = False
        self.sound_folder = sound_folder
        self.muted = bool(default_mute) if mute is None else bool(mute)
        self._mixer_ready = False
        self._loaded = False
        self._spray_channel_index = 7
        self._cups_channel_index = 8
        self._spray_channel = None
        self._cups_channel = None
        self.sounds = {
            'pop': None,
            'buy': None,
            'cheer': None,
            'cups': None,
            'music': None,
            'selection': None,
            'spray': None,
            'swish': None,
            'throw': None,
            'throw2': None
        }
        self._init_mixer_and_load()
        if self.muted:
            try:
                if _HAVE_PYGAME and pygame.mixer.get_init():
                    try:
                        pygame.mixer.music.pause()
                    except Exception:
                        pass
                    try:
                        pygame.mixer.pause()
                    except Exception:
                        pass
            except Exception:
                pass

    # SOUNDMANAGER FILEPATH RESOLUTION
    def _file_path_if_exists(self, fname: str) -> Optional[str]:
        if not fname:
            return None
        try:
            if fname.lower().endswith('.mp3'):
                candidate = resource_path(os.path.join("Sounds", fname)) if not os.path.isabs(fname) else fname
                if os.path.isfile(candidate):
                    return candidate
            fpath = os.path.join(self.sound_folder, fname)
            if os.path.isfile(fpath):
                return fpath
            alt = os.path.join("Sounds", fname)
            if os.path.isfile(alt):
                return alt
        except Exception:
            pass
        return None

    # SOUND MANAGER MIXER INIT & LOAD
    def _init_mixer_and_load(self):
        if not _HAVE_PYGAME:
            self._mixer_ready = False
            return
        try:
            try:
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception:
                pass
            if not pygame.mixer.get_init():
                try:
                    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                except Exception:
                    try:
                        pygame.mixer.init()
                    except Exception:
                        self._mixer_ready = False
                        return
            try:
                needed = max(32, self._spray_channel_index + 1, self._cups_channel_index + 1)
                pygame.mixer.set_num_channels(needed)
            except Exception:
                pass
            try:
                self._spray_channel = pygame.mixer.Channel(self._spray_channel_index)
            except Exception:
                self._spray_channel = None
            try:
                self._cups_channel = pygame.mixer.Channel(self._cups_channel_index)
            except Exception:
                self._cups_channel = None
            mapping = {
                'pop': 'Burst.mp3',
                'buy': 'Buy.mp3',
                'cheer': 'Cheer.mp3',
                'cups': 'Cups.mp3',
                'music': 'Music.mp3',
                'selection': 'Selection.mp3',
                'spray': 'Spray.mp3',
                'swish': 'Swish.mp3',
                'throw': 'Throw.mp3',
                'throw2': 'Throw2.mp3'
            }
            for key, fname in mapping.items():
                path = self._file_path_if_exists(fname)
                if path:
                    try:
                        if key == 'music':
                            self.sounds[key] = path
                        else:
                            snd = pygame.mixer.Sound(path)
                            snd.set_volume(1.0)
                            self.sounds[key] = snd
                    except Exception:
                        self.sounds[key] = None
                else:
                    self.sounds[key] = None
            self._mixer_ready = True
            self._loaded = True
        except Exception:
            self._mixer_ready = False
            self._loaded = False

    # SOUNDMANAGER MUTE SETTER
    def set_mute(self, muted: bool):
        muted = bool(muted)
        if muted == self.muted:
            return
        self.muted = muted
        if not _HAVE_PYGAME:
            return
        try:
            if self.muted:
                try:
                    if pygame.mixer.get_init():
                        try:
                            pygame.mixer.music.pause()
                        except Exception:
                            pass
                        try:
                            pygame.mixer.pause()
                        except Exception:
                            pass
                except Exception:
                    pass
            else:
                if not pygame.mixer.get_init():
                    try:
                        pygame.mixer.init()
                        self._init_mixer_and_load()
                    except Exception:
                        pass
                try:
                    pygame.mixer.music.unpause()
                except Exception:
                    pass
                try:
                    pygame.mixer.unpause()
                except Exception:
                    pass
        except Exception:
            pass

    # GENERIC PLAY SOUND HELPER
    def _play_sound(self, key: str, allow_overlap: bool = True, volume: Optional[float] = None) -> bool:
        if self.muted:
            return False
        if not self._loaded or not self._mixer_ready:
            return False
        snd = self.sounds.get(key)
        if snd is None:
            return False
        try:
            if volume is not None:
                try:
                    snd.set_volume(max(0.0, min(1.0, float(volume))))
                except Exception:
                    pass
            if allow_overlap:
                snd.play()
            else:
                ch = pygame.mixer.find_channel()
                if ch is None:
                    snd.play()
                else:
                    ch.play(snd)
            return True
        except Exception:
            return False

    # BACKGROUND MUSIC PLAYER
    def play_background_music(self, loop: bool = True, volume: float = 0.2):
        if self.muted:
            return
        if not self._loaded or not self._mixer_ready:
            return
        music_path = self.sounds.get('music')
        if isinstance(music_path, str):
            try:
                if not pygame.mixer.get_init():
                    try:
                        pygame.mixer.init()
                    except Exception:
                        pass
                if pygame.mixer.music.get_busy():
                    return
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(max(0.0, min(1.0, float(volume))))
                pygame.mixer.music.play(-1 if loop else 0)
                return
            except Exception:
                pass
        try:
            cheer = self.sounds.get('cheer')
            if cheer:
                cheer.play()
                return
        except Exception:
            return

    # PLAY POP SFX
    def play_pop(self, context: Optional[str] = None):
        self._play_sound('pop', allow_overlap=True, volume=0.8)

    # PLAY SELECTION SFX
    def play_selection(self):
        self._play_sound('selection', allow_overlap=True, volume=0.7)

    # PLAY BUY SFX
    def play_buy(self):
        self._play_sound('buy', allow_overlap=False, volume=0.9)

    # PLAY FANFARE SFX
    def play_fanfare(self):
        self._play_sound('cheer', allow_overlap=True, volume=0.95)

    # PLAY SWISH + CHEER COMBO
    def play_swish_cheer(self, intensity: Optional[str] = None):
        played = self._play_sound('swish', allow_overlap=True, volume=0.6)
        if intensity and intensity.lower() in ('perfect', 'big', 'strong'):
            self._play_sound('cheer', allow_overlap=True, volume=0.9)
        return played

    # PLAY THROW SFX
    def play_throw(self, variant: int = 1):
        if variant == 2 and self.sounds.get('throw2'):
            if not self._play_sound('throw2', allow_overlap=True, volume=0.9):
                self._play_sound('throw', allow_overlap=True, volume=0.9)
        else:
            self._play_sound('throw', allow_overlap=True, volume=0.9)

    # PLAY WATER SPRAY LOOP
    def play_water_spray(self, start: bool = True):
        if self.muted or not self._loaded or not self._mixer_ready:
            return
        key = 'spray'
        if start:
            snd = self.sounds.get(key)
            if snd is None:
                return
            try:
                if self._spray_channel:
                    self._spray_channel.play(snd, loops=-1)
                    try:
                        self._spray_channel.set_volume(0.6)
                    except Exception:
                        pass
                else:
                    ch = pygame.mixer.find_channel()
                    if ch:
                        ch.play(snd, loops=-1)
            except Exception:
                pass
        else:
            try:
                if self._spray_channel:
                    try:
                        self._spray_channel.fadeout(250)
                    except Exception:
                        self._spray_channel.stop()
                else:
                    snd = self.sounds.get(key)
                    if snd:
                        try:
                            snd.stop()
                        except Exception:
                            pass
            except Exception:
                pass

    # START CUPS LOOP
    def start_cups(self):
        if self.muted or not self._loaded or not self._mixer_ready:
            return
        snd = self.sounds.get('cups')
        if snd is None:
            return
        try:
            if self._cups_channel:
                self._cups_channel.play(snd, loops=-1)
            else:
                ch = pygame.mixer.find_channel()
                if ch:
                    ch.play(snd, loops=-1)
        except Exception:
            pass

    # STOP CUPS LOOP
    def stop_cups(self):
        if self.muted or not self._loaded or not self._mixer_ready:
            return
        try:
            if self._cups_channel:
                try:
                    self._cups_channel.stop()
                except Exception:
                    pass
            else:
                try:
                    pygame.mixer.stop()
                except Exception:
                    pass
        except Exception:
            pass

# PRIZE ICON CACHE
_icon_cache = {}

# PRIZE ICON RENDERER
def create_prize_icon_surf(icon_id: str, size: int = 64):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size // 2, size // 2)
    if icon_id == "teddy":
        face_r = size // 3
        ear_r = max(6, size // 8)
        pygame.draw.circle(surf, OG_ORANGE, (center[0] - face_r + 6, center[1] - face_r + 6), ear_r)
        pygame.draw.circle(surf, OG_ORANGE, (center[0] + face_r - 6, center[1] - face_r + 6), ear_r)
        pygame.draw.circle(surf, CARNIVAL_RED, center, face_r)
        pygame.draw.circle(surf, BLACK, (center[0] - 10, center[1] - 6), max(2, size // 12))
        pygame.draw.circle(surf, BLACK, (center[0] + 10, center[1] - 6), max(2, size // 12))
    elif icon_id == "robot":
        head_h = int(size * 0.46)
        head_w = int(size * 0.72)
        head_x = int((size - head_w) / 2)
        head_y = int(size * 0.18)
        try:
            pygame.draw.rect(surf, (200, 200, 220), (head_x, head_y, head_w, head_h), border_radius=8)
            pygame.draw.rect(surf, DARK_GRAY, (head_x, head_y, head_w, head_h), 2, border_radius=8)
        except TypeError:
            pygame.draw.rect(surf, (200, 200, 220), (head_x, head_y, head_w, head_h))
            pygame.draw.rect(surf, DARK_GRAY, (head_x, head_y, head_w, head_h), 2)
        eye_r = max(2, size // 16)
        pygame.draw.circle(surf, (20, 20, 20), (head_x + head_w // 3, head_y + head_h // 2), eye_r)
        pygame.draw.circle(surf, (20, 20, 20), (head_x + 2 * head_w // 3, head_y + head_h // 2), eye_r)
        pygame.draw.rect(surf, (120, 120, 140), (head_x + head_w // 4, head_y + head_h - 12, head_w // 2, 6))
        pygame.draw.line(surf, (180, 60, 60), (center[0], head_y - 6), (center[0], head_y + 4), 2)
        body_h = int(size * 0.24)
        body_w = int(size * 0.6)
        body_x = (size - body_w) // 2
        body_y = head_y + head_h + 6
        pygame.draw.rect(surf, (180, 180, 200), (body_x, body_y, body_w, body_h), border_radius=6)
        pygame.draw.rect(surf, DARK_GRAY, (body_x + 6, body_y + 6, body_w - 12, body_h - 12), 1)
    elif icon_id == "lollipop":
        candy_r = size // 4
        candy_center = (center[0], center[1] - 6)
        pygame.draw.circle(surf, (255, 120, 180), candy_center, candy_r)
        stick_top = (center[0], candy_center[1] + candy_r - 2)
        stick_bottom = (center[0], center[1] + size // 3)
        pygame.draw.line(surf, (200, 180, 140), stick_top, stick_bottom, max(2, size // 18))
    elif icon_id == "vr":
        try:
            pygame.draw.rect(surf, (30, 30, 30), (int(size * 0.12), int(size * 0.35), int(size * 0.76), int(size * 0.28)), border_radius=8)
            pygame.draw.rect(surf, (80, 180, 220), (int(size * 0.22), int(size * 0.4), int(size * 0.56), int(size * 0.18)), border_radius=6)
        except TypeError:
            pygame.draw.rect(surf, (30, 30, 30), (int(size * 0.12), int(size * 0.35), int(size * 0.76), int(size * 0.28)))
            pygame.draw.rect(surf, (80, 180, 220), (int(size * 0.22), int(size * 0.4), int(size * 0.56), int(size * 0.18)))
    elif icon_id == "scooter":
        deck_w = int(size * 0.64)
        deck_h = max(3, int(size * 0.08))
        deck_x = int((size - deck_w) / 2)
        deck_y = int(size * 0.62)
        pygame.draw.rect(surf, (80, 80, 80), (deck_x, deck_y, deck_w, deck_h), border_radius=3)
        wheel_r = max(4, size // 12)
        pygame.draw.circle(surf, BLACK, (deck_x + 10, deck_y + deck_h + wheel_r), wheel_r)
        pygame.draw.circle(surf, BLACK, (deck_x + deck_w - 10, deck_y + deck_h + wheel_r), wheel_r)
        pygame.draw.line(surf, (60, 60, 60), (deck_x + 10, deck_y), (deck_x + 10, deck_y - 28), 4)
        pygame.draw.line(surf, (60, 60, 60), (deck_x + 2, deck_y - 28), (deck_x + 18, deck_y - 28), 4)
    elif icon_id == "car":
        try:
            pygame.draw.rect(surf, (30, 120, 200), (int(size * 0.12), int(size * 0.45), int(size * 0.76), int(size * 0.28)), border_radius=8)
            wheel_r = max(4, size // 10)
            pygame.draw.circle(surf, BLACK, (int(size * 0.25), int(size * 0.76)), wheel_r)
            pygame.draw.circle(surf, BLACK, (int(size * 0.75), int(size * 0.76)), wheel_r)
        except TypeError:
            pygame.draw.rect(surf, (30, 120, 200), (int(size * 0.12), int(size * 0.45), int(size * 0.76), int(size * 0.28)))
            wheel_r = max(4, size // 10)
            pygame.draw.circle(surf, BLACK, (int(size * 0.25), int(size * 0.76)), wheel_r)
            pygame.draw.circle(surf, BLACK, (int(size * 0.75), int(size * 0.76)), wheel_r)
    elif icon_id == "sword":
        blade_w = max(4, size // 10)
        blade_h = int(size * 0.6)
        blade_x = size // 2 - blade_w // 2
        blade_y = int(size * 0.12)
        pygame.draw.rect(surf, (220, 220, 240), (blade_x, blade_y, blade_w, blade_h))
        pygame.draw.rect(surf, (180, 120, 20), (blade_x - 6, blade_y + blade_h, blade_w + 12, 6))
        pygame.draw.rect(surf, (80, 40, 20), (blade_x - 2, blade_y + blade_h + 6, blade_w + 4, 12))
    elif icon_id == "nerf":
        body_w = int(size * 0.72)
        body_h = int(size * 0.22)
        body_x = int((size - body_w) / 2)
        body_y = int(size * 0.35)
        pygame.draw.rect(surf, (255, 110, 110), (body_x, body_y, body_w, body_h), border_radius=6)
        pygame.draw.rect(surf, (30, 30, 30), (body_x + body_w - int(body_w * 0.25), body_y + body_h // 4, int(body_w * 0.25), body_h // 2))
        pygame.draw.rect(surf, (60, 60, 80), (body_x - 6, body_y + body_h // 4, int(body_w * 0.55), body_h // 2), border_radius=4)
        pygame.draw.circle(surf, (255, 180, 60), (body_x + body_w + 6, body_y + body_h // 2), max(6, size // 16))
    else:
        f = safe_font(size=size // 2)
        txt = f.render("?", True, WHITE)
        surf.blit(txt, txt.get_rect(center=center))
    return surf

# PRIZE ICON CACHER
def get_prize_icon(icon_id: str, size: int = 64):
    key = (icon_id, size)
    if key not in _icon_cache:
        _icon_cache[key] = create_prize_icon_surf(icon_id, size=size)
    return _icon_cache[key]

# PRIZE ICON BLITTER
def draw_prize_icon(surface, topleft, icon_id: str, size: int = 48):
    surf = get_prize_icon(icon_id, size=size)
    surface.blit(surf, topleft)

# CLOWN VISUAL HELPER CLASS
class Clown:
    # CLOWN INIT
    def __init__(self, center_x, center_y, size=72):
        self.clown_size = int(size)
        self.visual_size = max(self.clown_size + 24, int(self.clown_size * 1.4))
        self.center_x = int(center_x)
        self.center_y = int(center_y)
        self.is_hit = False
        self.visible_state = True
        self.hair_puffs = self._generate_hair_puffs(seed=(self.center_x ^ self.center_y) & 0xFFFF)
        self.image = pygame.Surface((self.visual_size, self.visual_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.center_x, self.center_y))
        self._redraw()

    # HAIR PUFFS GENERATOR
    def _generate_hair_puffs(self, seed=None):
        rng = random.Random(seed)
        puff_centers = []
        hair_width = max(self.clown_size + 4, int((self.clown_size // 2) * 2.4))
        hair_height = max(int((self.clown_size // 2) * 0.65), int(self.clown_size * 0.6))
        hair_center_y = self.visual_size // 2 - int((self.clown_size // 2) * 0.35)
        puff_spacing = int(hair_width // 7) if hair_width >= 70 else 10
        puff_radius = int(max(8, hair_height * 0.48))
        start_x = (self.visual_size // 2) - hair_width // 2
        x = start_x
        while x <= start_x + hair_width:
            y = hair_center_y + rng.randint(-4, 6)
            puff_centers.append((int(x), int(y)))
            x += puff_spacing
        side_offset = int(puff_radius * 0.9)
        puff_centers.append(((self.visual_size // 2) - hair_width // 2 - side_offset // 2, hair_center_y + rng.randint(-8, 2)))
        puff_centers.append(((self.visual_size // 2) + hair_width // 2 + side_offset // 2, hair_center_y + rng.randint(-8, 2)))
        puff_centers.append(((self.visual_size // 2) - int(puff_spacing * 1.5), hair_center_y - int(puff_radius * 0.6)))
        puff_centers.append(((self.visual_size // 2) + int(puff_spacing * 1.5), hair_center_y - int(puff_radius * 0.6)))
        puff_centers.append(((self.visual_size // 2), hair_center_y - int(puff_radius * 0.9)))
        return puff_centers

    # CLOWN REDRAW
    def _redraw(self):
        draw_clown_face_centered(self.image, self.clown_size, self.is_hit, self.visual_size, hair_puffs=self.hair_puffs)

    # MARK HIT
    def mark_hit(self):
        self.is_hit = True
        self._redraw()

    # RESET STATE
    def reset(self):
        self.is_hit = False
        self.visible_state = True
        self._redraw()

    # UPDATE VISUAL
    def update_visual(self, is_hit_flag: bool):
        self.is_hit = bool(is_hit_flag)
        self._redraw()

# PRIZE SCREEN CLASS
class PrizeScreen:
    # PRIZE SCREEN INIT
    def __init__(self, screen, font, sound_manager, manager=None):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager
        self.manager = manager
        self.small_font = safe_font(size=16)
        self.prize_font = safe_font(size=20)
        self.room_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.floor_y = SCREEN_HEIGHT - 80
        self.prize_positions = self._compute_prize_positions()
        self.prize_item_rects = {}
        self.modal_active = False
        self.modal_prize_id = None
        self.modal_message = ""
        self.modal_buttons = {}
        self.scroll_offset = 0
        self.scroll_speed = 32
        if self.manager and hasattr(self.manager, 'prize_unlocked'):
            self.unlocked = dict(self.manager.prize_unlocked)
        else:
            self.unlocked = {p['id']: False for p in PRIZES}
        self.header_font = safe_font(size=26)

    # PRIZE POSITIONS COMPUTATION
    def _compute_prize_positions(self):
        cols = 2
        rows = 4
        positions = []
        icon_w = 76
        left_pad = 100
        right_pad = 100
        usable_width = SCREEN_WIDTH - left_pad - right_pad
        col_spacing = usable_width / (cols - 1) if cols > 1 else usable_width
        top_start = 120
        row_spacing = 110
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                if idx >= len(PRIZES):
                    break
                x_center = int(left_pad + c * col_spacing)
                y_center = int(top_start + r * row_spacing)
                positions.append((x_center - icon_w // 2, y_center - icon_w // 2))
        return positions

    # RESET SCREEN
    def reset(self):
        self.scroll_offset = 0
        self.modal_active = False
        self.modal_prize_id = None

    # CLAMP SCROLL
    def _clamp_scroll(self):
        self.scroll_offset = max(0, min(self.scroll_offset, 200))

    # INPUT HANDLER
    def handle_input(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * self.scroll_speed
            self._clamp_scroll()
        if self.modal_active:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mpos = event.pos
                for name, rect in self.modal_buttons.items():
                    if rect.collidepoint(mpos):
                        if name == 'buy' or name == 'purchase':
                            self._attempt_purchase(self.modal_prize_id)
                        elif name == 'cancel':
                            self.modal_active = False
                            self.modal_prize_id = None
                        break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.modal_active = False
                self.modal_prize_id = None
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mpos = event.pos
            for pid, rect in self.prize_item_rects.items():
                if rect.collidepoint(mpos):
                    if self.unlocked.get(pid, False):
                        self.modal_active = True
                        self.modal_prize_id = pid
                        self.modal_message = f"You already own the {self._prize_by_id(pid)['name']}!"
                        cancel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 28, 120, 36)
                        self.modal_buttons = {'cancel': cancel_rect}
                    else:
                        self.modal_active = True
                        self.modal_prize_id = pid
                        cost = self._prize_by_id(pid)['cost']
                        self.modal_message = f"Purchase {self._prize_by_id(pid)['name']} for {cost} points?"
                        buy_rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 28, 120, 36)
                        cancel_rect = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 28, 120, 36)
                        self.modal_buttons = {'buy': buy_rect, 'cancel': cancel_rect}
                    break

    # LOOKUP PRIZE BY ID
    def _prize_by_id(self, pid):
        for p in PRIZES:
            if p['id'] == pid:
                return p
        return None

    # ATTEMPT PURCHASE
    def _attempt_purchase(self, pid):
        prize = self._prize_by_id(pid)
        if prize is None:
            self.modal_active = False
            self.modal_prize_id = None
            return
        cost = prize['cost']
        if self.manager is None:
            self.modal_active = False
            self.modal_prize_id = None
            return
        if getattr(self.manager, 'total_score', 0) >= cost:
            self.manager.total_score -= cost
            self.unlocked[pid] = True
            self.manager.prize_unlocked = self.unlocked
            try:
                self.manager._save_prizes()
            except Exception:
                pass
            self.modal_message = f"Purchased {prize['name']}! Congratulations!"
            try:
                self.sound_manager.play_buy()
            except Exception:
                pass
            try:
                self.sound_manager.play_fanfare()
            except Exception:
                pass
            cancel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 28, 120, 36)
            self.modal_buttons = {'cancel': cancel_rect}
        else:
            self.modal_message = "Insufficient points! Play more to earn this prize."
            cancel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 28, 120, 36)
            self.modal_buttons = {'cancel': cancel_rect}

    # UPDATE NO-OP
    def update(self, dt):
        return 0

    # DRAW PRIZE SCREEN
    def draw(self, total_score):
        self.screen.fill((28, 18, 30))

        title = self.font.render("PRIZE ROOM", True, CARNIVAL_YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 24))

        hud = self.small_font.render(f"POINTS: {total_score}", True, UI_PLAYFUL)
        self.screen.blit(hud, (SCREEN_WIDTH - hud.get_width() - 12, 12))

        self.prize_item_rects.clear()
        icon_size = 76

        for i, prize in enumerate(PRIZES):
            pos = self.prize_positions[i]
            px, py = pos
            display_x = px
            display_y = py

            pedestal_rect = pygame.Rect(display_x - 8, display_y + icon_size - 10, icon_size + 16, 14)
            pygame.draw.rect(self.screen, OG_BROWN, pedestal_rect)

            icon_surf = get_prize_icon(prize['id'], size=icon_size)
            unlocked = self.unlocked.get(prize['id'], False)

            if unlocked:
                self.screen.blit(icon_surf, (display_x, display_y))

                try:
                    pygame.draw.rect(self.screen, CARNIVAL_YELLOW, (display_x - 6, display_y - 6, icon_size + 12, icon_size + 12), 3, border_radius=8)
                except TypeError:
                    pygame.draw.rect(self.screen, CARNIVAL_YELLOW, (display_x - 6, display_y - 6, icon_size + 12, icon_size + 12), 3)

            else:
                faded = icon_surf.copy()

                try:
                    fade_overlay = pygame.Surface(faded.get_size(), pygame.SRCALPHA)
                    fade_overlay.fill((90, 90, 90, 200))
                    faded.blit(fade_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                except Exception:
                    faded.set_alpha(120)

                self.screen.blit(faded, (display_x, display_y))

                lock_x = display_x + icon_size - 18
                lock_y = display_y + 6
                pygame.draw.circle(self.screen, DARK_GRAY, (lock_x, lock_y), 10)
                pygame.draw.rect(self.screen, BLACK, (lock_x - 6, lock_y + 2, 12, 8))

            if unlocked:
                status_text = "OWNED"
                status_color = SPLASH_GREEN
            else:
                status_text = f"{prize['cost']} pts"
                status_color = CARNIVAL_YELLOW if total_score >= prize['cost'] else CARNIVAL_RED

            name_surf = self.small_font.render(prize['name'], True, WHITE)
            stat_surf = self.small_font.render(status_text, True, status_color)

            name_x = display_x + (icon_size // 2) - (name_surf.get_width() // 2)
            name_y = display_y + icon_size - 6
            stat_x = display_x + (icon_size // 2) - (stat_surf.get_width() // 2)
            stat_y = display_y + icon_size + 14

            self.screen.blit(name_surf, (name_x, name_y))
            self.screen.blit(stat_surf, (stat_x, stat_y))

            bounding = pygame.Rect(display_x - 6, display_y - 6, icon_size + 12, icon_size + 56)
            self.prize_item_rects[prize['id']] = bounding

        if self.modal_active:
            panel_w = 520
            panel_h = 150
            panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - panel_w // 2, SCREEN_HEIGHT // 2 - panel_h // 2, panel_w, panel_h)

            draw_rounded_box(self.screen, panel_rect, fill_color=MENU_DARK_BLUE, border_color=CARNIVAL_YELLOW, border_thickness=4, radius=12)

            title = self.header_font.render("PRIZE INTERACTION", True, UI_PLAYFUL)
            self.screen.blit(title, (panel_rect.left + 20, panel_rect.top + 12))

            msg_lines = wrap_text(self.small_font, self.modal_message, panel_w - 40)
            y = panel_rect.top + 44

            for line in msg_lines:
                surf = self.small_font.render(line, True, WHITE)
                self.screen.blit(surf, (panel_rect.left + 20, y))
                y += surf.get_height() + 6

            for name, rect in self.modal_buttons.items():
                is_buy = (name == 'buy' or name == 'purchase')
                color = SPLASH_GREEN if is_buy else (60, 60, 60)

                draw_button(self.screen, name.upper(), rect, color, BLACK, self.small_font, locked=False, hover=False)

    # PRIZE CLEANUP
    def cleanup(self):
        pass

# ANGLE DISTANCE UTILITY
def _angle_distance(a, b):
    diff = (a - b + math.pi) % (2 * math.pi) - math.pi
    return abs(diff)

# DART POP GAME CLASS
class DartPopGame:
    # DARTPOP INIT
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
        self.hit_angle_tolerance = 0.26
        self.reticle_mode = 'circle'
        self.reset()
        self.message = "Press SPACE to throw the dart! (Press F to toggle reticle mode)"

    # BALLOON GENERATOR
    def generate_balloons(self):
        self.balloons = []
        balloon_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        color_choices = [HOOP_BLUE, CARNIVAL_YELLOW, OG_ORANGE, SPLASH_GREEN, UI_PLAYFUL]
        for angle in balloon_angles:
            x = self.center_x + self.arm_length * math.cos(angle)
            y = self.center_y + self.arm_length * math.sin(angle)
            size = random.randint(18, 24)
            color = random.choice(color_choices)
            self.balloons.append({'pos': (int(x), int(y)), 'size': size, 'color': color, 'hit': False})

    # RESET GAME
    def reset(self):
        self.game_time = 0.0
        self.dart_thrown = False
        self.hit_result = None
        self.bullseye_radius = 20
        sign = random.choice([-1, 1])
        base_speed = 1.2 * random.uniform(0.85, 1.55)
        self.rotation_speed = sign * max(0.7, min(2.2, base_speed))
        self.generate_balloons()
        self.message = "Press SPACE to throw the dart! (Press F to toggle reticle mode)"

    # RETICLE POSITION
    def _reticle_pos(self, t):
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

    # INPUT HANDLER
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
                            hit_score += DARTPOP_BALLOON_SCORE
                            try:
                                self.sound_manager.play_pop()
                            except Exception:
                                pass
                if hit_balloon:
                    self.hit_result = 'HIT'
                    score_to_report = hit_score
                    self.message = f"POP! +{score_to_report} Points! (Press R to Reset/Continue)"
                else:
                    normalized_angle = (t) % (2 * math.pi)
                    angle_dist = _angle_distance(normalized_angle, self.target_angle)
                    if angle_dist < self.hit_angle_tolerance:
                        self.hit_result = 'NEAR_MISS'
                        score_to_report = DARTPOP_NEAR_MISS_SCORE
                        self.message = f"Good Timing! +{score_to_report} Points! (Press R to Reset/Continue)"
                    else:
                        self.hit_result = 'MISS'
                        score_to_report = 0
                        self.message = "MISS! (Press R to Reset/Continue)"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if self.dart_thrown:
                self.reset()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            if self.reticle_mode == 'circle':
                self.reticle_mode = 'figure8'
                self.message = "Reticle: FIGURE-8 mode (Press F to toggle)"
            else:
                self.reticle_mode = 'circle'
                self.message = "Reticle: CIRCULAR mode (Press F to toggle)"
        return score_to_report

    # UPDATE GAME
    def update(self, dt):
        if not self.dart_thrown:
            self.game_time += dt
        return 0

    # DRAW GAME
    def draw(self):
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
                pygame.draw.circle(self.screen, balloon['color'], balloon['pos'], balloon['size'])

        t = self.game_time * self.rotation_speed
        end_x, end_y = self._reticle_pos(t)
        reticle_color = UI_PLAYFUL if not ACCESSIBILITY_OPTIONS["reticle_alt"] else (255, 180, 180)

        if not self.dart_thrown:
            pygame.draw.circle(self.screen, reticle_color, (int(end_x), int(end_y)), 8)

        if self.dart_thrown:
            dart_x, dart_y = self._reticle_pos(t)
            color = SPLASH_GREEN if self.hit_result != 'MISS' else CARNIVAL_RED
            pygame.draw.circle(self.screen, color, (int(dart_x), int(dart_y)), 12)

        self._draw_message()

    # DRAW MESSAGE
    def _draw_message(self):
        max_w = SCREEN_WIDTH - 40
        lines = wrap_text(self.font, self.message, max_w)
        y = self.PLAY_AREA_RECT.bottom + 8
        for line in lines:
            surf = self.font.render(line, True, UI_PLAYFUL)
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))
            y += surf.get_height() + 2

    # CLEANUP
    def cleanup(self):
        pass

# SWAY OBJECT SPRITE CLASS
class SwayObject(pygame.sprite.Sprite):
    # SWAY INIT
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

    # UPDATE SWAY
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

# BASKETBALL SPRITE
class Basketball(pygame.sprite.Sprite):
    # BASKETBALL INIT
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

    # UPDATE BASKETBALL
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

# HOOP SHOT GAME CLASS
class HoopShotGame:
    # HOOPSHOT INIT
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
        self.hoop_center_x = self.PLAY_AREA_RECT.right - 100
        self.hoop_center_y = self.PLAY_AREA_CENTER_Y
        self.hoop_radius = 80
        self.hoop_reticle_angle = 0.0
        self.hoop_reticle_speed = 1.2
        self.time_lerp_speed = 6.0
        self.last_shot_time = 0.0
        self.shot_cooldown = 0.6
        self.reset()

    # RESET HOOPSHOT
    def reset(self):
        self.shot_result = "Press SPACE to shoot!"
        self.swish_combo = 0
        self.combo_max = 8
        self.base_speed_multiplier = 1.0
        self.bar_center_x = self.PLAY_AREA_RECT.left + 80
        self.bar_center_y = self.PLAY_AREA_CENTER_Y
        self.bar_amplitude = self.PLAY_AREA_RECT.height // 2 - 50
        self.zone_height = 50
        freq = 1.0 + (self.swish_combo * 0.10)
        freq = min(freq, 2.5)
        self.power_meter = SwayObject(
            center_x=self.bar_center_x,
            center_y=self.bar_center_y,
            amplitude=self.bar_amplitude,
            frequency=freq,
            pattern=1,
            color=UI_PLAYFUL,
            size=18
        )
        self.all_sprites = pygame.sprite.Group(self.power_meter)
        self.shooter_x = self.PLAY_AREA_RECT.left + 150
        self.shooter_y = self.PLAY_AREA_RECT.bottom - 50
        self.perfect_zone_rect = pygame.Rect(0, 0, 0, 0)
        self._randomize_target_zone()

    # RANDOMIZE TARGET ZONE
    def _randomize_target_zone(self):
        min_top_y = self.bar_center_y - self.bar_amplitude
        max_top_y = self.bar_center_y + self.bar_amplitude - self.zone_height
        self.perfect_zone_top = random.randint(int(min_top_y), int(max_top_y))
        self.perfect_zone_bottom = self.perfect_zone_top + self.zone_height
        self.perfect_zone_rect = pygame.Rect(
            int(self.bar_center_x - 10), int(self.perfect_zone_top), 20, self.zone_height
        )

    # CHECK SHOT
    def _check_shot(self):
        score_to_report = 0
        indicator_y = self.power_meter.rect.centery
        arc_type = 'miss'
        now = time.time()
        if now - self.last_shot_time < self.shot_cooldown:
            self.shot_result = "Shot cooldown..."
            return 0
        speed_multiplier = 1.0 + (self.swish_combo * 0.06)
        speed_multiplier = min(speed_multiplier, 1.4)
        self.power_meter.frequency = 1.0 + (self.swish_combo * 0.08)
        self.power_meter.frequency = min(self.power_meter.frequency, 2.5)
        if self.perfect_zone_top <= indicator_y <= self.perfect_zone_bottom:
            combo_bonus = min(self.swish_combo * 0.06, HOOPSHOT_SWISH_MAX_BONUS)
            raw_score = int(HOOPSHOT_SWISH_BASE * (1.0 + combo_bonus))
            score_to_report = raw_score
            self.shot_result = f"SWISH! Perfect Shot! +{score_to_report} Points!"
            arc_type = 'swish'
            try:
                self.sound_manager.play_swish_cheer(intensity='perfect')
            except Exception:
                pass
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
        try:
            self.sound_manager.play_throw()
        except Exception:
            pass
        self.power_meter.time_offset = pygame.time.get_ticks()
        self._randomize_target_zone()
        self.last_shot_time = time.time()
        return score_to_report

    # INPUT HANDLER
    def handle_input(self, event):
        score_change = 0
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            score_change = self._check_shot()
        return score_change

    # UPDATE
    def update(self, dt):
        self.all_sprites.update()
        for sprite in list(self.all_sprites):
            if isinstance(sprite, Basketball) and not sprite.in_flight and sprite.alive():
                try:
                    sprite.kill()
                except Exception:
                    pass
        self.hoop_reticle_angle += self.hoop_reticle_speed * dt
        self.hoop_reticle_angle %= (2 * math.pi)
        return 0

    # DRAW
    def draw(self):
        self.screen.fill(HOOP_BLUE)

        pygame.draw.rect(self.screen, BLACK, self.PLAY_AREA_RECT)

        track_rect = pygame.Rect(
            int(self.power_meter.start_x - 10), int(self.power_meter.start_y - self.bar_amplitude), 20, int(self.bar_amplitude * 2)
        )

        try:
            pygame.draw.rect(self.screen, DARK_GRAY, track_rect, 0, border_radius=5)
            pygame.draw.rect(self.screen, SPLASH_GREEN, self.perfect_zone_rect, 0, border_radius=5)
        except TypeError:
            pygame.draw.rect(self.screen, DARK_GRAY, track_rect)
            pygame.draw.rect(self.screen, SPLASH_GREEN, self.perfect_zone_rect)

        pygame.draw.circle(self.screen, WHITE, (int(self.shooter_x), int(self.shooter_y)), 25)
        pygame.draw.circle(self.screen, DARK_GRAY, (int(self.shooter_x), int(self.shooter_y)), 25, 3)

        rim_center_x = self.hoop_center_x - 40
        hoop_center_x = rim_center_x
        hoop_center_y = self.hoop_center_y

        backboard_rect = (rim_center_x + 40, hoop_center_y - 75, 10, 150)
        pygame.draw.rect(self.screen, WHITE, backboard_rect)

        net_top_width = 70
        net_bottom_width = 42
        net_height = 78
        net_top_y = hoop_center_y + 8
        net_bottom_y = hoop_center_y + net_height

        net_top_left = (rim_center_x - net_top_width // 2, net_top_y)
        net_top_right = (rim_center_x + net_top_width // 2, net_top_y)
        net_bottom_left = (rim_center_x - net_bottom_width // 2, net_bottom_y)
        net_bottom_right = (rim_center_x + net_bottom_width // 2, net_bottom_y)

        num_strings = 6
        for i in range(num_strings):
            t = i / (num_strings - 1)
            top_x = net_top_left[0] + t * (net_top_right[0] - net_top_left[0])
            bottom_x = net_bottom_left[0] + t * (net_bottom_right[0] - net_bottom_left[0])
            pygame.draw.line(self.screen, WHITE, (top_x, net_top_y), (bottom_x, net_bottom_y), 1)

        pygame.draw.line(self.screen, WHITE, net_top_left, net_bottom_left, 2)
        pygame.draw.line(self.screen, WHITE, net_top_right, net_bottom_right, 2)
        pygame.draw.line(self.screen, WHITE, net_bottom_left, net_bottom_right, 2)
        pygame.draw.line(self.screen, WHITE, net_top_left, net_top_right, 2)

        rim_rect = (rim_center_x - 40, hoop_center_y - 15, 80, 30)
        pygame.draw.ellipse(self.screen, DARK_GRAY, rim_rect, 8)

        front_rim_rect = (rim_center_x - 36, hoop_center_y - 8, 72, 18)
        pygame.draw.ellipse(self.screen, DARK_GRAY, front_rim_rect, 6)

        self.all_sprites.draw(self.screen)

        combo_text = f"Combo: {self.swish_combo}"
        combo_surf = self.font.render(combo_text, True, UI_PLAYFUL)
        self.screen.blit(combo_surf, (20, 20))

        msg_lines = wrap_text(self.font, self.shot_result, SCREEN_WIDTH // 2)
        y = SCREEN_HEIGHT - 30

        for line in reversed(msg_lines):
            surf = self.font.render(line, True, UI_PLAYFUL)
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y - surf.get_height()))
            y -= surf.get_height() + 2

    # CLEANUP
    def cleanup(self):
        try:
            self.all_sprites.empty()
        except Exception:
            pass

# CLOWN FACE RENDERER
def draw_clown_face_centered(surface, clown_size, hit, surface_size, hair_puffs: Optional[List[Tuple[int, int]]] = None):
    surface.fill((0, 0, 0, 0))
    center = (surface_size // 2, surface_size // 2)
    radius = clown_size // 2

    hair_width = max(clown_size + 4, int(radius * 2.4))
    hair_height = max(int(radius * 0.65), int(clown_size * 0.6))
    hair_center_y = center[1] - int(radius * 0.35)

    hair_color_base = (170, 30, 30)
    hair_color_highlight = (220, 60, 60)
    puff_radius = int(max(8, hair_height * 0.48))

    if hair_puffs:
        puff_centers = hair_puffs
    else:
        puff_centers = []
        puff_spacing = int(hair_width // 7) if hair_width >= 70 else 10
        start_x = center[0] - hair_width // 2

        x = start_x
        while x <= start_x + hair_width:
            y = hair_center_y + random.randint(-4, 6)
            puff_centers.append((int(x), int(y)))
            x += puff_spacing

        side_offset = int(puff_radius * 0.9)
        puff_centers.append((center[0] - hair_width // 2 - side_offset // 2, hair_center_y + random.randint(-8, 2)))
        puff_centers.append((center[0] + hair_width // 2 + side_offset // 2, hair_center_y + random.randint(-8, 2)))
        puff_centers.append((center[0] - int(puff_spacing * 1.5), hair_center_y - int(puff_radius * 0.6)))
        puff_centers.append((center[0] + int(puff_spacing * 1.5), hair_center_y - int(puff_radius * 0.6)))
        puff_centers.append((center[0], hair_center_y - int(puff_radius * 0.9)))

    for pc in puff_centers:
        rr = int(puff_radius * (0.85 + (random.random() * 0.3)))
        pygame.draw.circle(surface, hair_color_base, pc, rr)

    for pc in puff_centers:
        hh = int(puff_radius * 0.45)
        hx = pc[0] - max(1, int(puff_radius * 0.12))
        hy = pc[1] - max(1, int(puff_radius * 0.25))
        pygame.draw.circle(surface, hair_color_highlight, (hx, hy), hh)

    face_color = WHITE if not hit else (200, 200, 200)
    pygame.draw.circle(surface, face_color, center, radius)

    eye_y = center[1] - int(radius * 0.2)
    eye_x_offset = int(radius * 0.5)
    eye_r = max(3, int(radius * 0.12))

    mouth_rect = pygame.Rect(center[0] - int(radius * 0.6), center[1] + int(radius * 0.18), int(radius * 1.2), int(radius * 0.5))
    nose_pos = (center[0], center[1] + int(radius * 0.02))

    if hit:
        pygame.draw.circle(surface, BLACK, (center[0] - eye_x_offset, eye_y), eye_r + 1)
        pygame.draw.circle(surface, BLACK, (center[0] + eye_x_offset, eye_y), eye_r + 1)
        pygame.draw.arc(surface, BLACK, mouth_rect, math.pi * 1.1, math.pi * 1.9, 2)
        pygame.draw.circle(surface, (160, 160, 160), nose_pos, max(5, int(radius * 0.14)))
    else:
        pygame.draw.circle(surface, BLACK, (center[0] - eye_x_offset, eye_y), eye_r)
        pygame.draw.circle(surface, BLACK, (center[0] + eye_x_offset, eye_y), eye_r)
        pygame.draw.arc(surface, CARNIVAL_RED, mouth_rect, math.pi, 2 * math.pi, max(2, int(radius * 0.1)))
        pygame.draw.circle(surface, CARNIVAL_RED, nose_pos, max(6, int(radius * 0.18)))

# WATER GUN SPRITE
class WaterGun(pygame.sprite.Sprite):
    # WATERGUN INIT
    def __init__(self, center_x, bottom_y):
        super().__init__()
        self.center_x_base = int(center_x)
        self.current_angle = random.uniform(0.0, 2.0 * math.pi)
        self.current_stream_x = float(center_x)
        self.current_stream_y = float(bottom_y - STREAM_LENGTH)
        self.pivot_x = int(center_x)
        self.pivot_y = int(bottom_y - 10)
        self.barrel_width = 100
        self.barrel_height = 24
        self.image = pygame.Surface([self.barrel_width, self.barrel_height], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.center_x_base, bottom_y - self.barrel_height // 2))
        try:
            pygame.draw.rect(self.image, (30, 30, 30), (0, 0, self.barrel_width, self.barrel_height), 0, border_radius=6)
            pygame.draw.rect(self.image, CARNIVAL_YELLOW, (6, 6, self.barrel_width - 12, self.barrel_height - 12), 2, border_radius=5)
        except TypeError:
            pygame.draw.rect(self.image, (30, 30, 30), (0, 0, self.barrel_width, self.barrel_height))
            pygame.draw.rect(self.image, CARNIVAL_YELLOW, (6, 6, self.barrel_width - 12, self.barrel_height - 12), 2)
        self.is_spraying = False
        self.max_stream_width = 25
        self.hit_stream_x = float(center_x)
        self.stream_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.stream_rect = self.stream_image.get_rect(topleft=(0, 0))
        self.particles = []
        self.particle_sway_speed = 4.0
        self.particle_sway_amp = 6.0

    # UPDATE POSITION
    def update_position(self, dt):
        self.current_angle += SWING_SPEED * dt
        swing_angle = math.sin(self.current_angle) * MAX_SWING_ANGLE
        self.current_stream_x = self.pivot_x + STREAM_LENGTH * math.sin(swing_angle)
        self.current_stream_y = self.pivot_y - STREAM_LENGTH * math.cos(swing_angle)

    # UPDATE STREAM AND PARTICLES
    def update_stream(self, target_y, water_level_ratio, dt):
        self.stream_image.fill((0, 0, 0, 0))
        current_time_s = pygame.time.get_ticks() / 1000.0
        if self.is_spraying:
            min_width_ratio = 0.25
            current_width_ratio = min_width_ratio + water_level_ratio * (1.0 - min_width_ratio)
            stream_width = max(2, int(self.max_stream_width * current_width_ratio))
            dy_target = (self.pivot_y - target_y)
            dy_total = (self.pivot_y - self.current_stream_y)
            if abs(dy_total) < 1e-3 or abs(dy_target) < 1e-3:
                hit_x = float(self.pivot_x)
            else:
                t = max(0.0, min(1.0, dy_target / dy_total))
                hit_x = float(self.pivot_x + t * (self.current_stream_x - self.pivot_x))
            self.hit_stream_x += (hit_x - self.hit_stream_x) * min(1.0, dt * 12.0)
            flicker_blue = min(255, max(140, OG_WATER_CYAN[2] + random.randint(-20, 20)))
            water_color = (OG_WATER_CYAN[0], OG_WATER_CYAN[1], flicker_blue, 200)
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
            for i in range(6):
                frac = random.random()
                px = int(self.pivot_x + (self.current_stream_x - self.pivot_x) * frac + random.uniform(-6, 6))
                py = int(self.pivot_y + (self.current_stream_y - self.pivot_y) * frac + random.uniform(-6, 6))
                size = random.randint(2, 5)
                life = random.uniform(0.9, 1.6)
                phase = random.random() * math.pi * 2
                sway_amp = random.uniform(2.0, self.particle_sway_amp)
                vy = random.uniform(20, 80)
                self.particles.append({'x': px, 'y': py, 'size': size, 'life': life, 'age': 0.0, 'vy': vy, 'phase': phase, 'sway_amp': sway_amp})
            MAX_PARTICLES = 300
            if len(self.particles) > MAX_PARTICLES:
                del self.particles[0:len(self.particles) - MAX_PARTICLES]
        for p in list(self.particles):
            p['age'] += dt
            if p['age'] >= p['life']:
                try:
                    self.particles.remove(p)
                except ValueError:
                    pass
                continue
            alpha = int(255 * (1.0 - (p['age'] / p['life'])))
            p['y'] += p.get('vy', 30) * dt
            sway = math.sin(current_time_s * self.particle_sway_speed + p.get('phase', 0.0)) * p.get('sway_amp', 2.0)
            p['x'] += sway * dt * 30.0
            pygame.draw.circle(self.stream_image, (OG_WATER_CYAN[0], OG_WATER_CYAN[1], OG_WATER_CYAN[2], alpha), (int(p['x']), int(p['y'])), p['size'])

    # DRAW STREAM TO SURFACE
    def draw_stream(self, surface):
        if self.is_spraying or self.particles:
            surface.blit(self.stream_image, self.stream_rect)

# CLOWN SPLASH MINI-GAME CLASS
class ClownSplashMiniGame:
    # CLOWNSPLASH INIT
    def __init__(self, screen, font, sound_manager):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager
        self.small_font = safe_font(size=18)
        self.PLAY_AREA_RECT = pygame.Rect(
            PLAY_AREA_MARGIN, PLAY_AREA_MARGIN,
            SCREEN_WIDTH - 2 * PLAY_AREA_MARGIN,
            SCREEN_HEIGHT - 2 * PLAY_AREA_MARGIN
        )
        self.PLAY_AREA_CENTER_X = self.PLAY_AREA_RECT.centerx
        self.reset()

    # RESET GAME
    def reset(self):
        self.message = "Hold SPACE to spray water! Press R to top-up. Splash for points!"
        self.WATER_MAX = 100.0
        self.water_level = self.WATER_MAX
        self.SPRAY_RATE = 10.0
        self.REFILL_TAP_AMOUNT = 8.0
        self.REFILL_TAP_COOLDOWN = 0.75
        self.last_refill_tap_time = 0.0
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
        self.last_attempt_spray_time = 0.0
        self.tank_x = self.PLAY_AREA_RECT.left + 20
        self.tank_width = 40
        self.tank_height = 200
        self.tank_y = self.PLAY_AREA_RECT.bottom - self.tank_height - 80
        self.reticle_sway_speed = 4.0
        self.reticle_sway_amp = 6.0

    # SETUP CLOWNS
    def _setup_clowns(self):
        self.clown_targets.empty()
        clown_spacing = 150
        num_clowns = 3
        start_x = self.PLAY_AREA_CENTER_X - (num_clowns - 1) * clown_spacing / 2
        for i in range(num_clowns):
            x = int(start_x + (i * clown_spacing))
            clown = Clown(x, self.clown_target_y, size=84)
            sprite = pygame.sprite.Sprite()
            sprite.image = pygame.Surface((clown.visual_size, clown.visual_size), pygame.SRCALPHA)
            draw_clown_face_centered(sprite.image, clown.clown_size, False, clown.visual_size, hair_puffs=clown.hair_puffs)
            sprite.rect = sprite.image.get_rect(center=(clown.center_x, clown.center_y))
            sprite.clown_logic = clown
            sprite.clown_logic.reset()
            sprite.marked_hit = False
            self.clown_targets.add(sprite)

    # INPUT HANDLER
    def handle_input(self, event):
        score_change = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not self.is_in_cooldown:
                    self.space_down = True
                    if self.space_held_since is None:
                        self.space_held_since = time.time()
            elif event.key == pygame.K_r:
                now = time.time()
                if now - self.last_refill_tap_time >= self.REFILL_TAP_COOLDOWN:
                    self.last_refill_tap_time = now
                    if not self.is_in_cooldown:
                        if self.water_level < self.WATER_MAX:
                            added = min(self.REFILL_TAP_AMOUNT, self.WATER_MAX - self.water_level)
                            self.water_level += added
                            self.water_level = min(self.water_level, self.WATER_MAX)
                            percent = int((self.water_level / self.WATER_MAX) * 100)
                            self.message = f"Refilled +{int(added)} water! ({percent}% full)"
                        else:
                            self.message = "Tank already full."
                    else:
                        self.message = "Cannot refill during cooldown."
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                if self.space_down:
                    self.space_down = False
                    self.space_held_since = None
                    if not self.is_in_cooldown and self.water_gun.is_spraying:
                        self.last_spray_time = time.time()
                        self.is_in_cooldown = True
                        for clown in self.clown_targets:
                            try:
                                clown.clown_logic.reset()
                            except Exception:
                                pass
                        try:
                            self.sound_manager.play_pop()
                        except Exception:
                            pass
                        self.message = "Cooldown initiated..."
        return score_change

    # UPDATE GAME
    def update(self, dt):
        score_to_report = 0
        current_time = time.time()
        self.water_gun.update_position(dt)
        should_spray_attempt = self.space_down and not self.is_in_cooldown
        is_spraying_now = False
        if should_spray_attempt:
            if self.water_level < (self.WATER_MAX * self.start_threshold_ratio):
                self.message = f"Tank needs {int(self.start_threshold_ratio * 100)}% to start spraying!"
                self.water_gun.is_spraying = False
            else:
                held = (self.space_held_since is not None) and (current_time - self.space_held_since >= self.spray_charge_time)
                if held and (current_time - self.last_attempt_spray_time > 0.06):
                    self.last_attempt_spray_time = current_time
                    if self.water_level > 0:
                        consumption = self.SPRAY_RATE * dt
                        self.water_level -= consumption
                        self.water_level = max(0.0, self.water_level)
                        is_spraying_now = True
                        try:
                            self.sound_manager.play_water_spray(start=True)
                        except Exception:
                            pass
                        percent = int((self.water_level / self.WATER_MAX) * 100)
                        self.message = f"Spraying! Water: {percent}%"
                        clowns_being_hit_this_frame = []
                        for clown in self.clown_targets:
                            try:
                                if abs(clown.rect.centerx - self.water_gun.hit_stream_x) < (clown.clown_logic.clown_size // 2 + 8):
                                    clown.clown_logic.mark_hit()
                                    clowns_being_hit_this_frame.append(clown)
                                    clown.image.fill((0, 0, 0, 0))
                                    draw_clown_face_centered(clown.image, clown.clown_logic.clown_size, True, clown.clown_logic.visual_size, hair_puffs=clown.clown_logic.hair_puffs)
                            except Exception:
                                pass
                        if clowns_being_hit_this_frame and current_time - self.last_score_time >= HIT_SCORE_INTERVAL:
                            score_to_report = SPLASH_BULLSEYE_SCORE
                            self.last_score_time = current_time
                            percent = int((self.water_level / self.WATER_MAX) * 100)
                            self.message = f"BULLSEYE! +{score_to_report} (Water: {percent}%)"
                        for clown in self.clown_targets:
                            if clown not in clowns_being_hit_this_frame:
                                clown.image.fill((0, 0, 0, 0))
                                draw_clown_face_centered(clown.image, clown.clown_logic.clown_size, False, clown.clown_logic.visual_size, hair_puffs=clown.clown_logic.hair_puffs)
                    if self.water_level <= 0.0 and is_spraying_now:
                        is_spraying_now = False
                        self.last_spray_time = current_time
                        self.is_in_cooldown = True
                        try:
                            self.sound_manager.play_water_spray(start=False)
                        except Exception:
                            pass
                        self.message = "Tank EMPTY! Cooldown..."
                        for clown in self.clown_targets:
                            try:
                                clown.clown_logic.reset()
                                clown.image.fill((0, 0, 0, 0))
                                draw_clown_face_centered(clown.image, clown.clown_logic.clown_size, False, clown.clown_logic.visual_size, hair_puffs=clown.clown_logic.hair_puffs)
                            except Exception:
                                pass
        time_since_spray = current_time - self.last_spray_time
        if self.is_in_cooldown:
            if time_since_spray >= self.COOLDOWN_TIME:
                self.is_in_cooldown = False
                if not self.space_down and self.water_level >= self.WATER_MAX:
                    self.message = "Tank fully charged. Hold SPACE to spray water!"
                elif not self.space_down and self.water_level < self.WATER_MAX:
                    self.message = "Refill using R to add water."
            else:
                remaining_time = self.COOLDOWN_TIME - time_since_spray
                self.message = f"Cooldown: {remaining_time:.1f}s until ready."
        if not is_spraying_now and not self.is_in_cooldown:
            if self.water_level >= self.WATER_MAX:
                self.message = "Tank full. Hold SPACE to spray!"
            else:
                self.message = "Press R to refill a portion of the tank."
        if not is_spraying_now:
            try:
                self.sound_manager.play_water_spray(start=False)
            except Exception:
                pass
        self.water_gun.is_spraying = is_spraying_now
        water_ratio = self.water_level / self.WATER_MAX if self.WATER_MAX > 0 else 0.0
        water_ratio = max(0.0, min(1.0, water_ratio))
        self.water_gun.update_stream(self.clown_target_y, water_ratio, dt)
        return score_to_report

    # DRAW GAME
    def draw(self):
        self.screen.fill(SPLASH_GREEN)

        pygame.draw.rect(self.screen, BLACK, self.PLAY_AREA_RECT)
        pygame.draw.rect(self.screen, CARNIVAL_RED, (self.PLAY_AREA_RECT.left, self.clown_target_y + 30, self.PLAY_AREA_RECT.width, 10))
        pygame.draw.rect(self.screen, CARNIVAL_RED, (self.PLAY_AREA_RECT.left, self.PLAY_AREA_RECT.bottom - 70, self.PLAY_AREA_RECT.width, 70))

        tank_x, tank_y = self.tank_x, self.tank_y
        tank_width, tank_height = self.tank_width, self.tank_height
        tank_rect = pygame.Rect(tank_x - 4, tank_y - 4, tank_width + 8, tank_height + 8)

        border_color = BLACK
        if self.water_level >= self.WATER_MAX * 0.9:
            border_color = SPLASH_GREEN
        elif self.water_level <= self.WATER_MAX * 0.1:
            border_color = CARNIVAL_RED

        draw_rounded_box(self.screen, tank_rect, fill_color=WHITE, border_color=border_color, border_thickness=3, radius=8)

        fill_ratio = self.water_level / self.WATER_MAX if self.WATER_MAX > 0 else 0.0
        displayed_ratio = max(0.0, min(1.0, fill_ratio))
        fill_height = int(displayed_ratio * tank_height)

        for i in range(fill_height):
            t = i / max(1, fill_height)
            r = int(OG_WATER_CYAN[0] * (0.6 + 0.4 * t))
            g = int(OG_WATER_CYAN[1] * (0.6 + 0.4 * t))
            b = int(OG_WATER_CYAN[2] * (0.6 + 0.4 * t))
            pygame.draw.line(self.screen, (r, g, b), (tank_x, tank_y + tank_height - i), (tank_x + tank_width - 1, tank_y + tank_height - i))

        threshold_y = tank_y + tank_height - int(self.start_threshold_ratio * tank_height)
        pygame.draw.line(self.screen, CARNIVAL_YELLOW, (tank_x - 6, threshold_y), (tank_x + tank_width + 6, threshold_y), 2)

        label = self.small_font.render("WATER", True, BLACK)
        self.screen.blit(label, (tank_x + tank_width // 2 - label.get_width() // 2, tank_y - 26))

        display_message = self.message.replace('**', '')
        max_w = SCREEN_WIDTH - 40
        lines = wrap_text(self.font, display_message, max_w)
        y = SCREEN_HEIGHT - 30 - (len(lines) - 1) * (self.font.get_linesize() // 1)

        for line in lines:
            msg_text = self.font.render(line, True, UI_PLAYFUL)
            self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, y))
            y += msg_text.get_height() + 2

        self.water_gun.draw_stream(self.screen)
        self.clown_targets.draw(self.screen)
        self.screen.blit(self.water_gun.image, self.water_gun.rect)

        reticle_color = UI_PLAYFUL if not ACCESSIBILITY_OPTIONS["reticle_alt"] else (255, 220, 180)

        try:
            dot_x = float(self.water_gun.hit_stream_x)
            t = pygame.time.get_ticks() / 1000.0
            sway = math.sin(t * self.reticle_sway_speed) * self.reticle_sway_amp

            dot_x = int(dot_x + sway)
            dot_y = int(self.clown_target_y) - 8

            dot_x = max(self.PLAY_AREA_RECT.left + 8, min(self.PLAY_AREA_RECT.right - 8, dot_x))
            dot_y = max(self.PLAY_AREA_RECT.top + 8, min(self.PLAY_AREA_RECT.bottom - 8, dot_y))

            pygame.draw.circle(self.screen, reticle_color, (dot_x, dot_y), 6)
        except Exception:
            pass

    # CLEANUP
    def cleanup(self):
        self.clown_targets.empty()
        try:
            self.sound_manager.play_water_spray(start=False)
        except Exception:
            pass

# CUP SPRITE CLASS
class Cup(pygame.sprite.Sprite):
    # CUP INIT
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

    # DRAW CUP
    def _draw_cup(self):
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

    # SET TARGET
    def set_target(self, target_x, target_y):
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        self.start_time = time.time()
        self.is_moving = True
        self.duration = SHUFFLE_DURATION_MS / 1000.0

    # UPDATE CUP
    def update(self):
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

    # REVEAL
    def reveal(self, should_reveal=True):
        self.is_revealed = bool(should_reveal)
        self._draw_cup()

# SHELL GAME MINI-GAME
class ShellGameMiniGame:
    # SHELLGAME INIT
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

    # RESET SHELLGAME
    def reset(self):
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
        self._cups_sound_playing = False

    # SETUP CUPS
    def _setup_cups(self):
        ball_index = random.randint(0, 2)
        self.cups = []
        for i, x_pos in enumerate(self.cup_x_positions):
            cup = Cup(x_pos, self.cup_y, size=160, has_ball=(i == ball_index))
            self.cups.append(cup)
        self.all_sprites = pygame.sprite.Group(self.cups)
        for cup in self.cups:
            cup.reveal(False)
            cup.is_moving = False

    # INITIAL REVEAL SEQUENCE
    def _initial_reveal_sequence(self):
        self.state = "START_REVEAL"
        for cup in self.cups:
            cup.reveal(cup.has_ball)
        self.message = "Watch the ball!"
        pygame.time.set_timer(SHUFFLE_EVENT, INITIAL_REVEAL_DURATION_MS)

    # START SHUFFLING
    def _start_shuffling(self):
        for cup in self.cups:
            cup.reveal(False)
        self.state = "SHUFFLING"
        self.current_shuffle = 0
        self.shuffle_pairs = self._generate_shuffle_pairs()
        self.message = f"Shuffling {self.shuffle_count} times... Keep your eyes on the ball!"
        try:
            self.sound_manager.start_cups()
            self._cups_sound_playing = True
        except Exception:
            self._cups_sound_playing = False
        pygame.time.set_timer(SHUFFLE_EVENT, SHUFFLE_DURATION_MS + 100)

    # GENERATE PAIRS
    def _generate_shuffle_pairs(self):
        pairs = []
        for _ in range(self.shuffle_count):
            indices = random.sample(range(3), 2)
            pairs.append(tuple(indices))
        return pairs

    # DO ONE SHUFFLE
    def _do_one_shuffle(self):
        if any(cup.is_moving for cup in self.cups):
            return
        if self.current_shuffle >= len(self.shuffle_pairs):
            pygame.time.set_timer(SHUFFLE_EVENT, 0)
            self.state = "WAITING_CHOICE"
            self.message = "Where is the ball? Click on a cup!"
            try:
                if self._cups_sound_playing:
                    self.sound_manager.stop_cups()
                    self._cups_sound_playing = False
            except Exception:
                pass
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

    # CHECK CHOICE
    def _check_choice(self, pos):
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
                score_to_report = SHELLGAME_WIN_SCORE
                self.message = f"CONGRATS! You found the ball! +{score_to_report} Points! (Game resets soon)"
                try:
                    self.sound_manager.play_fanfare()
                except Exception:
                    pass
            else:
                score_to_report = 0
                self.message = "Too bad! The ball was not there. (Game resets soon)"
            pygame.time.set_timer(SHUFFLE_EVENT, INITIAL_REVEAL_DURATION_MS)
        return score_to_report

    # INPUT HANDLER
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

    # UPDATE
    def update(self, dt):
        self.all_sprites.update()
        any_moving = any(cup.is_moving for cup in self.cups)
        if any_moving and not self._cups_sound_playing:
            try:
                self.sound_manager.start_cups()
                self._cups_sound_playing = True
            except Exception:
                self._cups_sound_playing = False
        if not any_moving and self._cups_sound_playing:
            try:
                self.sound_manager.stop_cups()
            except Exception:
                pass
            self._cups_sound_playing = False
        return 0

    # DRAW
    def draw(self):
        self.screen.fill(BLACK)
        table_rect = pygame.Rect(self.PLAY_AREA_RECT.left, self.PLAY_AREA_RECT.top + 100, self.PLAY_AREA_RECT.width, self.PLAY_AREA_RECT.height - 100)
        pygame.draw.rect(self.screen, OG_BROWN, table_rect)
        msg_text = self.font.render(self.message, True, UI_PLAYFUL)
        self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, 80))
        self.all_sprites.draw(self.screen)

    # CLEANUP
    def cleanup(self):
        pygame.time.set_timer(SHUFFLE_EVENT, 0)
        self.all_sprites.empty()
        try:
            if self._cups_sound_playing:
                self.sound_manager.stop_cups()
                self._cups_sound_playing = False
        except Exception:
            pass

# WHACK TARGET SPRITE
class WhackTarget(pygame.sprite.Sprite):
    # WHACKTARGET INIT
    def __init__(self, x, y, size=92):
        super().__init__()
        self.size = int(size)
        self.surface_size = self.size + 36
        self.image = pygame.Surface((self.surface_size, self.surface_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.visible = False
        self.pop_time = 0.0
        self.lifetime = 1.2
        self.clown = Clown(self.rect.centerx, self.rect.centery, size=self.size - 10)
        self._redraw()

    # REDRAW
    def _redraw(self):
        self.image.fill((0, 0, 0, 0))
        hole_h = int(self.size * 0.4)
        hole_rect = pygame.Rect(0, self.surface_size - hole_h, self.surface_size, hole_h)
        pygame.draw.ellipse(self.image, (40, 40, 40), hole_rect)
        if self.visible:
            clown_surf = pygame.Surface((self.clown.visual_size, self.clown.visual_size), pygame.SRCALPHA)
            draw_clown_face_centered(clown_surf, self.clown.clown_size, False, self.clown.visual_size, hair_puffs=self.clown.hair_puffs)
            pos = (self.surface_size // 2 - clown_surf.get_width() // 2, self.surface_size // 2 - clown_surf.get_height() // 2 - 6)
            self.image.blit(clown_surf, pos)

    # POP
    def pop(self, lifetime=1.2):
        self.visible = True
        self.pop_time = time.time()
        self.lifetime = lifetime
        self._redraw()

    # HIDE
    def hide(self):
        self.visible = False
        self._redraw()

    # WHACK
    def whack(self):
        if self.visible:
            self.hide()
            return WHACK_HIT_SCORE
        return 0

    # UPDATE
    def update(self, dt):
        if self.visible and time.time() - self.pop_time >= self.lifetime:
            self.hide()

# WHACK-A-MOLE GAME
class WhackAMoleGame:
    # WHACKAMOLE INIT
    def __init__(self, screen, font, sound_manager):
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager
        self.small_font = safe_font(size=16)
        self.PLAY_AREA_RECT = pygame.Rect(
            PLAY_AREA_MARGIN, PLAY_AREA_MARGIN,
            SCREEN_WIDTH - 2 * PLAY_AREA_MARGIN,
            SCREEN_HEIGHT - 2 * PLAY_AREA_MARGIN
        )
        self.reset()

    # RESET
    def reset(self):
        self.message = "Whack the clown! Only one appears at a time."
        self.rows = 4
        self.cols = 3
        self.hole_spacing_x = (self.PLAY_AREA_RECT.width) // (self.cols + 1)
        self.hole_spacing_y = (self.PLAY_AREA_RECT.height) // (self.rows + 1)
        self.targets = []
        for r in range(2):
            for c in range(self.cols):
                x = self.PLAY_AREA_RECT.left + (c + 1) * self.hole_spacing_x
                y = self.PLAY_AREA_RECT.top + (r + 1) * self.hole_spacing_y + 20
                t = WhackTarget(x, y, size=92)
                self.targets.append(t)
        self.active_target: Optional[WhackTarget] = None
        self.next_spawn_time = time.time() + random.uniform(1.2, 2.2)
        self.spawn_delay_range = (1.2, 2.2)
        self.active_lifetime_range = (1.0, 1.6)
        self.hits = 0
        self.misses = 0
        self.time_started = time.time()
        self.duration = 30.0
        self.round_over = False
        self.round_end_time = None

    # INPUT HANDLER
    def handle_input(self, event):
        score_change = 0
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.active_target and self.active_target.visible and self.active_target.rect.collidepoint(pos):
                gained = self.active_target.whack()
                score_change += gained
                if gained > 0:
                    try:
                        self.sound_manager.play_pop()
                    except Exception:
                        pass
                self.hits += 1
                self.message = f"Clown Whacked! +{WHACK_HIT_SCORE}"
                self.next_spawn_time = time.time() + random.uniform(*self.spawn_delay_range)
                self.active_target = None
            else:
                self.misses += 1
        return score_change

    # UPDATE
    def update(self, dt):
        if self.round_over:
            if time.time() >= self.round_end_time:
                self.reset()
            return 0
        if self.active_target:
            self.active_target.update(dt)
            if not self.active_target.visible:
                self.active_target = None
                self.next_spawn_time = time.time() + random.uniform(*self.spawn_delay_range)
        else:
            if time.time() >= self.next_spawn_time:
                candidates = [t for t in self.targets if not t.visible]
                if candidates:
                    t = random.choice(candidates)
                    t.pop(lifetime=random.uniform(*self.active_lifetime_range))
                    self.active_target = t
        for t in self.targets:
            t.update(dt)
        if time.time() - self.time_started >= self.duration:
            self.round_over = True
            self.round_end_time = time.time() + 3.0
            self.message = f"Round over! Hits: {self.hits} | Misses: {self.misses}"
        return 0

    # DRAW
    def draw(self):
        self.screen.fill(MENU_DARK_BLUE)

        pygame.draw.rect(self.screen, BLACK, self.PLAY_AREA_RECT)

        title = self.font.render("WHACK-A-CLOWN", True, UI_PLAYFUL)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))

        for t in self.targets:
            self.screen.blit(t.image, t.rect.topleft)

        time_left = max(0, int(self.duration - (time.time() - self.time_started))) if not self.round_over else 0
        hud = self.small_font.render(f"Time: {time_left}s   Hits: {self.hits}   Misses: {self.misses}", True, UI_PLAYFUL)
        self.screen.blit(hud, (10, 10))

        lines = wrap_text(self.font, self.message, SCREEN_WIDTH - 60)
        y = SCREEN_HEIGHT - 60 - (len(lines) - 1) * (self.font.get_linesize() // 1)
        
        for line in lines:
            t_surf = self.font.render(line, True, UI_PLAYFUL)
            self.screen.blit(t_surf, (SCREEN_WIDTH // 2 - t_surf.get_width() // 2, y))
            y += t_surf.get_height() + 2

    # CLEANUP
    def cleanup(self):
        for t in self.targets:
            t.hide()

# ARCADE MANAGER CLASS
class ArcadeManager:
    # MANAGER INIT
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.title_font = safe_font(size=52)
        self.header_font = safe_font(size=34)
        self.button_font = safe_font(size=22)
        self.ui_font = safe_font(size=20)
        self.small_font = safe_font(size=16)
        self.sound_manager = SoundManager()
        self.total_score = 0
        self.current_game_score = 0
        self.game_high_scores = {
            STATE_DARTPOP: 0,
            STATE_HOOPSHOT: 0,
            STATE_SPLASH: 0,
            STATE_SHELLGAME: 0,
            STATE_WHACK: 0,
        }
        self._load_scores()
        self.prize_unlocked = {}
        self._load_prizes()
        self.game_unlocked = {}
        self._load_unlocks()
        self.state = STATE_MENU
        self.button_rects = {}
        self.stats_button_rect = pygame.Rect(0, 0, 0, 0)
        self.settings_button_rect = pygame.Rect(0, 0, 0, 0)
        self.prize_button_rect = pygame.Rect(0, 0, 0, 0)
        self.games = {
            STATE_DARTPOP: DartPopGame(self.screen, self.ui_font, self.sound_manager),
            STATE_HOOPSHOT: HoopShotGame(self.screen, self.ui_font, self.sound_manager),
            STATE_SPLASH: ClownSplashMiniGame(self.screen, self.ui_font, self.sound_manager),
            STATE_SHELLGAME: ShellGameMiniGame(self.screen, self.ui_font, self.sound_manager),
            STATE_PRIZES: PrizeScreen(self.screen, self.header_font, self.sound_manager, manager=self),
            STATE_WHACK: WhackAMoleGame(self.screen, self.ui_font, self.sound_manager),
        }
        self.game_names = {
            STATE_DARTPOP: "Dart Pop",
            STATE_HOOPSHOT: "Hoop Shot",
            STATE_SPLASH: "Clown Splash",
            STATE_SHELLGAME: "Shell Game",
            STATE_PRIZES: "Prize Room",
            STATE_WHACK: "Whack-A-Clown",
        }
        self.show_fps = False
        self.settings = {
            "slow_game": ACCESSIBILITY_OPTIONS["slow_game"],
            "monochrome": ACCESSIBILITY_OPTIONS["monochrome"],
            "mute_audio": ACCESSIBILITY_OPTIONS["mute"],
            "reticle_alt": ACCESSIBILITY_OPTIONS["reticle_alt"],
            "fps_in_settings": False,
            "timer_enabled": True,
            "timer_seconds": 60,
        }
        self.time_scale_target = 0.75 if self.settings["slow_game"] else 1.0
        self.time_scale_current = self.time_scale_target
        self.time_scale_lerp_speed = 4.0
        self.modal_active = False
        self.modal_type = None
        self.modal_message = ""
        self.modal_buttons = {}
        self.modal_target = None
        self.settings_toggle_rects = []
        self._menu_last_hovered = None
        try:
            self.sound_manager.set_mute(self.settings["mute_audio"])
        except Exception:
            pass
        ACCESSIBILITY_OPTIONS["reticle_alt"] = self.settings["reticle_alt"]
        self.timer_active = False
        self.timer_remaining = 0.0
        self.timed_games_played = 0
        self.timed_game_records = []
        try:
            self.sound_manager.play_background_music()
        except Exception:
            pass

        self._button_hovered = {}
        self._selection_sound = None
        try:
            sel_candidates = [
                resource_path(os.path.join("Sounds", "Selection.mp3")),
                resource_path(os.path.join("Sounds", "selection.mp3")),
                os.path.join("Sounds", "Selection.mp3"),
                os.path.join("Sounds", "selection.mp3"),
            ]
            sel_path = None
            for cand in sel_candidates:
                try:
                    if cand and os.path.isfile(cand):
                        sel_path = cand
                        break
                except Exception:
                    pass
            if sel_path and _HAVE_PYGAME:
                try:
                    self._selection_sound = pygame.mixer.Sound(sel_path)
                except Exception:
                    self._selection_sound = None
            else:
                self._selection_sound = None
        except Exception:
            self._selection_sound = None

    # LOAD SCORES
    def _load_scores(self):
        try:
            with open(SCORES_FILE, 'r') as f:
                data = json.load(f)
                for k in self.game_high_scores.keys():
                    self.game_high_scores[k] = data.get(str(k), 0)
        except Exception:
            pass

    # SAVE SCORES
    def _save_scores(self):
        try:
            data = {str(k): v for k, v in self.game_high_scores.items()}
            atomic_write_json(SCORES_FILE, data)
        except Exception:
            pass

    # LOAD PRIZES
    def _load_prizes(self):
        try:
            with open(PRIZE_STATE_FILE, 'r') as f:
                data = json.load(f)
                self.prize_unlocked = {k: bool(v) for k, v in data.items()}
                for p in PRIZES:
                    self.prize_unlocked.setdefault(p['id'], False)
        except Exception:
            self.prize_unlocked = {p['id']: False for p in PRIZES}

    # SAVE PRIZES
    def _save_prizes(self):
        try:
            atomic_write_json(PRIZE_STATE_FILE, self.prize_unlocked)
        except Exception:
            pass

    # LOAD UNLOCKS
    def _load_unlocks(self):
        try:
            with open(UNLOCK_STATE_FILE, 'r') as f:
                data = json.load(f)
                self.game_unlocked = {k: bool(v) for k, v in data.items()}
                self.game_unlocked.setdefault(str(STATE_WHACK), False)
                self.game_unlocked.setdefault(str(STATE_SHELLGAME), False)
        except Exception:
            self.game_unlocked = {str(STATE_WHACK): False, str(STATE_SHELLGAME): False}

    # SAVE UNLOCKS
    def _save_unlocks(self):
        try:
            atomic_write_json(UNLOCK_STATE_FILE, self.game_unlocked)
        except Exception:
            pass

    # APPLY SETTINGS
    def _apply_settings(self):
        self.time_scale_target = 0.75 if self.settings["slow_game"] else 1.0
        try:
            self.sound_manager.set_mute(self.settings["mute_audio"])
        except Exception:
            pass
        ACCESSIBILITY_OPTIONS["monochrome"] = self.settings["monochrome"]
        ACCESSIBILITY_OPTIONS["reticle_alt"] = self.settings["reticle_alt"]
        self.show_fps = bool(self.settings.get("fps_in_settings", False))

    # HANDLE INPUT
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.modal_active:
                        self.modal_active = False
                        self.modal_type = None
                        self.modal_message = ""
                        self.modal_buttons = {}
                        self.modal_target = None
                        continue
                    if self.state != STATE_MENU and self.state != STATE_STATS and self.state != STATE_SETTINGS:
                        game_state = self.state
                        if game_state in self.game_high_scores and self.current_game_score > self.game_high_scores[game_state]:
                            self.game_high_scores[game_state] = self.current_game_score
                        self.current_game_score = 0
                        current_game = self.games.get(self.state)
                        if current_game:
                            try:
                                current_game.cleanup()
                                if hasattr(current_game, 'reset'):
                                    current_game.reset()
                            except Exception:
                                pass
                        self.timer_active = False
                        self.timer_remaining = 0.0
                        self.state = STATE_MENU
                    elif self.state == STATE_MENU:
                        self.running = False
                    elif self.state == STATE_STATS:
                        self.state = STATE_MENU
                    elif self.state == STATE_SETTINGS:
                        self._apply_settings()
                        self.state = STATE_MENU
                if self.state == STATE_STATS and event.key == pygame.K_SPACE:
                    self.state = STATE_MENU
            if self.modal_active:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mp = event.pos
                    for name, rect in self.modal_buttons.items():
                        if rect.collidepoint(mp):
                            if self.modal_type == 'unlock_game':
                                if name == 'purchase':
                                    self._attempt_unlock_game(self.modal_target)
                                elif name == 'cancel':
                                    self.modal_active = False
                                    self.modal_type = None
                            elif self.modal_type == 'info':
                                self.modal_active = False
                                self.modal_type = None
                            break
                continue
            if self.state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.prize_button_rect.collidepoint(event.pos):
                        self.state = STATE_PRIZES
                        prize_screen = self.games.get(STATE_PRIZES)
                        if prize_screen:
                            try:
                                prize_screen.reset()
                                prize_screen.unlocked = self.prize_unlocked
                            except Exception:
                                pass
                        continue
                    if self.settings_button_rect.collidepoint(event.pos):
                        self.state = STATE_SETTINGS
                        continue
                    if self.stats_button_rect.collidepoint(event.pos):
                        self.state = STATE_STATS
                        continue
                    for game_state, rect in self.button_rects.items():
                        if rect.collidepoint(event.pos):
                            if game_state == STATE_WHACK and not self._is_game_unlocked(STATE_WHACK):
                                self._open_unlock_modal(game_state)
                                break
                            if game_state == STATE_SHELLGAME and not self._is_game_unlocked(STATE_SHELLGAME):
                                self._open_unlock_modal(game_state)
                                break
                            self.state = game_state
                            if game_state != STATE_PRIZES:
                                g = self.games.get(self.state)
                                if g and hasattr(g, 'reset'):
                                    g.reset()
                                self.current_game_score = 0
                                if self.settings.get("timer_enabled", False):
                                    self.timer_active = True
                                    self.timer_remaining = float(self.settings.get("timer_seconds", 60))
                                else:
                                    self.timer_active = False
                                    self.timer_remaining = 0.0
                            break
            elif self.state == STATE_SETTINGS:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mpos = event.pos
                    if hasattr(self, 'settings_toggle_rects'):
                        toggles = self.settings_toggle_rects
                        if toggles and len(toggles) >= 6:
                            if toggles[0].collidepoint(mpos):
                                self.settings["slow_game"] = not self.settings["slow_game"]
                                self._apply_settings()
                            elif toggles[1].collidepoint(mpos):
                                self.settings["monochrome"] = not self.settings["monochrome"]
                                self._apply_settings()
                            elif toggles[2].collidepoint(mpos):
                                self.settings["mute_audio"] = not self.settings["mute_audio"]
                                self._apply_settings()
                            elif toggles[3].collidepoint(mpos):
                                self.settings["reticle_alt"] = not self.settings["reticle_alt"]
                                self._apply_settings()
                            elif toggles[4].collidepoint(mpos):
                                self.settings["fps_in_settings"] = not self.settings["fps_in_settings"]
                                self._apply_settings()
                            elif toggles[5].collidepoint(mpos):
                                self.settings["timer_enabled"] = not self.settings["timer_enabled"]
                                self._apply_settings()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.settings["slow_game"] = not self.settings["slow_game"]
                        self._apply_settings()
                    elif event.key == pygame.K_2:
                        self.settings["monochrome"] = not self.settings["monochrome"]
                        self._apply_settings()
                    elif event.key == pygame.K_3:
                        self.settings["mute_audio"] = not self.settings["mute_audio"]
                        self._apply_settings()
                    elif event.key == pygame.K_4:
                        self.settings["reticle_alt"] = not self.settings["reticle_alt"]
                        self._apply_settings()
                    elif event.key == pygame.K_5:
                        self.settings["fps_in_settings"] = not self.settings["fps_in_settings"]
                        self._apply_settings()
                    elif event.key == pygame.K_6:
                        self.settings["timer_enabled"] = not self.settings["timer_enabled"]
                        self._apply_settings()
            elif self.state == STATE_PRIZES:
                prize_screen = self.games.get(STATE_PRIZES)
                if prize_screen:
                    prize_screen.handle_input(event)
            elif self.state in self.games:
                score_change = self.games[self.state].handle_input(event)
                if score_change > 0:
                    self.total_score += score_change
                    self.current_game_score += score_change

    # CHECK UNLOCK
    def _is_game_unlocked(self, state_id: int) -> bool:
        return bool(self.game_unlocked.get(str(state_id), False))

    # OPEN UNLOCK MODAL
    def _open_unlock_modal(self, state_id: int):
        self.modal_active = True
        self.modal_type = 'unlock_game'
        self.modal_target = state_id
        game_name = self.game_names.get(state_id, "Unknown")
        cost = WHACK_GAME_UNLOCK_SCORE if state_id == STATE_WHACK else SHELL_GAME_UNLOCK_SCORE
        self.modal_message = f"Unlock {game_name} permanently for {cost} points? This will deduct points from your total."
        purchase_rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 28, 120, 25)
        cancel_rect = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 28, 120, 25)
        self.modal_buttons = {'purchase': purchase_rect, 'cancel': cancel_rect}

    # ATTEMPT UNLOCK
    def _attempt_unlock_game(self, state_id: int):
        cost = WHACK_GAME_UNLOCK_SCORE if state_id == STATE_WHACK else SHELL_GAME_UNLOCK_SCORE
        if self.total_score >= cost:
            self.total_score -= cost
            self.game_unlocked[str(state_id)] = True
            self._save_unlocks()
            self.modal_message = f"{self.game_names.get(state_id)} unlocked! Enjoy the game."
            self.modal_buttons = {'cancel': pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 28, 120, 36)}
            try:
                self.sound_manager.play_buy()
            except Exception:
                pass
            try:
                self.sound_manager.play_fanfare()
            except Exception:
                pass
        else:
            self.modal_message = "Insufficient points to unlock this game."
            self.modal_buttons = {'cancel': pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 28, 120, 36)}

    # UPDATE STATE
    def _update_state(self, dt):
        t = max(0.0, min(1.0, dt * self.time_scale_lerp_speed))
        self.time_scale_current += (self.time_scale_target - self.time_scale_current) * t
        scaled_dt = dt * self.time_scale_current
        if self.state in self.games and self.state != STATE_PRIZES:
            if self.timer_active and self.settings.get("timer_enabled", False):
                self.timer_remaining -= scaled_dt
                if self.timer_remaining <= 0.0:
                    final_score = self.current_game_score
                    try:
                        if self.state in self.game_high_scores and final_score > self.game_high_scores[self.state]:
                            self.game_high_scores[self.state] = final_score
                    except Exception:
                        pass
                    record = {'game': self.state, 'score': int(final_score), 'timestamp': time.time()}
                    self.timed_game_records.append(record)
                    self.timed_games_played += 1
                    current_game = self.games.get(self.state)
                    if current_game:
                        try:
                            current_game.cleanup()
                            if hasattr(current_game, 'reset'):
                                current_game.reset()
                        except Exception:
                            pass
                    self.current_game_score = 0
                    self.timer_active = False
                    self.timer_remaining = 0.0
                    self.state = STATE_STATS
                    return
            score_change = self.games[self.state].update(scaled_dt)
            if score_change > 0:
                self.total_score += score_change
                self.current_game_score += score_change
        if self.state == STATE_PRIZES:
            prize_game = self.games.get(STATE_PRIZES)
            if prize_game:
                prize_game.unlocked = self.prize_unlocked
                prize_game.update(scaled_dt)

    # DRAW MAIN MENU
    def _draw_menu(self):
        self.screen.fill(MENU_DARK_BLUE)
        stripe_width = 40
        for i in range(0, SCREEN_WIDTH + stripe_width, stripe_width):
            color = CARNIVAL_RED if (i // stripe_width) % 2 == 0 else WHITE
            pygame.draw.rect(self.screen, color, (i, 0, stripe_width, SCREEN_HEIGHT))
        overlay_width = 480
        overlay_height = 560
        overlay_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - overlay_width // 2,
            70,
            overlay_width,
            overlay_height
        )
        draw_rounded_box(self.screen, overlay_rect, fill_color=(25, 35, 50), border_color=CARNIVAL_YELLOW, border_thickness=5, radius=26)
        title_surf = self.title_font.render("JAY'S CARNIVAL ARCADE", True, CARNIVAL_YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 58))
        self.screen.blit(title_surf, title_rect)
        square_size = 46
        left_margin = 10
        stats_top = SCREEN_HEIGHT - PLAY_AREA_MARGIN - square_size - 10
        stats_button_rect = pygame.Rect(left_margin, stats_top, square_size, square_size)
        draw_rounded_box(self.screen, stats_button_rect, fill_color=(25, 35, 50), border_color=CARNIVAL_YELLOW, border_thickness=3, radius=12)
        bar_w = 8
        gap = 6
        bar_left = stats_button_rect.left + 6
        base_y = stats_button_rect.top + square_size - 12
        pygame.draw.rect(self.screen, UI_PLAYFUL, (bar_left, base_y - 6, bar_w, 6))
        pygame.draw.rect(self.screen, UI_PLAYFUL, (bar_left + (bar_w + gap), base_y - 14, bar_w, 14))
        pygame.draw.rect(self.screen, UI_PLAYFUL, (bar_left + 2 * (bar_w + gap), base_y - 22, bar_w, 22))
        self.stats_button_rect = stats_button_rect
        settings_top = stats_top - square_size - 10
        settings_button_rect = pygame.Rect(left_margin, settings_top, square_size, square_size)
        draw_rounded_box(self.screen, settings_button_rect, fill_color=(25, 35, 50), border_color=CARNIVAL_YELLOW, border_thickness=3, radius=12)
        gear_center = (settings_button_rect.left + square_size // 2, settings_button_rect.top + square_size // 2)
        pygame.draw.circle(self.screen, UI_PLAYFUL, gear_center, 10)
        tooth_w = 4
        tooth_h = 10
        pygame.draw.rect(self.screen, UI_PLAYFUL, (gear_center[0] - tooth_w // 2, gear_center[1] - 20, tooth_w, tooth_h))
        pygame.draw.rect(self.screen, UI_PLAYFUL, (gear_center[0] - tooth_w // 2, gear_center[1] + 10, tooth_w, tooth_h))
        pygame.draw.rect(self.screen, UI_PLAYFUL, (gear_center[0] - 20, gear_center[1] - tooth_w // 2, tooth_h, tooth_w))
        pygame.draw.rect(self.screen, UI_PLAYFUL, (gear_center[0] + 10, gear_center[1] - tooth_w // 2, tooth_h, tooth_w))
        self.settings_button_rect = settings_button_rect
        prize_top = settings_top - square_size - 10
        prize_button_rect = pygame.Rect(left_margin, prize_top, square_size, square_size)
        draw_rounded_box(self.screen, prize_button_rect, fill_color=(25, 35, 50), border_color=CARNIVAL_YELLOW, border_thickness=3, radius=12)
        gift_center_x = prize_button_rect.left + square_size // 2
        gift_center_y = prize_button_rect.top + square_size // 2
        box_w = 28
        box_h = 18
        pygame.draw.rect(self.screen, UI_PLAYFUL, (gift_center_x - box_w // 2, gift_center_y - 2, box_w, box_h))
        pygame.draw.rect(self.screen, CARNIVAL_YELLOW, (gift_center_x - 3, gift_center_y - 6, 6, box_h + 2))
        pygame.draw.rect(self.screen, CARNIVAL_YELLOW, (gift_center_x - box_w // 2, gift_center_y - 1, box_w, 4))
        self.prize_button_rect = prize_button_rect
        y_start = overlay_rect.top + 40
        button_height = 48
        button_width = overlay_width - 60
        button_left = overlay_rect.left + 30
        self.button_rects = {}
        mouse_pos = pygame.mouse.get_pos()
        ordered = [STATE_DARTPOP, STATE_HOOPSHOT, STATE_SPLASH, STATE_WHACK, STATE_SHELLGAME]

        # helper to play selection sound once per hover entry
        def _maybe_play_selection_for_key(key):
            try:
                if self._button_hovered.get(key, False):
                    return
                self._button_hovered[key] = True
                if self.sound_manager and hasattr(self.sound_manager, 'play_selection'):
                    try:
                        self.sound_manager.play_selection()
                        return
                    except Exception:
                        pass
                if self._selection_sound:
                    try:
                        self._selection_sound.play()
                    except Exception:
                        pass
            except Exception:
                pass

        # small side buttons hover handling: stats, settings, prize
        # reset hover if not over them
        side_keys = [('stats', self.stats_button_rect), ('settings', self.settings_button_rect), ('prize', self.prize_button_rect)]
        for skey, srect in side_keys:
            try:
                h = srect.collidepoint(mouse_pos)
                prev = self._button_hovered.get(skey, False)
                if h and not prev:
                    _maybe_play_selection_for_key(skey)
                elif not h and prev:
                    self._button_hovered[skey] = False
            except Exception:
                pass

        for i, state_id in enumerate(ordered):
            rect = pygame.Rect(button_left, y_start + i * (button_height + BUTTON_SPACING), button_width, button_height)
            is_locked = False
            lock_text = ""
            if state_id == STATE_WHACK and not self._is_game_unlocked(STATE_WHACK):
                is_locked = True
                lock_text = f" (Unlock {WHACK_GAME_UNLOCK_SCORE})"
            if state_id == STATE_SHELLGAME and not self._is_game_unlocked(STATE_SHELLGAME):
                is_locked = True
                lock_text = f" (Unlock {SHELL_GAME_UNLOCK_SCORE})"
            button_text = self.game_names.get(state_id, "Unknown") + lock_text
            hover = rect.collidepoint(mouse_pos)
            key = f"game_{state_id}"
            prev_hover = self._button_hovered.get(key, False)
            if hover and not prev_hover:
                _maybe_play_selection_for_key(key)
            elif not hover and prev_hover:
                self._button_hovered[key] = False
            color = CARNIVAL_RED
            if state_id == STATE_HOOPSHOT:
                color = HOOP_BLUE
            elif state_id == STATE_SPLASH:
                color = SPLASH_GREEN
            elif state_id == STATE_WHACK:
                color = OG_ORANGE
            elif state_id == STATE_SHELLGAME:
                color = CARNIVAL_YELLOW
            text_color = BLACK if state_id in (STATE_DARTPOP, STATE_SPLASH, STATE_SHELLGAME, STATE_PRIZES, STATE_WHACK) else WHITE
            draw_button(self.screen, button_text, rect, color, text_color, self.button_font, locked=is_locked, hover=hover)
            self.button_rects[state_id] = rect
        inst_surf = self.small_font.render("Press ESC to exit Arcade", True, UI_PLAYFUL)
        self.screen.blit(inst_surf, (SCREEN_WIDTH // 2 - inst_surf.get_width() // 2, SCREEN_HEIGHT - 30))

    # DRAW SETTINGS
    def _draw_settings_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        panel_w = 520
        panel_h = 380
        panel_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - panel_w // 2,
            SCREEN_HEIGHT // 2 - panel_h // 2,
            panel_w, panel_h
        )
        draw_rounded_box(self.screen, panel_rect, fill_color=MENU_DARK_BLUE, border_color=CARNIVAL_YELLOW, border_thickness=5, radius=16)
        title_surf = self.header_font.render("SETTINGS", True, UI_PLAYFUL)
        self.screen.blit(title_surf, title_surf.get_rect(center=(panel_rect.left + panel_w // 2, panel_rect.top + 30)))
        row_top = panel_rect.top + 50
        row_height = 36
        left_text_x = panel_rect.left + 24
        toggle_box_size = 22
        toggle_right_x = panel_rect.right - 28 - toggle_box_size
        toggle_rects = []
        r1_rect = pygame.Rect(panel_rect.left + 12, row_top, panel_rect.width - 24, row_height)
        draw_rounded_box(self.screen, r1_rect, fill_color=(30, 30, 40), border_color=None, border_thickness=0, radius=10)
        label1 = self.ui_font.render("Velocity Attenuation (-25%)", True, UI_PLAYFUL)
        self.screen.blit(label1, (left_text_x, row_top + (row_height - label1.get_height()) // 2))
        toggle1_rect = pygame.Rect(toggle_right_x, row_top + (row_height - toggle_box_size) // 2, toggle_box_size, toggle_box_size)
        draw_rounded_box(self.screen, toggle1_rect, fill_color=(60, 60, 60), border_color=CARNIVAL_YELLOW, border_thickness=2, radius=8)
        if self.settings["slow_game"]:
            pygame.draw.circle(self.screen, UI_PLAYFUL, toggle1_rect.center, toggle_box_size // 3)
        toggle_rects.append(toggle1_rect)
        row_top += row_height + 10
        r2_rect = pygame.Rect(panel_rect.left + 12, row_top, panel_rect.width - 24, row_height)
        draw_rounded_box(self.screen, r2_rect, fill_color=(30, 30, 40), border_color=None, border_thickness=0, radius=10)
        label2 = self.ui_font.render("Chromatic Simplification", True, UI_PLAYFUL)
        self.screen.blit(label2, (left_text_x, row_top + (row_height - label2.get_height()) // 2))
        toggle2_rect = pygame.Rect(toggle_right_x, row_top + (row_height - toggle_box_size) // 2, toggle_box_size, toggle_box_size)
        draw_rounded_box(self.screen, toggle2_rect, fill_color=(60, 60, 60), border_color=CARNIVAL_YELLOW, border_thickness=2, radius=8)
        if self.settings["monochrome"]:
            pygame.draw.circle(self.screen, UI_PLAYFUL, toggle2_rect.center, toggle_box_size // 3)
        toggle_rects.append(toggle2_rect)
        row_top += row_height + 10
        r3_rect = pygame.Rect(panel_rect.left + 12, row_top, panel_rect.width - 24, row_height)
        draw_rounded_box(self.screen, r3_rect, fill_color=(30, 30, 40), border_color=None, border_thickness=0, radius=10)
        label3 = self.ui_font.render("Acoustic Output Control", True, UI_PLAYFUL)
        self.screen.blit(label3, (left_text_x, row_top + (row_height - label3.get_height()) // 2))
        toggle3_rect = pygame.Rect(toggle_right_x, row_top + (row_height - toggle_box_size) // 2, toggle_box_size, toggle_box_size)
        draw_rounded_box(self.screen, toggle3_rect, fill_color=(60, 60, 60), border_color=CARNIVAL_YELLOW, border_thickness=2, radius=8)
        if self.settings["mute_audio"]:
            pygame.draw.circle(self.screen, UI_PLAYFUL, toggle3_rect.center, toggle_box_size // 3)
        toggle_rects.append(toggle3_rect)
        row_top += row_height + 10
        r4_rect = pygame.Rect(panel_rect.left + 12, row_top, panel_rect.width - 24, row_height)
        draw_rounded_box(self.screen, r4_rect, fill_color=(30, 30, 40), border_color=None, border_thickness=0, radius=10)
        label4 = self.ui_font.render("Reticle Variant", True, UI_PLAYFUL)
        self.screen.blit(label4, (left_text_x, row_top + (row_height - label4.get_height()) // 2))
        toggle4_rect = pygame.Rect(toggle_right_x, row_top + (row_height - toggle_box_size) // 2, toggle_box_size, toggle_box_size)
        draw_rounded_box(self.screen, toggle4_rect, fill_color=(60, 60, 60), border_color=CARNIVAL_YELLOW, border_thickness=2, radius=8)
        if self.settings["reticle_alt"]:
            pygame.draw.circle(self.screen, UI_PLAYFUL, toggle4_rect.center, toggle_box_size // 3)
        toggle_rects.append(toggle4_rect)
        row_top += row_height + 10
        r5_rect = pygame.Rect(panel_rect.left + 12, row_top, panel_rect.width - 24, row_height)
        draw_rounded_box(self.screen, r5_rect, fill_color=(30, 30, 40), border_color=None, border_thickness=0, radius=10)
        label5 = self.ui_font.render("Performance Metrics", True, UI_PLAYFUL)
        self.screen.blit(label5, (left_text_x, row_top + (row_height - label5.get_height()) // 2))
        toggle5_rect = pygame.Rect(toggle_right_x, row_top + (row_height - toggle_box_size) // 2, toggle_box_size, toggle_box_size)
        draw_rounded_box(self.screen, toggle5_rect, fill_color=(60, 60, 60), border_color=CARNIVAL_YELLOW, border_thickness=2, radius=8)
        if self.settings["fps_in_settings"]:
            pygame.draw.circle(self.screen, UI_PLAYFUL, toggle5_rect.center, toggle_box_size // 3)
        toggle_rects.append(toggle5_rect)
        row_top += row_height + 10
        r6_rect = pygame.Rect(panel_rect.left + 12, row_top, panel_rect.width - 24, row_height)
        draw_rounded_box(self.screen, r6_rect, fill_color=(30, 30, 40), border_color=None, border_thickness=0, radius=10)
        label6 = self.ui_font.render(f"Temporal Constraints ({int(self.settings.get('timer_seconds', 60))}s)", True, UI_PLAYFUL)
        self.screen.blit(label6, (left_text_x, row_top + (row_height - label6.get_height()) // 2))
        toggle6_rect = pygame.Rect(toggle_right_x, row_top + (row_height - toggle_box_size) // 2, toggle_box_size, toggle_box_size)
        draw_rounded_box(self.screen, toggle6_rect, fill_color=(60, 60, 60), border_color=CARNIVAL_YELLOW, border_thickness=2, radius=8)
        if self.settings["timer_enabled"]:
            pygame.draw.circle(self.screen, UI_PLAYFUL, toggle6_rect.center, toggle_box_size // 3)
        toggle_rects.append(toggle6_rect)
        self.settings_toggle_rects = toggle_rects
        hint_surf = self.small_font.render("Click toggles or press 1/2/3/4/5/6 to toggle. ESC to return.", True, UI_PLAYFUL)
        self.screen.blit(hint_surf, (panel_rect.left + panel_w // 2 - hint_surf.get_width() // 2, panel_rect.bottom - 25))

    # DRAW STATS
    def _draw_stats_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        panel_w, panel_h = 520, 420
        panel_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - panel_w // 2,
            SCREEN_HEIGHT // 2 - panel_h // 2,
            panel_w, panel_h
        )
        draw_rounded_box(self.screen, panel_rect, fill_color=MENU_DARK_BLUE, border_color=CARNIVAL_YELLOW, border_thickness=5, radius=20)
        panel_center_x = panel_rect.left + panel_w // 2
        title_surf = self.header_font.render("ARCADE STATS", True, UI_PLAYFUL)
        self.screen.blit(title_surf, title_surf.get_rect(center=(panel_center_x, panel_rect.top + 30)))
        total_surf = self.button_font.render(f"GRAND TOTAL: {self.total_score} Points", True, WHITE)
        self.screen.blit(total_surf, total_surf.get_rect(center=(panel_center_x, panel_rect.top + 80)))
        header_surf = self.ui_font.render("--- HIGHEST SCORE PER GAME (All Sessions) ---", True, CARNIVAL_RED)
        self.screen.blit(header_surf, header_surf.get_rect(center=(panel_center_x, panel_rect.top + 130)))
        y_pos = panel_rect.top + 160
        game_states = [STATE_DARTPOP, STATE_HOOPSHOT, STATE_SPLASH, STATE_SHELLGAME, STATE_WHACK]
        for game_state in game_states:
            game_name = self.game_names.get(game_state, "Unknown Game")
            high_score = self.game_high_scores.get(game_state, 0)
            rank_text = f"{game_name}: {high_score} Points"
            color = SPLASH_GREEN if high_score > 0 else WHITE
            score_surf = self.button_font.render(rank_text, True, color)
            self.screen.blit(score_surf, score_surf.get_rect(center=(panel_center_x, y_pos)))
            y_pos += 40
        y_pos += 2
        timed_header = self.ui_font.render(f"Timed Games Played: {self.timed_games_played}", True, UI_PLAYFUL)
        self.screen.blit(timed_header, (panel_center_x - timed_header.get_width() // 2, y_pos))
        y_pos += 18
        if self.timed_game_records:
            last = self.timed_game_records[-1]
            last_game = self.game_names.get(last.get('game', ''), "Unknown")
            last_score = last.get('score', 0)
            last_line = self.small_font.render(f"Last Timed: {last_game} | Score: {last_score}", True, WHITE)
            self.screen.blit(last_line, (panel_center_x - last_line.get_width() // 2, y_pos))
            y_pos += 30
        exit_surf = self.ui_font.render("Press SPACE to return to Menu", True, UI_PLAYFUL)
        self.screen.blit(exit_surf, exit_surf.get_rect(center=(panel_center_x, panel_rect.bottom - 20)))

    # DRAW GAME SCORE HUD
    def _draw_game_score(self):
        session_text = f"SESSION: {self.current_game_score}"
        session_surf = self.ui_font.render(session_text, True, UI_PLAYFUL)
        self.screen.blit(session_surf, (SCREEN_WIDTH - session_surf.get_width() - 10, 10))
        total_text = f"TOTAL: {self.total_score} | ESC to Menu"
        total_surf = self.ui_font.render(total_text, True, UI_PLAYFUL)
        self.screen.blit(total_surf, (SCREEN_WIDTH - total_surf.get_width() - 10, 30))
        if self.timer_active:
            try:
                time_left = max(0, int(self.timer_remaining))
                timer_surf = self.ui_font.render(f"Timer: {time_left}s", True, UI_PLAYFUL)
                self.screen.blit(timer_surf, (SCREEN_WIDTH - timer_surf.get_width() - 10, 50))
            except Exception:
                pass

    # MONOCHROME FILTER
    def _apply_monochrome_filter(self):
        surf = self.screen
        try:
            import numpy as np
            arr = pygame.surfarray.array3d(surf)
            gray = (0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]).astype(np.uint8)
            gray3 = np.empty_like(arr)
            gray3[..., 0] = gray
            gray3[..., 1] = gray
            gray3[..., 2] = gray
            gray_surf = pygame.surfarray.make_surface(gray3)
            surf.blit(gray_surf, (0, 0))
        except Exception:
            w, h = surf.get_size()
            gray_surf = pygame.Surface((w, h))
            surf.lock()
            gray_surf.lock()
            for y in range(h):
                for x in range(w):
                    try:
                        r, g, b, a = surf.get_at((x, y))
                    except Exception:
                        r, g, b = surf.get_at((x, y))[:3]
                        a = 255
                    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                    gray_surf.set_at((x, y), (gray, gray, gray))
            surf.unlock()
            gray_surf.unlock()
            surf.blit(gray_surf, (0, 0))

    # MAIN RUN LOOP
    def run(self):
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
            elif self.state == STATE_SETTINGS:
                self._draw_menu()
                self._draw_settings_screen()
            elif self.state in self.games:
                game = self.games[self.state]
                if self.state == STATE_PRIZES:
                    try:
                        game.unlocked = self.prize_unlocked
                        game.draw(self.total_score)
                    except Exception:
                        game.draw(self.total_score)
                else:
                    game.draw()
                if self.state != STATE_PRIZES:
                    self._draw_game_score()
            if self.modal_active:
                panel_w = 540
                panel_h = 150
                panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - panel_w // 2, SCREEN_HEIGHT // 2 - panel_h // 2, panel_w, panel_h)
                draw_rounded_box(self.screen, panel_rect, fill_color=MENU_DARK_BLUE, border_color=CARNIVAL_YELLOW, border_thickness=4, radius=12)
                title = self.header_font.render("UNLOCK GAME", True, UI_PLAYFUL) if self.modal_type == 'unlock_game' else self.header_font.render("NOTICE", True, UI_PLAYFUL)
                self.screen.blit(title, (panel_rect.left + 20, panel_rect.top + 12))
                msg_lines = wrap_text(self.small_font, self.modal_message, panel_w - 40)
                y = panel_rect.top + 44
                for line in msg_lines:
                    surf = self.small_font.render(line, True, WHITE)
                    self.screen.blit(surf, (panel_rect.left + 20, y))
                    y += surf.get_height() + 6
                for name, rect in self.modal_buttons.items():
                    is_primary = (name in ('purchase', 'purchase', 'ok'))
                    color = SPLASH_GREEN if is_primary else (60, 60, 60)
                    draw_button(self.screen, name.upper(), rect, color, BLACK, self.small_font, locked=False, hover=False)
            if self.show_fps:
                fps_surf = self.small_font.render(f"FPS: {int(self.clock.get_fps())}", True, UI_PLAYFUL)
                self.screen.blit(fps_surf, (10, SCREEN_HEIGHT - 30))
            if self.settings["monochrome"]:
                try:
                    self._apply_monochrome_filter()
                except Exception:
                    pass
            pygame.display.flip()
            self.clock.tick(FPS)
        self._save_scores()
        self._save_prizes()
        self._save_unlocks()

# PROGRAM ENTRYPOINT
if __name__ == '__main__':
    manager = ArcadeManager()
    manager.run()
    pygame.quit()
    sys.exit()

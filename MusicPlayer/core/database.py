### database.py

# Core database module for the Music Player

import os, json, sys

# Path helpers
def get_project_root():
    if getattr(sys, 'frozen', False):
        # If program is an executable
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# Path definitions
PROJECT_ROOT = os.path.dirname(get_project_root()) if get_project_root().endswith('core') else get_project_root()
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")
SETTINGS_FILE = os.path.join(DATABASE_DIR, "settings.json")

os.makedirs(DATABASE_DIR, exist_ok=True)


# Load and save settings
def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ settings.json was hurmled — creating a new one.")
    return {}


def save_settings(data: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# Theme management
def get_theme() -> str:
    settings = load_settings()
    return settings.get("theme", "green")


def set_theme(theme_name: str):
    settings = load_settings()
    settings["theme"] = theme_name
    save_settings(settings)


# Download path management
def get_download_path_setting() -> str | None:
    settings = load_settings()
    return settings.get("download_path")


def set_download_path_setting(path: str):
    settings = load_settings()
    settings["download_path"] = path
    save_settings(settings)


# Language management
def get_language() -> str:
    settings = load_settings()
    return settings.get("language", "en")


def set_language(lang: str):
    settings = load_settings()
    settings["language"] = lang
    save_settings(settings)

# Custom background image
def get_custom_background() -> str | None:
    settings = load_settings()
    return settings.get("custom_background")


def set_custom_background(path: str):
    settings = load_settings()
    settings["custom_background"] = path
    save_settings(settings)

# Animation settings
def get_animation_settings() -> dict:
    settings = load_settings()
    return settings.get("animation_settings", {
        "screen": True,
        "cover": True,
        "pulse": True
    })

def set_animation_settings(animation_settings: dict):
    settings = load_settings()
    settings["animation_settings"] = animation_settings
    save_settings(settings)

# Cover style settings
def get_cover_settings() -> dict:
    settings = load_settings()
    return settings.get("cover_settings", {
        "style": "circle"
    })

def set_cover_settings(cover_settings: dict):
    settings = load_settings()
    settings["cover_settings"] = cover_settings
    save_settings(settings)

# Equalizer settings
def get_equalizer_settings() -> dict:
    settings = load_settings()
    return settings.get("equalizer", {
        "60": 0,
        "150": 0,
        "400": 0,
        "1000": 0,
        "2400": 0,
        "15000": 0
    })

def set_equalizer_settings(eq_settings: dict):
    settings = load_settings()
    settings["equalizer"] = eq_settings
    save_settings(settings)

# Shortcut settings
def get_shortcuts() -> dict:
    settings = load_settings()
    return settings.get("shortcuts", {
        "play_pause": ["ctrl", "space"],
        "next": ["ctrl", "right"],
        "prev": ["ctrl", "left"]
    })

def set_shortcuts(shortcuts: dict):
    settings = load_settings()
    settings["shortcuts"] = shortcuts
    save_settings(settings)

# Lite mode settings
def get_lite_mode() -> bool:
    settings = load_settings()
    return settings.get("lite_mode", False)

def set_lite_mode(state: bool):
    settings = load_settings()
    settings["lite_mode"] = state
    save_settings(settings)

# Tray mode settings
def get_tray_mode() -> bool:
    settings = load_settings()
    return settings.get("tray_mode", False)

def set_tray_mode(state: bool):
    settings = load_settings()
    settings["tray_mode"] = state
    save_settings(settings)

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


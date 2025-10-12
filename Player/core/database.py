import os
import json
import sys

# === Визначаємо кореневу папку проекту ===
def get_project_root():
    if getattr(sys, 'frozen', False):
        # Якщо програма запущена як .exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# === Шлях до папки "database" у корені ===
PROJECT_ROOT = os.path.dirname(get_project_root()) if get_project_root().endswith('core') else get_project_root()
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")
SETTINGS_FILE = os.path.join(DATABASE_DIR, "settings.json")

# === Створюємо папку, якщо немає ===
os.makedirs(DATABASE_DIR, exist_ok=True)


# === Основні функції ===
def load_settings() -> dict:
    """Зчитує налаштування з settings.json."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ settings.json пошкоджено — створюю новий.")
    return {}


def save_settings(data: dict):
    """Зберігає словник у settings.json."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# === Тема (приклад змінної, що зберігається) ===
def get_theme() -> str:
    settings = load_settings()
    return settings.get("theme", "green")


def set_theme(theme_name: str):
    settings = load_settings()
    settings["theme"] = theme_name
    save_settings(settings)

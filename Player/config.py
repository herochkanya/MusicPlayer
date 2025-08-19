import os
import sys

def get_music_base_dir():
    if sys.platform.startswith('win'):
        # Windows
        music_dir = os.path.join(os.environ.get('USERPROFILE', ''), 'Music')
    elif sys.platform.startswith('linux'):
        # Linux
        music_dir = os.path.join(os.environ.get('HOME', ''), 'Music')
    elif sys.platform.startswith('darwin'):
        # macOS
        music_dir = os.path.join(os.environ.get('HOME', ''), 'Music')
    else:
        # Фолбек - поточна папка проекту
        music_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music')

    player_music_dir = os.path.join(music_dir, 'PlayerMusic')
    os.makedirs(player_music_dir, exist_ok=True)
    return player_music_dir

def get_download_path(subfolder='downloads'):
    base_dir = get_music_base_dir()
    path = os.path.join(base_dir, subfolder)
    os.makedirs(path, exist_ok=True)
    return path

### config.py

# Configuration file for the Music Player application

import os, sys

# Function to get the base music directory based on the OS
def get_music_base_dir():
    # Windows
    if sys.platform.startswith('win'):
        music_dir = os.path.join(os.environ.get('USERPROFILE', ''), 'Music')
    # Linux
    elif sys.platform.startswith('linux'):
        music_dir = os.path.join(os.environ.get('HOME', ''), 'Music')
    # macOS
    elif sys.platform.startswith('darwin'):
        music_dir = os.path.join(os.environ.get('HOME', ''), 'Music')
    # Fallback to current directory if OS is unknown
    else:
        music_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music')

    # Ensure the directory exists
    player_music_dir = os.path.join(music_dir, 'PlayerMusic')
    os.makedirs(player_music_dir, exist_ok=True)
    return player_music_dir

# Function to get the download path for music files
# Default subfolder is 'downloads'
def get_download_path(subfolder='downloads'):
    base_dir = get_music_base_dir()
    path = os.path.join(base_dir, subfolder)
    os.makedirs(path, exist_ok=True)
    return path

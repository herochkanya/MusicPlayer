import os, re

def sanitize_filename(name: str) -> str:
    """Очищення імені файлу від заборонених символів"""
    return re.sub(r'[\/:*?"<>|\\]', '_', name)

def find_ffmpeg_path() -> str | None:
    """Пошук FFmpeg у папці /bin або системному PATH"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Виходимо на рівень вище core/ і шукаємо в bin/
    ffmpeg_dir = os.path.normpath(os.path.join(base_dir, '..', 'bin'))
    ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
    
    if os.path.exists(ffmpeg_exe):
        return ffmpeg_dir
    return None

def get_resource_type(info: dict) -> str:
    """Визначає, що саме ми качаємо: трек, альбом чи плейлист"""
    ie_key = info.get("ie_key", "")
    has_entries = 'entries' in info
    if 'YoutubeMusic' in ie_key or 'Soundcloud' in ie_key:
        if 'Playlist' in ie_key or 'Set' in ie_key or 'Album' in ie_key:
            return 'playlist'
        return 'track' if not has_entries else 'playlist'
    return 'playlist' if has_entries else 'track'
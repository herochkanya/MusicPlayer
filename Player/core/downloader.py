from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TIT2, TPE1, TALB
import requests
import os
import re

from config import get_download_path


def sanitize_filename(name: str) -> str:
    """Replace problematic characters in filenames."""
    return re.sub(r'[\/:*?"<>|\\]', '_', name)


def get_resource_type(info: dict) -> str:
    """Determines the type of media resource."""
    ie_key = info.get("ie_key", "")
    has_entries = 'entries' in info

    if ie_key == 'YoutubeMusicAlbum':
        return 'album'
    elif ie_key == 'YoutubeMusicPlaylist':
        return 'playlist'
    elif ie_key == 'YoutubeMusic':
        return 'track' if not has_entries else 'playlist'
    elif ie_key == 'Soundcloud':
        return 'track' if not has_entries else 'playlist'
    elif ie_key == 'SoundcloudPlaylist':
        return 'playlist'
    elif ie_key == 'SoundcloudSet':
        return 'album'
    elif has_entries:
        return 'playlist'
    else:
        return 'track'


def find_ffmpeg_path() -> str | None:
    """
    Returns the path to ffmpeg/ffprobe if found in local /bin folder.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(base_dir, '..', 'bin')
    ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
    ffprobe_exe = os.path.join(ffmpeg_dir, 'ffprobe.exe')

    if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
        return ffmpeg_dir
    else:
        print("⚠️ FFmpeg not found in /bin — will try system PATH.")
        return None


def download_audio(url: str, target_folder: str = None) -> dict | list | None:
    """
    Downloads audio from YouTube/SoundCloud into a given folder.
    Automatically uses local ffmpeg binaries if present.
    """
    download_dir = get_download_path(target_folder if target_folder else 'downloads')
    os.makedirs(download_dir, exist_ok=True)

    ffmpeg_location = find_ffmpeg_path()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': ['-ar', '44100'],
        'prefer_ffmpeg': True,
    }

    if ffmpeg_location:
        ydl_opts['ffmpeg_location'] = ffmpeg_location

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

    if not info:
        print("❌ No information returned from yt-dlp.")
        return None

    def process_track(track_info):
        thumbnail_url = track_info.get('thumbnail')
        img_data = None
        if thumbnail_url:
            try:
                img_data = requests.get(thumbnail_url, timeout=10).content
            except Exception:
                img_data = None

        title = track_info.get('title', 'Unknown Title')
        artist = track_info.get('uploader', 'Unknown Artist')
        album = track_info.get('album', 'Unknown Album')

        safe_title = sanitize_filename(title)
        safe_artist = sanitize_filename(artist)

        filename = ydl.prepare_filename(track_info).rsplit('.', 1)[0] + '.mp3'
        safe_filename = os.path.join(download_dir, f"{safe_artist} - {safe_title}.mp3")

        if os.path.exists(filename) and not os.path.exists(safe_filename):
            os.rename(filename, safe_filename)
        else:
            safe_filename = filename

        audio = MP3(safe_filename, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass

        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        audio.tags.add(TALB(encoding=3, text=album))
        if img_data:
            audio.tags.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=img_data
            ))
        audio.save()

        return {
            'title': title,
            'artist': artist,
            'album': album,
            'thumbnail_url': thumbnail_url,
            'path': safe_filename,
            'source_url': track_info.get('webpage_url', '')
        }

    resource_type = get_resource_type(info)

    if resource_type in ('playlist', 'album'):
        results = []
        for entry in info.get('entries', []):
            if entry:
                result = process_track(entry)
                if result:
                    results.append(result)
        return results
    else:
        return process_track(info)

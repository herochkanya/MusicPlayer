### downloader.py

# Module for downloading audio using yt-dlp and tagging with mutagen

from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TIT2, TPE1, TALB
import requests, os, re

from config import get_download_path

# Helper to sanitize filenames
def sanitize_filename(name: str) -> str:
    return re.sub(r'[\/:*?"<>|\\]', '_', name)

# Determine resource type from yt-dlp info
def get_resource_type(info: dict) -> str:
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

# Find ffmpeg path (You need to have ffmpeg.exe and ffprobe.exe in /bin)
def find_ffmpeg_path() -> str | None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(base_dir, '..', 'bin')
    ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
    ffprobe_exe = os.path.join(ffmpeg_dir, 'ffprobe.exe')

    if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
        return ffmpeg_dir
    else:
        print("⚠️ FFmpeg not found in /bin — will try system PATH.")
        return None

# Main download function
def download_audio(url: str, target_folder: str = None, cookies_path: str = None) -> dict | list | None:
    download_dir = get_download_path(target_folder if target_folder else 'downloads')
    os.makedirs(download_dir, exist_ok=True)

    ffmpeg_location = find_ffmpeg_path()

    # Options for yt-dlp
    ydl_opts = {
        # Format priority
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        
        # General options
        'quiet': True,
        'no_warnings': True,
        'verbose': False,
        'noplaylist': False,
        
        # Reliability options
        'retries': 10,
        'continuedl': True,
        'fragment_retries': 10,
        
        # Speed and timeout
        'ratelimit': 1024*1024,
        'socket_timeout': 30,
        
        # Post-processing
        'prefer_ffmpeg': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': ['-ar', '44100'],

        # Geo and proxy
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        
        'proxy': None,
        
        'forceurl': False,
        
        # Cookies (for Youtube Music)
        'cookiefile': cookies_path if cookies_path and os.path.exists(cookies_path) else None,
    }

    if ffmpeg_location:
        ydl_opts['ffmpeg_location'] = ffmpeg_location

    if cookies_path and os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path

    # Downloading
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

    if not info:
        print("❌ No information returned from yt-dlp.")
        return None

    # Tagging function
    def process_track(track_info):
        # Download thumbnail
        thumbnail_url = track_info.get('thumbnail')
        img_data = None
        if thumbnail_url:
            try:
                img_data = requests.get(thumbnail_url, timeout=10).content
            except Exception:
                img_data = None

        # Prepare filename and tags
        title = track_info.get('title', 'Unknown Title')
        artist = track_info.get('uploader', 'Unknown Artist')
        album = track_info.get('album', 'Unknown Album')

        # Sanitize
        safe_title = sanitize_filename(title)
        safe_artist = sanitize_filename(artist)

        filename = ydl.prepare_filename(track_info).rsplit('.', 1)[0] + '.mp3'
        safe_filename = os.path.join(download_dir, f"{safe_artist} - {safe_title}.mp3")

        # Rename if necessary
        if os.path.exists(filename) and not os.path.exists(safe_filename):
            os.rename(filename, safe_filename)
        else:
            safe_filename = filename

        audio = MP3(safe_filename, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass

        # Add ID3 tags
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

    # Process based on resource type
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

from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TIT2, TPE1, TALB
import requests
import os
import re

from config import get_download_path

# Replace problematic characters in filenames
def sanitize_filename(name: str) -> str:
    return re.sub(r'[\/:*?"<>|\\]', '_', name)

# Determine the resource type: single track, playlist, or album
def get_resource_type(info: dict) -> str:
    """
    Determines the type of media resource: 'track', 'playlist', 'album', or 'unknown'.
    """
    ie_key = info.get("ie_key", "")
    has_entries = 'entries' in info

    # YouTube Music-specific identifiers
    if ie_key == 'YoutubeMusicAlbum':
        return 'album'
    elif ie_key == 'YoutubeMusicPlaylist':
        return 'playlist'
    elif ie_key == 'YoutubeMusic':
        return 'track' if not has_entries else 'playlist'

    # SoundCloud-specific identifiers
    elif ie_key == 'Soundcloud':
        return 'track' if not has_entries else 'playlist'
    elif ie_key == 'SoundcloudPlaylist':
        return 'playlist'
    elif ie_key == 'SoundcloudSet':
        return 'album'

    # Fallbacks
    elif has_entries:
        return 'playlist'
    else:
        return 'track'

# Function to download audio from YouTube or SoundCloud
def download_audio(url: str, target_folder: str = None) -> dict | list | None:
    """
    Downloads audio from YouTube or SoundCloud using the provided URL into the specified folder.
    If no folder is specified, it defaults to 'music/downloads'.

    Returns a dictionary with track metadata for a single track,
    or a list of such dictionaries for playlists or albums.
    If the download fails, returns None.
    """
    download_dir = get_download_path(target_folder if target_folder else 'downloads')
    os.makedirs(download_dir, exist_ok=True)

    # Options for yt-dlp
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

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

    if not info:
        print("❌ No information returned from yt-dlp.")
        return None

    # Helper function to process individual track metadata
    def process_track(track_info):
        # Download thumbnail if available
        thumbnail_url = track_info.get('thumbnail')
        img_data = None
        if thumbnail_url:
            try:
                img_data = requests.get(thumbnail_url).content
            except Exception:
                img_data = None

        # Retrieve basic metadata
        title = track_info.get('title', 'Unknown Title')
        artist = track_info.get('uploader', 'Unknown Artist')
        album = track_info.get('album', 'Unknown Album')

        # Sanitize metadata for filename safety
        safe_title = sanitize_filename(title)
        safe_artist = sanitize_filename(artist)

        # Prepare file paths and rename accordingly
        filename = ydl.prepare_filename(track_info).rsplit('.', 1)[0] + '.mp3'
        safe_filename = os.path.join(download_dir, f"{safe_artist} - {safe_title}.mp3")

        if os.path.exists(filename) and not os.path.exists(safe_filename):
            os.rename(filename, safe_filename)
        else:
            safe_filename = filename

        # Apply ID3 tags to the MP3 file
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

    # Determine type of content: track, playlist, or album
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

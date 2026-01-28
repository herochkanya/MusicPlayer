### downloader.py

# Module for downloading audio using yt-dlp and tagging with mutagen

import os, requests
from yt_dlp import YoutubeDL
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from config import get_download_path
from .utils import sanitize_filename, find_ffmpeg_path, get_resource_type

requests.packages.urllib3.disable_warnings()

def tag_file(filepath, title, artist):
    try:
        audio = EasyID3(filepath)
    except:
        audio = EasyID3()
        audio.save(filepath)
        audio = EasyID3(filepath)
    
    audio['title'] = title
    audio['artist'] = artist
    audio.save()
    print(f"🏷️ Tagged: {artist} - {title}")

def resolve_spotify_to_youtube(url):
    try:
        api_url = f"https://api.song.link/v1-alpha.1/links?url={url}"
        resp = requests.get(api_url, timeout=10, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            eid = data.get('entityUniqueId')
            entity = data.get('entitiesByUniqueId', {}).get(eid, {})
            
            return {
                'query': f"{entity.get('artistName')} - {entity.get('title')}",
                'is_album': entity.get('type') == 'album',
                'artist': entity.get('artistName'),
                'title': entity.get('title')
            }
    except Exception as e:
        print(f"⚠️ Metadata error: {e}")
    return None

def find_youtube_id(query):
    try:
        print(f"🔍 Searching YouTube for: {query}")
        ydl_opts = {
            'quiet': True, 
            'no_warnings': True, 
            'format': 'bestaudio/best',
            'noprogress': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                v_id = info['entries'][0]['id']
                print(f"🎥 YouTube ID: {v_id}")
                return v_id
    except Exception as e:
        print(f"❌ YouTube search error: {e}")
    return None

def download_audio(url: str, target_folder: str = None, cookies_path: str = None, progress_cb=None) -> dict | list | None:
    download_dir = get_download_path(target_folder if target_folder else 'downloads')
    os.makedirs(download_dir, exist_ok=True)

    info_spot = None

    if "spotify.com" in url:
        print("🛰️ Spotify link detected. Analyzing...")
        info_spot = resolve_spotify_to_youtube(url)
        if not info_spot: return None

        if info_spot['is_album']:
            print(f"💿 Album detected: {info_spot['query']}. Searching for individual tracks...")
            search_query = f"ytsearch10:{info_spot['query']} album"
            url = search_query 
        else:
            video_id = find_youtube_id(f"ytsearch1:{info_spot['query']}")
            if video_id:
                url = f"https://www.youtube.com/watch?v={video_id}"
            else:
                return None

    if "youtube.com" in url:
        video_id = url.split("v=")[-1].split("&")[0].split("/")[-1].split("?")[0]
        print(url)
        print(video_id)

    ffmpeg_location = find_ffmpeg_path()

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'noplaylist': False,
        'prefer_ffmpeg': True,

        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },

        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },

            {'key': 'EmbedThumbnail'},
        ],

        'ignoreerrors': True,
        'writethumbnail': True,
        'ffmpeg_location': ffmpeg_location,
        'cookiefile': cookies_path if cookies_path and os.path.exists(cookies_path) else None,
        'progress_hooks': [progress_cb] if progress_cb else [],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            def process_entry(entry):
                if not entry: return None
               
                raw_title = entry.get('title', 'Unknown')
                uploader = entry.get('uploader', 'Unknown Artist')

                yt_artist = entry.get('artist') or entry.get('creator')

                final_title = raw_title
                final_artist = yt_artist if yt_artist else uploader

                if info_spot and not entry.get('entries'):
                    final_title = info_spot['title']
                    final_artist = info_spot['artist']
                elif ' - ' in raw_title:
                    parts = raw_title.split(' - ', 1)
                    final_artist = parts[0].strip()
                    final_title = parts[1].strip()

                temp_filename = ydl.prepare_filename(entry)
                original_file = temp_filename.rsplit('.', 1)[0] + '.mp3'
                clean_artist = sanitize_filename(final_artist)
                clean_title = sanitize_filename(final_title)
                safe_name = f"{clean_artist} - {clean_title}.mp3"
                final_path = os.path.join(download_dir, safe_name)

                if os.path.exists(original_file):
                    tag_file(original_file, final_title, final_artist)
                    if os.path.exists(final_path): os.remove(final_path)
                    os.rename(original_file, final_path)

                return {
                    'title': final_title,
                    'artist': final_artist,
                    'path': final_path,
                    'thumbnail_url': entry.get('thumbnail'),
                    'source_url': entry.get('webpage_url', '')
                }
            
            if 'entries' in info:
                results = []
                for entry in info['entries']:
                    res = process_entry(entry)
                    if res: results.append(res)
                return results

            res_type = get_resource_type(info)

            if res_type == 'playlist':
                return [process_entry(e) for e in info.get('entries', []) if e]

            return process_entry(info)

    except Exception as e:
        return None

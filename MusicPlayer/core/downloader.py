### downloader.py

# Module for downloading audio using yt-dlp and tagging with mutagen

import os, requests, re
from yt_dlp import YoutubeDL
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.id3 import ID3, USLT, SYLT
from config import get_download_path
from .utils import sanitize_filename, find_ffmpeg_path, get_resource_type

requests.packages.urllib3.disable_warnings()

def is_synced(lrc_content):
    if not lrc_content:
        return False
    return bool(re.search(r'\[\d{2}:\d{2}\.\d{2,3}\]', lrc_content))

def fetch_from_netease(artist, title):
    try:
        search_url = f"https://music.cyrany.so/search?keywords={artist} {title}&limit=1"
        r = requests.get(search_url, timeout=5)
        if r.status_code == 200 and r.json()['result']['songs']:
            song_id = r.json()['result']['songs'][0]['id']
            lyric_url = f"https://music.cyrany.so/lyric?id={song_id}"
            l_resp = requests.get(lyric_url, timeout=5)
            if l_resp.status_code == 200:
                lrc = l_resp.json().get('lrc', {}).get('lyric')
                if is_synced(lrc):
                    return lrc
    except:
        pass
    return None

def fetch_lrc_smart(artist, title, album, duration, output_path):
    final_lrc = None
    is_final_synced = False

    try:
        # LRCLIB
        params = {
            'artist_name': artist, 
            'track_name': title, 
            'album_name': album or '', 
            'duration': duration
            }
        resp = requests.get("https://lrclib.net/api/get", params=params, timeout=7)
        
        if resp.status_code == 200:
            data = resp.json()
            synced = data.get('syncedLyrics')
            plain = data.get('plainLyrics')
            
            if synced:
                final_lrc = synced
                is_final_synced = True
            else:
                final_lrc = plain
        
        # NetEase
        if not is_final_synced:
            print(f"🔄 Synced lyrics not found on LRCLIB, trying NetEase...")
            netease_lrc = fetch_from_netease(artist, title)
            if netease_lrc:
                final_lrc = netease_lrc
                is_final_synced = True
                print("✅ Found synced lyrics on NetEase!")

        # Saving
        if final_lrc:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_lrc)
            status = "synced" if is_final_synced else "plain"
            print(f"✅ Lyrics saved ({status})")
            return True

    except Exception as e:
        print(f"⚠️ Lyrics fetch error: {e}")
    
    return False

def tag_file(filepath, title, artist, album=None, cover_path=None):
    try:
        try:
            audio = EasyID3(filepath)
        except:
            audio = EasyID3()
            audio.save(filepath)
            audio = EasyID3(filepath)
        
        audio['title'] = title
        audio['artist'] = artist

        if album and not album.startswith("Related tracks"):
            audio['album'] = album
        else:
            audio['album'] = ""
        
        audio.save()
        print(f"🏷️ Tagged: {artist} - {title} (Album: {album or 'N/A'})")
        if cover_path and os.path.exists(cover_path):
            tags = ID3(filepath)
            with open(cover_path, 'rb') as f:
                tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg' if cover_path.endswith(('.jpg', '.jpeg')) else 'image/png',
                    type=3,
                    desc=u'Cover',
                    data=f.read()
                ))
            tags.save(v2_version=3)
            print(f"🖼️ Cover embedded for: {title}")
    except Exception as e:
        print(f"❌ Tagging error: {e}")

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

        'nocheckcertificate': True,
        'cachedir': False,

        'writesubtitles': True,
        'subtitleslangs': ['all'],
        'writeautomaticsubs': True,

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

            {'key': 'FFmpegMetadata'},
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
                yt_album = entry.get('album')
                yt_artist = entry.get('artist') or entry.get('creator')
                duration = entry.get('duration')

                final_title = raw_title
                final_artist = yt_artist if yt_artist else uploader
                final_album = yt_album

                if info_spot and not entry.get('entries'):
                    final_title = info_spot['title']
                    final_artist = info_spot['artist']
                elif ' - ' in raw_title:
                    parts = raw_title.split(' - ', 1)
                    final_artist = parts[0].strip()
                    final_title = parts[1].strip()

                temp_filename = ydl.prepare_filename(entry)
                base_path = temp_filename.rsplit('.', 1)[0]
                original_file = base_path + '.mp3'

                cover_file = None
                for ext in ['.jpg', '.jpeg', '.webp', '.png']:
                    if os.path.exists(base_path + ext):
                        cover_file = base_path + ext
                        break
                
                clean_artist = sanitize_filename(final_artist)
                clean_title = sanitize_filename(final_title)

                safe_name = f"{clean_artist} - {clean_title}"
                file_base_name = safe_name + ".mp3"
                final_path = os.path.join(download_dir, file_base_name)
                lrc_path = os.path.join(download_dir, safe_name + ".lrc")

                if os.path.exists(original_file):
                    tag_file(original_file, final_title, final_artist, final_album, cover_path=cover_file)
                    if os.path.exists(final_path): os.remove(final_path)
                    os.rename(original_file, final_path)

                    yt_lrc = base_path + ".lrc"
                    if os.path.exists(yt_lrc):
                        os.rename(yt_lrc, lrc_path)
                    else:
                        fetch_lrc_smart(final_artist, final_title, yt_album, duration, lrc_path)
                    
                    for f in os.listdir(download_dir):
                        if f.startswith(os.path.basename(base_path)) and f.endswith(('.webp', '.jpg', '.png', '.jpeg')):
                            try: os.remove(os.path.join(download_dir, f))
                            except: pass

                return {
                    'title': final_title,
                    'artist': final_artist,
                    'album': final_album if final_album and not final_album.startswith("Related") else None,
                    'path': final_path,
                    'lyrics_path': lrc_path if os.path.exists(lrc_path) else None,
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

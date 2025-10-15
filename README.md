# 🎵 MusicPlayer

![Banner](https://github.com/user-attachments/assets/f1db33cf-2e71-4c38-8735-0ec0b21db542)

**[BETA]** — Simple but powerful music player with built-in downloader from **YouTube** and **SoundCloud**. Perfect for offline listening, playlist management, and enjoying your favorite tracks in one place.

## 🚀 Features

* 🎧 Play local music with album covers, track info, and smooth transitions.
* ⬇️ Download tracks directly from YouTube and SoundCloud.
* 🔍 Live search: quickly find tracks in your playlists.
* 🌐 Global playlist: aggregate all your music into one unified list.
* 🎶 Playback controls: play/pause, next/previous, shuffle, cycle modes.
* 💡 Visual enhancements: glowing effects for currently playing tracks, smooth album art transitions.
* 🖥️ Modern UI: glassmorphism design, responsive layouts, animated screens.

## 📸 Screenshots

### Player Screen

![MyCollages](https://github.com/user-attachments/assets/ab24fc03-ecc5-4421-a7a7-0603e836c9b8)

### Downloader Screen

<img width="1920" height="991" alt="python3 11_ohIFMNLf6b" src="https://github.com/user-attachments/assets/29c719e7-5aa0-4885-be5f-c72648105934" />

## ⚡ Installation

### Requirements

* Python 3.10+
* PyQt6 / PySide6
* yt-dlp
* ffpyplayer / VLC backend

### Install dependencies

```
pip install -r requirements.txt
```

### Install FFmpeg

* Download FFmpeg — [ffmpeg-8.0-essentials_build.zip](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip)
* Unzip the archive
* Open the 'bin' folder inside the unzipped directory
* Copy 'ffmpeg.exe' and 'ffprobe.exe'
* Paste both files into your Player/bin/ folder

### Install vlc

* Download vlc — [vlc-3.0.21-win64.exe](https://get.videolan.org/vlc/3.0.21/win64/vlc-3.0.21-win64.exe)

### Run the player

```
python main.py
```

## 🔧 Usage

1. Open Player screen to browse and play your music.
2. Switch to Downloader to download tracks from YouTube or SoundCloud.
3. Use the Global Playlist button to aggregate all your local tracks.
4. Control playback with the buttons: play/pause, next, previous, shuffle, repeat.
5. Search for tracks live using the search bar above the track list.

## 🗂 Directory Structure

```
Player/
│
├─ bin/            # resources
├─ core/           # backend logic
├─ interface/      # HTML/CSS/JS UI files
├─ config.py       # config
├─ main.py         # main entry point
├─ requirements.txt
├─ MusicPlayerWin.spec
└─ .gitignore
```

## 🌍 Roadmap

* [x] Search bar functionality
* [x] Global playlist aggregation
* [x] Updated glassmorphism UI
* [ ] Add equalizer support
* [x] Dark/Light theme toggle
* [ ] Mobile-friendly layout

## 💡 Notes

* Currently in **BETA**, expect occasional bugs.
* Works best on **Windows** with Python 3.10+.
* Feedback and contributions are welcome! 🚀

## 📫 Contact & Contribution

* GitHub Issues [MusicPlayer](https://github.com/herochkanya/MusicPlayer)
* Telegram: [N*body](https://t.me/nobody_from_nothing)

![Banner](https://github.com/user-attachments/assets/3da8af2c-b376-454b-ae0a-dc0511637476)

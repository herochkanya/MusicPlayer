### main.py

# Main application file for the Music Player
# There are @Slot and @Signal decorators for JS interaction

import sys, os, platform, subprocess

def restart_without_wayland():
    if platform.system() == "Linux" and os.environ.get("WAYLAND_DISPLAY"):
        print("Wayland detected — restarting in X11 mode...")
        new_env = os.environ.copy()
        new_env.pop("WAYLAND_DISPLAY", None)
        subprocess.run([sys.executable] + sys.argv, env=new_env)
        sys.exit(0)

if platform.system() == "Linux":
    restart_without_wayland()
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-gpu "
        "--disable-software-rasterizer "
        "--disable-features=VizDisplayCompositor"
    )

elif platform.system() == "Windows":
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = ""

from PySide6.QtCore import QObject, Signal, Slot, QUrl, QRunnable, QThreadPool
from PySide6.QtWidgets import QApplication, QFileDialog, QSystemTrayIcon, QMenu
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtGui import QIcon, QDesktopServices, QAction

from core.database import (get_theme, set_theme, 
    set_download_path_setting, get_language, set_language, 
    get_custom_background, set_custom_background,
    get_animation_settings, set_animation_settings,
    set_cover_settings, get_cover_settings,
    get_equalizer_settings, set_equalizer_settings,
    get_shortcuts, set_shortcuts,
    get_lite_mode, set_lite_mode)

def check_graphics_and_setup():
    probe_code = "from PySide6.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); sys.exit(0)"
    
    try:
        result = subprocess.run(
            [sys.executable, "-c", probe_code],
            capture_output=True,
            timeout=3
        )
        
        if result.returncode != 0:
            raise Exception("GPU initialization failed")
            
    except Exception:
        print("⚠️ Detected graphics issues — enabling Software rendering and Lite Mode.")
        
        os.environ["QT_QUICK_BACKEND"] = "software"
        os.environ["QSG_RHI_BACKEND"] = "software"
        
        set_lite_mode(True)

from core.downloader import download_audio
from core.player import MusicPlayer
from config import get_music_base_dir
from core.global_hotkeys import GlobalHotkeys

# Resource helper
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Worker for downloading
class Worker(QRunnable):
    def __init__(self, url, folder, backend):
        super().__init__()
        self.url = url
        self.folder = folder
        self.backend = backend

    def run(self):
        self.backend.log_signal.emit("⬇️ Starting download...")

        def hook(d):
            if d['status'] == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)

                percent = int(downloaded / total * 100)
                msg = f"⬇️ {percent}% — {downloaded//1_000_000}/{total//1_000_000} MB — {int(speed/1024)} KB/s — ETA {eta}s"
                self.backend.log_signal.emit(msg)

            elif d['status'] == 'finished':
                self.backend.log_signal.emit("🎵 Processing audio...")

        result = download_audio(self.url, self.folder, progress_cb=hook)

        if result is None:
            self.backend.log_signal.emit("❌ Error during download.")
        else:
            self.backend.log_signal.emit("✅ Download complete.")

# Backend class for JS interaction
class Backend(QObject):
    log_signal = Signal(str) # Log messages to JS
    track_changed = Signal(dict) # Track info to JS
    playback_state_changed = Signal(bool) # Is playing or paused
    theme_changed = Signal(str) # Theme change signal
    download_path_changed = Signal(str) # Download path change signal
    language_changed = Signal(str) # Language change signal
    lite_mode_changed = Signal(bool) # Lite mode change signal

    def __init__(self):
        super().__init__()
        self.view = None
        self.thread_pool = QThreadPool.globalInstance()
        self.player = MusicPlayer()
        self.player.set_track_change_callback(lambda track: self.track_changed.emit(track))
        self.player.set_state_callback(lambda is_playing: self.playback_state_changed.emit(is_playing))
        self.current_theme = get_theme()
        self.shortcuts = get_shortcuts()
        self.hotkeys = GlobalHotkeys(self.player, self.shortcuts)
        self.hotkeys.start()



    # Slots for JS calls:


    # === File and folder management ===
    @Slot(result='QStringList')
    # Get list of music folders
    def get_folders(self):
        try:
            base_dir = get_music_base_dir()
            return [name for name in os.listdir(base_dir)
                    if os.path.isdir(os.path.join(base_dir, name))]
        except Exception as e:
            self.log_signal.emit(f"❌ Error: {e}")
            return []

    @Slot(result='QVariantList')
    # List all music files from all folders (Global Playlist)
    def list_all_files(self):
        return self.player.list_files()

    @Slot(str, result='QVariantList')
    # List music files from a specific folder
    def list_files(self, folder):
        return self.player.list_files(folder)

    @Slot(result='QVariantList')
    # Get current playlist as list of dicts
    def get_playlist(self):
        try:
            return self.player.get_playlist_dicts()
        except Exception as e:
            self.log_signal.emit(f"❌ get_playlist error: {e}")
            return []

    @Slot(str, result='QVariantList')
    # Set playlist from a specific folder
    def set_playlist(self, folder):
        try:
            return self.player.set_playlist_from_folder(folder)
        except Exception as e:
            self.log_signal.emit(f"❌ set_playlist_from_folder error: {e}")
            return []
    
    @Slot(result='QVariantList')
    # Set playlist to all files (Global Playlist)
    def set_global_playlist(self):
        try:
            return self.player.set_global_playlist()
        except Exception as e:
            self.log_signal.emit(f"❌ set_global_playlist error: {e}")
            return []

    @Slot(list, result='QVariantList')
    # Set custom playlist from list of folder names
    def create_temp_playlist(self, playlist_names):
        return self.player.set_custom_playlist(playlist_names)


    # === Downloading ===


    @Slot(str, str)
    # Start downloading a track
    def start_download(self, url, folder):
        self.thread_pool.start(Worker(url, folder, self))


    # === Playback control ===


    @Slot(str, result='QVariantMap')
    # Play a specific track by path
    def play_track(self, path):
        try:
            if hasattr(self.player, "is_active") and self.player.is_active():
                self.player.stop()
        except Exception as e:
            self.log_signal.emit(f"❌ stop previous track error: {e}")

        track = self.player.play_track(path)
        if track:
            self.track_changed.emit(track)
        return track

    @Slot()
    # Toggle play/pause
    def toggle_pause(self):
        self.player.toggle_pause()

    @Slot()
    # Stop playback
    def stop(self):
        self.player.stop()

    @Slot(result='QVariantMap')
    # Play next track
    def next_track(self):
        try:
            track = self.player.next_track()
            if track:
                self.track_changed.emit(track)
            return track or {}
        except Exception as e:
            self.log_signal.emit(f"❌ next_track error: {e}")
            return {}

    @Slot(result='QVariantMap')
    # Play previous track
    def prev_track(self):
        try:
            track = self.player.prev_track()
            if track:
                self.track_changed.emit(track)
            return track or {}
        except Exception as e:
            self.log_signal.emit(f"❌ prev_track error: {e}")
            return {}

    @Slot(float)
    # Seek to a position in seconds
    def seek(self, seconds):
        try:
            self.player.seek(seconds)
        except Exception as e:
            self.log_signal.emit(f"❌ seek error: {e}")


    # === Check the playback state ===


    @Slot(result=bool)
    # Is a track currently active (playing or paused)
    def is_active(self):
        return getattr(self.player, "is_active", lambda: False)()

    @Slot(result='QVariantMap')
    # Get current playback info
    def get_playback_info(self):
        try:
            return self.player.get_playback_info()
        except Exception as e:
            self.log_signal.emit(f"❌ get_playback_info error: {e}")
            return {'position': 0, 'duration': 0, 'is_paused': False, 'current_index': -1}


    # === Other playback buttons ===


    @Slot(int)
    # Set cycle mode (0: no cycle, 1: cycle all, 2: cycle one)
    def set_cycle_mode(self, mode):
        self.player.set_cycle_mode(mode)

    @Slot(result=bool)
    # Toggle shuffle mode
    def toggle_shuffle(self):
        try:
            state = self.player.toggle_shuffle()
            updated = self.player.get_playlist_dicts()
            self.track_changed.emit({"playlist_updated": True, "tracks": updated})
            return state
        except Exception as e:
            self.log_signal.emit(f"❌ toggle_shuffle error: {e}")
            return False


    # === Theme management ===


    @Slot(result=str)
    # Get current theme
    def get_theme(self):
        return self.current_theme

    @Slot(str)
    # Set a new theme and save to DB (json)
    def set_theme(self, theme_name):
        try:
            self.current_theme = theme_name
            set_theme(theme_name)
            self.theme_changed.emit(theme_name)
        except Exception as e:
            self.log_signal.emit(f"❌ set_theme error: {e}")
    
    @Slot(result=str)
    # Choose custom background image
    def choose_custom_background(self):
        path, _ = QFileDialog.getOpenFileName(
            None,
            "Select background image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if not path:
            return ""
        set_custom_background(path)
        return path

    @Slot(result=str)
    # Get custom background image path
    def get_custom_background(self):
        return get_custom_background() or ""
    
    @Slot(result='QVariantMap')
    # Get animation settings
    def get_animation_settings(self):
            return get_animation_settings()

    @Slot('QVariantMap')
    # Set animation settings
    def set_animation_settings(self, settings):
            set_animation_settings(settings)
    
    @Slot(result=str)
    # Get cover style settings
    def get_cover_settings(self):
            settings = get_cover_settings() 
            return settings.get("data-cover", "circle") 
    
    @Slot(str)
    # Set cover style settings
    def set_cover_settings(self, style):
        settings = {"data-cover": style}
        set_cover_settings(settings)

    
    # === Settings management ===


    @Slot(str)
    # Open a file path in the system file explorer
    def open_path(self, path: str):
        if not os.path.exists(path):
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    @Slot()
    # Choose download path
    def choose_download_path(self):
        path = QFileDialog.getExistingDirectory(
            None,
            "Select Download Folder"
        )

        if not path:
            return

        return set_download_path_setting(path)
    
    @Slot(result=str)
    # Get download path
    def get_download_path(self):
        return get_music_base_dir()
    
    @Slot()
    # Clear and rebuild library index
    def clear_library_index(self):
        self.player.clear_library_index()
        self.player.build_library_index()
    
    @Slot(result=str)
    # Get current language
    def get_language(self):
        return get_language()

    @Slot(str)
    # Set a new language
    def set_language(self, lang):
        set_language(lang)
        self.language_changed.emit(lang)
    
    @Slot(result='QVariantMap')
    def get_equalizer_settings(self):
        state = self.player.equalizer.get_state()
        {str(k): float(v) for k, v in state.items()}
        return get_equalizer_settings()

    @Slot('QVariantMap')
    def set_equalizer_settings(self, eq_settings):
        try:
            self.player.equalizer.set_all(eq_settings)
            set_equalizer_settings(eq_settings)
        except Exception as e:
            print(f"Error saving EQ: {e}")

    @Slot(result='QVariantMap')
    # Get current shortcuts
    def get_shortcuts(self):
        return self.shortcuts

    @Slot('QVariantMap')
    # Set new shortcuts
    def set_shortcuts(self, shortcuts):
        self.shortcuts = shortcuts
        set_shortcuts(shortcuts)
        self.hotkeys.update_shortcuts(shortcuts)
    
    @Slot(result=bool)
    # Get lite mode setting
    def get_lite_mode(self):
        from core.database import get_lite_mode
        return get_lite_mode()

    @Slot(bool)
    # Set lite mode setting
    def set_lite_mode(self, state):
        from core.database import set_lite_mode
        set_lite_mode(state)
        self.lite_mode_changed.emit(state)

    # === Application control ===


    @Slot()
    # Close the application
    def close_app(self):
        if self.view:
            self.view.is_really_quitting = True
        QApplication.quit()

# Custom QWebEngineView to handle close event
class MainWebView(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.is_really_quitting = False

    def closeEvent(self, event):
        if not self.is_really_quitting:
            event.ignore()
            self.hide()
            print("🔽 Application minimized to tray.")
        else:
            event.accept()

# Start the application
def main():
    app = QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(False)

    icon_path = resource_path("bin/app.ico")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)

    view = MainWebView()
    backend = Backend()

    backend.view = view

    channel = QWebChannel()
    channel.registerObject("backend", backend)
    view.page().setWebChannel(channel)

    html_path = resource_path("interface/index.html")
    view.load(QUrl.fromLocalFile(html_path))

    tray_icon = QSystemTrayIcon(app_icon, app)
    tray_menu = QMenu()

    show_action = QAction("Open", tray_menu)
    show_action.triggered.connect(view.show)
    
    quit_action = QAction("Quit", tray_menu)
    
    def real_quit():
        view.is_really_quitting = True
        QApplication.quit()
        
    quit_action.triggered.connect(real_quit)
    
    tray_menu.addAction(show_action)
    tray_menu.addSeparator()
    tray_menu.addAction(quit_action)
    
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    def on_tray_icon_activated(reason):
        if reason == QSystemTrayIcon.Trigger:
            if view.isVisible():
                view.hide()
            else:
                view.show()
                view.raise_()
                view.activateWindow()

    tray_icon.activated.connect(on_tray_icon_activated)

    view.resize(1100, 700)
    view.setMinimumSize(800, 550)
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

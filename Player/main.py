import sys, os, platform, subprocess

def restart_without_wayland():
    if platform.system() == "Linux" and os.environ.get("WAYLAND_DISPLAY"):
        print("Wayland detected — restarting in X11 mode...")
        new_env = os.environ.copy()
        new_env.pop("WAYLAND_DISPLAY", None)
        subprocess.run([sys.executable] + sys.argv, env=new_env)
        sys.exit(0)

restart_without_wayland()

from PySide6.QtCore import QObject, Signal, Slot, QUrl, QRunnable, QThreadPool
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

from core.downloader import download_audio
from core.player_logic import MusicPlayer
from config import get_music_base_dir

# === Платформені налаштування ===
if platform.system() == "Linux":
    restart_without_wayland()
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-gpu "
        "--disable-software-rasterizer "
        "--disable-accelerated-2d-canvas "
        "--disable-accelerated-video-decode "
        "--disable-accelerated-mjpeg-decode "
        "--disable-features=VizDisplayCompositor"
    )
elif platform.system() == "Windows":
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = ""
elif platform.system() == "Darwin":
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = ""


class Worker(QRunnable):
    def __init__(self, url, folder, backend):
        super().__init__()
        self.url = url
        self.folder = folder
        self.backend = backend

    def run(self):
        self.backend.log_signal.emit(f"🔄 Downloading: {self.url} → {self.folder}")
        result = download_audio(self.url, self.folder)
        if result is None:
            self.backend.log_signal.emit("❌ Error")
        else:
            self.backend.log_signal.emit("✅ Success")


class Backend(QObject):
    log_signal = Signal(str)
    track_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool.globalInstance()
        self.player = MusicPlayer()
        # Пов'язуємо callback, щоб при зміні трека MusicPlayer викликав Backend.track_changed.emit(...)
        self.player.set_track_change_callback(lambda track: self.track_changed.emit(track))


    # === Downloader ===
    @Slot(result='QStringList')
    def get_folders(self):
        try:
            base_dir = get_music_base_dir()
            return [name for name in os.listdir(base_dir)
                    if os.path.isdir(os.path.join(base_dir, name))]
        except Exception as e:
            self.log_signal.emit(f"❌ Помилка: {e}")
            return []

    @Slot(str, str)
    def start_download(self, url, folder):
        self.thread_pool.start(Worker(url, folder, self))

    # === Player ===
    @Slot(result='QVariantList')
    def list_all_files(self):
        return self.player.list_files()

    @Slot(str, result='QVariantList')
    def list_files(self, folder):
        return self.player.list_files(folder)

    @Slot(str, result='QVariantMap')
    def play_track(self, path):
        # ==== Зупинка поточного треку, якщо він активний або на паузі ====
        try:
            playback_info = self.player.get_playback_info()
            # Якщо щось грається або на паузі — зупиняємо
            if playback_info['is_paused'] or playback_info['position'] > 0:
                self.player.stop()
        except Exception as e:
            self.log_signal.emit(f"❌ stop previous track error: {e}")

        # ==== Відтворення нового треку ====
        track = self.player.play_track(path)
        if track:
            self.track_changed.emit(track)
        return track

    @Slot()
    def toggle_pause(self):
        self.player.toggle_pause()

    @Slot()
    def stop(self):
        self.player.stop()

    @Slot(result=bool)
    def is_active(self):
        return self.player.is_active()

    @Slot(result='QVariantMap')
    def get_playback_info(self):
        try:
            return self.player.get_playback_info()
        except Exception as e:
            self.log_signal.emit(f"❌ get_playback_info error: {e}")
            return {'position': 0, 'duration': 0, 'is_paused': False, 'current_index': -1}
    
    @Slot(float)
    def seek(self, seconds):
        try:
            return self.player.seek(seconds)
        except Exception as e:
            self.log_signal.emit(f"❌ seek error: {e}")
            return False

    @Slot(result='QVariantMap')
    def next_track(self):
        try:
            res = self.player.next_track()
            if res:
                self.track_changed.emit(res)
                return res
            return {}
        except Exception as e:
            self.log_signal.emit(f"❌ next_track error: {e}")
            return {}

    @Slot(result='QVariantMap')
    def prev_track(self):
        try:
            res = self.player.prev_track()
            if res:
                self.track_changed.emit(res)
                return res
            return {}
        except Exception as e:
            self.log_signal.emit(f"❌ prev_track error: {e}")
            return {}


    @Slot()
    def close_app(self):
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    view = QWebEngineView()   # стандартне вікно з рамкою

    backend = Backend()
    channel = QWebChannel()
    channel.registerObject("backend", backend)
    view.page().setWebChannel(channel)

    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "interface/index.html"))
    view.load(QUrl.fromLocalFile(html_path))

    view.resize(1100, 700)
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

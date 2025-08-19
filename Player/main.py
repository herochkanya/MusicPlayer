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
        track = self.player.play_track(path)
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
        if not self.player or not self.player.player:
            return {'position': 0, 'duration': 0}
        try:
            pos = self.player.player.get_pts()
            dur = self.player.player.get_metadata().get('duration', 0)
            return {'position': pos, 'duration': float(dur)}
        except:
            return {'position': 0, 'duration': 0}

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

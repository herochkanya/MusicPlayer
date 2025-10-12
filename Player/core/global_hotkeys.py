# core/global_hotkeys.py
import threading
import platform
from pynput import keyboard

class GlobalHotkeys:
    def __init__(self, player):
        self.player = player
        self.is_windows = platform.system() == "Windows"

    def start(self):
        """Запуск перехоплювача у окремому потоці"""
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        # ============================
        # Перехоплювач клавіш
        # ============================
        def on_press(key):
            try:
                # Стандартні хоткеї
                if key == keyboard.Key.space and self._ctrl_pressed():
                    self.player.toggle_pause()
                elif key == keyboard.Key.right and self._ctrl_pressed():
                    self.player.next_track()
                elif key == keyboard.Key.left and self._ctrl_pressed():
                    self.player.prev_track()

                # Мультимедійні клавіші (Windows)
                if self.is_windows:
                    if key == keyboard.Key.media_play_pause:
                        self.player.toggle_pause()
                    elif key == keyboard.Key.media_next:
                        self.player.next_track()
                    elif key == keyboard.Key.media_previous:
                        self.player.prev_track()
            except AttributeError:
                pass  # деякі клавіші не мають властивості

        # ============================
        # Перевірка Ctrl
        # ============================
        self._pressed_keys = set()

        def on_press_ctrl(key):
            self._pressed_keys.add(key)
            on_press(key)

        def on_release_ctrl(key):
            if key in self._pressed_keys:
                self._pressed_keys.remove(key)

        # ============================
        # Запуск Listener
        # ============================
        with keyboard.Listener(on_press=on_press_ctrl, on_release=on_release_ctrl) as listener:
            listener.join()

    def _ctrl_pressed(self):
        return keyboard.Key.ctrl in self._pressed_keys or keyboard.Key.ctrl_l in self._pressed_keys or keyboard.Key.ctrl_r in self._pressed_keys

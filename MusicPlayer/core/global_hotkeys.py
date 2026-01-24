# global_hotkeys.py

# Core module for global hotkeys using pynput

import threading
import platform
from pynput import keyboard


KEY_ALIASES = {
    # modifiers
    "ctrl": {"ctrl", "ctrl_l", "ctrl_r", "control", "control_l", "control_r"},
    "shift": {"shift", "shift_l", "shift_r"},
    "alt": {"alt", "alt_l", "alt_r", "alt_gr"},
    "cmd": {"cmd", "cmd_l", "cmd_r", "super", "win", "meta"},

    # arrows
    "up": {"up", "arrowup"},
    "down": {"down", "arrowdown"},
    "left": {"left", "arrowleft"},
    "right": {"right", "arrowright"},

    # specials
    "space": {"space", "spacebar", " "},
    "enter": {"enter", "return"},
    "esc": {"esc", "escape"},
    "tab": {"tab"},
    "backspace": {"backspace"},
    "delete": {"delete", "del"},
    "insert": {"insert"},
    "home": {"home"},
    "end": {"end"},
    "pageup": {"page_up"},
    "pagedown": {"page_down"},
}


REVERSE_ALIASES = {
    alias: canon
    for canon, names in KEY_ALIASES.items()
    for alias in names
}


class GlobalHotkeys:
    def __init__(self, player, shortcuts: dict):
        self.player = player
        self.shortcuts = self._normalize_shortcuts(shortcuts)
        self._pressed = set()
        self._lock = threading.Lock()
        self._cooldown = set()

    # ---------------- Public API ----------------

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def update_shortcuts(self, shortcuts: dict):
        with self._lock:
            self.shortcuts = self._normalize_shortcuts(shortcuts)

    # ---------------- Core ----------------

    def _run(self):
        def on_press(key):
            k = self._normalize_key(key)
            if not k:
                return

            self._pressed.add(k)

            with self._lock:
                for action, combo in self.shortcuts.items():
                    if self._combo_active(combo):
                        if action not in self._cooldown:
                            self._cooldown.add(action)
                            self._trigger(action)

        def on_release(key):
            k = self._normalize_key(key)
            if not k:
                return

            self._pressed.discard(k)
            self._cooldown.clear()

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    # ---------------- Logic ----------------

    def _combo_active(self, combo):
        return all(key in self._pressed for key in combo)

    def _trigger(self, action):
        if action == "play_pause":
            self.player.toggle_pause()
        elif action == "next":
            self.player.next_track()
        elif action == "prev":
            self.player.prev_track()

    # ---------------- Normalization ----------------

    def _normalize_shortcuts(self, shortcuts: dict):
        out = {}
        for action, combo in shortcuts.items():
            norm = []
            for k in combo:
                nk = self._normalize_name(k)
                if nk:
                    norm.append(nk)
            out[action] = sorted(set(norm))
        return out

    def _normalize_key(self, key):
        try:
            if isinstance(key, keyboard.Key):
                return self._normalize_name(key.name)
            if isinstance(key, keyboard.KeyCode) and key.char:
                return self._normalize_name(key.char)
        except Exception:
            return None

    def _normalize_name(self, name):
        if not name:
            return None
        n = name.lower()

        # direct alias hit
        if n in REVERSE_ALIASES:
            return REVERSE_ALIASES[n]

        # letters & digits
        if len(n) == 1:
            return n

        # function keys
        if n.startswith("f") and n[1:].isdigit():
            return n

        return n  # fallback (still consistent)

# global_hotkeys.py

import threading
from pynput import keyboard

KEY_ALIASES = {
    "ctrl": {"ctrl", "ctrl_l", "ctrl_r", "control", "control_l", "control_r"},
    "shift": {"shift", "shift_l", "shift_r"},
    "alt": {"alt", "alt_l", "alt_r", "alt_gr"},
    "cmd": {"cmd", "cmd_l", "cmd_r", "super", "win", "meta"},
    "up": {"up", "arrowup"},
    "down": {"down", "arrowdown"},
    "left": {"left", "arrowleft"},
    "right": {"right", "arrowright"},
    "space": {"space", "spacebar", " "},
    "enter": {"enter", "return"},
    "esc": {"esc", "escape"},
}

REVERSE_ALIASES = {alias: canon for canon, names in KEY_ALIASES.items() for alias in names}

class GlobalHotkeys:
    def __init__(self, player, shortcuts: dict):
        self.player = player
        self.shortcuts = self._normalize_shortcuts(shortcuts)
        self._pressed = set()
        self._lock = threading.Lock()
        self._cooldown = set()

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def update_shortcuts(self, shortcuts: dict):
        with self._lock:
            self.shortcuts = self._normalize_shortcuts(shortcuts)

    def _run(self):
        def on_press(key):
            if key == keyboard.Key.media_play_pause:
                self._trigger("play_pause")
                return
            if key == keyboard.Key.media_next:
                self._trigger("next")
                return
            if key == keyboard.Key.media_previous:
                self._trigger("prev")
                return

            k = self._normalize_key(key)
            if not k: return

            with self._lock:
                self._pressed.add(k)
                for action, combo in self.shortcuts.items():
                    if self._combo_active(combo):
                        if action not in self._cooldown:
                            self._cooldown.add(action)
                            self._trigger(action)

        def on_release(key):
            k = self._normalize_key(key)
            if not k: return
            with self._lock:
                self._pressed.discard(k)
                self._cooldown.clear()

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    def _combo_active(self, combo):
        return all(key in self._pressed for key in combo)

    def _trigger(self, action):
        if action == "play_pause":
            self.player.toggle_pause()
        elif action == "next":
            self.player.next_track()
        elif action == "prev":
            self.player.prev_track()

    def _normalize_shortcuts(self, shortcuts: dict):
        out = {}
        for action, combo in shortcuts.items():
            norm = []
            keys = [combo] if isinstance(combo, str) else combo
            for k in keys:
                nk = self._normalize_name(k)
                if nk: norm.append(nk)
            out[action] = sorted(set(norm))
        return out

    def _normalize_key(self, key):
        try:
            if isinstance(key, keyboard.Key):
                return self._normalize_name(key.name)
            
            if isinstance(key, keyboard.KeyCode):
                if 65 <= key.vk <= 90: # A-Z
                    return chr(key.vk).lower()
                if 48 <= key.vk <= 57: # 0-9
                    return chr(key.vk).lower()
                
                if key.char: 
                    return self._normalize_name(key.char)
        except: 
            pass
        return None

    def _normalize_name(self, name):
        if not name: return None
        n = name.lower()
        if n in REVERSE_ALIASES: return REVERSE_ALIASES[n]
        if len(n) == 1: return n
        if n.startswith("f") and n[1:].isdigit(): return n
        return n

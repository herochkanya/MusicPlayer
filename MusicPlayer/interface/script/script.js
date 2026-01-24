// script.js
// Handles UI interactions and communicates with the Python backend via QWebChannel

// Ensure the DOM is fully loaded before running scripts
document.addEventListener('DOMContentLoaded', () => {
    // ==== QWebChannel ====
    new QWebChannel(qt.webChannelTransport, function(channel) {
        Backend.backend = channel.objects.backend;

        Backend.backend.get_download_path().then(path => {
            UI.pathSpan.textContent = path;
        });

        Backend.backend.get_theme().then(theme => {
            applyTheme(theme);
        });

        Backend.backend.theme_changed.connect(theme => {
            applyTheme(theme);
        });

        Backend.backend.get_folders().then(folders => populateFolders(folders));

        Backend.backend.log_signal.connect(msg => {
            UI.debugLog.textContent += msg + "\n";
            UI.debugLog.scrollTop = UI.debugLog.scrollHeight;
        });

        Backend.backend.get_folders().then(folders => {
            UI.folderSelect.innerHTML = '';
            folders.forEach(folder => {
                const div = document.createElement('div');
                div.classList.add('playlist-item');
                div.dataset.name = folder;
                div.textContent = folder;

                div.addEventListener('click', (e) => {
                    if (Backend.setMode) {
                        e.preventDefault();
                        e.stopPropagation();
                        if (Backend.selectedPlaylists.has(folder)) {
                            Backend.selectedPlaylists.delete(folder);
                            div.classList.remove('selected-set');
                        } else {
                            Backend.selectedPlaylists.add(folder);
                            div.classList.add('selected-set');
                        }
                        Backend.backend.set_playlist(folder).then(tracks => {
                            populateTracks(tracks);
                        });
                    } else {
                        Array.from(UI.folderSelect.children).forEach(child => child.classList.remove('selected'));
                        div.classList.add('selected');

                        Backend.backend.set_playlist(folder).then(tracks => {
                            populateTracks(tracks);
                        });

                        UI.folderInput.value = folder;
                    }
                });

                UI.folderSelect.appendChild(div);
            });
        });

        Backend.backend.track_changed.connect(track => {
            if (track) {
                updateTrackInfo(track);
                markPlaying(track.path);
            }

            if (Backend.isPlaying) {
                UI.trackCover.classList.add('rotating');
                UI.trackCover.classList.remove('reset');
            } else {
                UI.trackCover.classList.remove('rotating');
                UI.trackCover.classList.add('reset');
            }
        });

        Backend.backend.playback_state_changed.connect((isPlaying) => {
            UI.playBtn.textContent = isPlaying ? '||' : '►';

            if (isPlaying) {
                UI.trackCover.classList.add('rotating');
                UI.trackCover.classList.remove('reset');
            } else {
                UI.trackCover.classList.remove('rotating');
                UI.trackCover.classList.add('reset');
            }
        });

        Backend.backend.get_language().then(lang => {
            loadLanguage(lang);
            document.getElementById("language-select").value = lang;
            document.getElementById("current-language").textContent =
                lang === "uk" ? "Українська" : "English";
        });

        Backend.backend.language_changed.connect(lang => {
            loadLanguage(lang);
            document.getElementById("current-language").textContent =
                lang === "uk" ? "Українська" : "English";
        });

        Backend.backend.get_custom_background().then(path => {
            if (!path) return;
            const cssPath = path.replace(/\\/g, "/");
            document.documentElement.style.setProperty(
                "--custom-bg-image",
                `url("${cssPath}")`
            );
        });

        // Animation toggles

        const animationState = {
            screen: true,
            cover: true,
            pulse: true
        };

        function applyAnimationAttributes() {
            const root = document.documentElement;
            root.setAttribute("data-animation-screen", String(animationState.screen));
            root.setAttribute("data-animation-cover", String(animationState.cover));
            root.setAttribute("data-animation-pulse", String(animationState.pulse));
        }

        function saveAnimationSettings() {
            Backend.backend.set_animation_settings(animationState);
        }

        UI.screenAnimationToggle.addEventListener("change", e => {
            animationState.screen = e.target.checked;
            applyAnimationAttributes();
            saveAnimationSettings();
        });

        UI.coverAnimationToggle.addEventListener("change", e => {
            animationState.cover = e.target.checked;
            applyAnimationAttributes();
            saveAnimationSettings();
        });

        UI.pulseAnimationToggle.addEventListener("change", e => {
            animationState.pulse = e.target.checked;
            applyAnimationAttributes();
            saveAnimationSettings();
        });

        Backend.backend.get_animation_settings().then(settings => {
            animationState.screen = !!settings.screen;
            animationState.cover = !!settings.cover;
            animationState.pulse = !!settings.pulse;

            UI.screenAnimationToggle.checked = animationState.screen;
            UI.coverAnimationToggle.checked = animationState.cover;
            UI.pulseAnimationToggle.checked = animationState.pulse;

            applyAnimationAttributes();
        });

        Backend.backend.get_cover_settings().then(style => {
            document.documentElement.setAttribute("data-cover", style);
        });

        // ==== Equalizer ====
        Backend.backend.get_equalizer_settings().then(eq => {
            sliders[0].value = eq["60"];
            sliders[1].value = eq["150"];
            sliders[2].value = eq["400"];
            sliders[3].value = eq["1000"];
            sliders[4].value = eq["2400"];
            sliders[5].value = eq["15000"];
            updateCurve();
        });

        function saveEqSettings() {
            const eq = {
                "60": parseFloat(sliders[0].value),
                "150": parseFloat(sliders[1].value),
                "400": parseFloat(sliders[2].value),
                "1000": parseFloat(sliders[3].value),
                "2400": parseFloat(sliders[4].value),
                "15000": parseFloat(sliders[5].value),
            };
            Backend.backend.set_equalizer_settings(eq);
        }

        dots.forEach(dot => dot.addEventListener("pointerup", saveEqSettings));
        resetBtn.addEventListener("click", saveEqSettings);

        const shortcutMap = {
            play_pause: UI.shortcutPause,
            next: UI.shortcutNext,
            prev: UI.shortcutPrev
        };

        let captureMode = null;
        let capturedKeys = [];

        function keyToLabel(e) {
            if (e.key === " ") return "Space";
            if (e.key.length === 1) return e.key.toUpperCase();
            return e.key.replace("Arrow", "");
        }

        function normalizeKey(e) {
            if (e.key === " ") return "space";
            return e.key.toLowerCase();
        }

        function formatCombo(keys) {
            return keys.map(k => k.toUpperCase()).join(" + ");
        }

        function enterCaptureMode(action) {
            captureMode = action;
            capturedKeys = [];
            shortcutMap[action].textContent = "Press keys…";
            shortcutMap[action].classList.add("capturing");
        }

        function exitCaptureMode(save = true) {
            if (!captureMode) return;

            const action = captureMode;
            const el = shortcutMap[action];
            el.classList.remove("capturing");

            if (save && capturedKeys.length === 2) {
                const combo = capturedKeys.map(k => k.normalized);
                el.textContent = formatCombo(combo);

                Backend.backend.get_shortcuts().then(current => {
                    current[action] = combo;
                    Backend.backend.set_shortcuts(current);
                });
            }

            captureMode = null;
            capturedKeys = [];
        }

        // ==== Load shortcuts from backend ====
        Backend.backend.get_shortcuts().then(shortcuts => {
            for (const [action, combo] of Object.entries(shortcuts)) {
                if (shortcutMap[action]) {
                    shortcutMap[action].textContent = formatCombo(combo);
                }
            }
        });

        // ==== Bind change buttons ====
        UI.shortcutPauseChangeBtn.addEventListener("click", () => enterCaptureMode("play_pause"));
        UI.shortcutNextChangeBtn.addEventListener("click", () => enterCaptureMode("next"));
        UI.shortcutPrevChangeBtn.addEventListener("click", () => enterCaptureMode("prev"));

        // ==== Global key capture ====
        document.addEventListener("keydown", e => {
            if (!captureMode) return;

            e.preventDefault();
            e.stopPropagation();

            const normalized = normalizeKey(e);
            const label = keyToLabel(e);

            if (capturedKeys.some(k => k.normalized === normalized)) return;

            capturedKeys.push({ normalized, label });

            shortcutMap[captureMode].textContent =
                capturedKeys.map(k => k.label).join(" + ");

            if (capturedKeys.length === 2) {
                exitCaptureMode(true);
            }
        }, true);
    });
});

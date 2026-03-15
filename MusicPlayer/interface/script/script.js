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

        // Temporary cache for tracks to be downloaded
        let preDownloadCache = [];

        function initDownloaderSignals() {
            if (!Backend.backend) return;

            // 1. When we get info about a new track in the queue
            Backend.backend.pre_track_info_signal.connect((meta) => {
                // Avoid duplicates if yt-dlp sends info multiple times
                if (!preDownloadCache.find(t => t.id === meta.id)) {
                    preDownloadCache.push(meta);
                    renderPreList();
                }
            });

            // 2. When a track is finished, remove it from the list
            Backend.backend.track_finished_signal.connect((trackId) => {
                preDownloadCache = preDownloadCache.filter(t => t.id !== trackId);
                renderPreList();
            });
        }

        function renderPreList() {
            UI.trackPreList.innerHTML = '';
            
            preDownloadCache.forEach(track => {
                const div = document.createElement('div');
                div.classList.add('track-item');
                div.style.opacity = '0.7';
                
                const cover = track.thumbnail 
                    ? `<img src="${track.thumbnail}" style="width:2.5rem;height:2.5rem;margin-right:0.5rem;border-radius:0.4rem;vertical-align:middle;object-fit:cover;">` 
                    : '';
                    
                div.innerHTML = `
                    ${cover} 
                    <div style="display:inline-block; vertical-align:middle;">
                        <div style="font-weight:bold; font-size:0.9rem;">${track.title}</div>
                        <div style="font-size:0.75rem; color:var(--text-dim);">${track.artist}</div>
                    </div>
                `;
                
                UI.trackPreList.appendChild(div);
            });

            // Auto-scroll to the bottom of the pre-list
            UI.trackPreList.scrollTop = UI.trackPreList.scrollHeight;
        }
        setTimeout(initDownloaderSignals, 500);

        // Queue signal
        Backend.backend.playlist_progress_signal.connect((current, total, title) => {
            let progressEl = document.getElementById('playlist-sticky-log');
            
            if (total <= 1 && current === 0) {
                if (progressEl) progressEl.style.display = 'none';
                return;
            }

            progressEl.style.display = 'block';
            progressEl.textContent = `📦 Playlist: ${title} | Track: ${current} of ${total} 🚀`;
            
            UI.debugLog.scrollTop = UI.debugLog.scrollHeight;
        });

        // Log signal
        Backend.backend.log_signal.connect(msg => {
            const cleanMsg = msg.trim();
            if (!cleanMsg) return;

            let currentLog = UI.debugLog.textContent;

            const isProgress = cleanMsg.includes('⬇️') || cleanMsg.includes('🎵');

            if (isProgress) {
                let lines = currentLog.split('\n');
                
                if (lines.length > 0 && (lines[lines.length - 1].includes('⬇️') || lines[lines.length - 1].includes('🎵'))) {
                    lines[lines.length - 1] = cleanMsg;
                    UI.debugLog.textContent = lines.join('\n');
                } else {
                    UI.debugLog.textContent += (currentLog ? '\n' : '') + cleanMsg;
                }
            } else {
                UI.debugLog.textContent += (currentLog ? '\n' : '') + cleanMsg;
            }

            UI.debugLog.scrollTop = UI.debugLog.scrollHeight;
        });

        // Clear the static HTML placeholders first
        UI.urlListContainer.innerHTML = '';
        addUrlRow();

        // Attach event listener to the "Add" button
        if (UI.newUrlBtn) {
            UI.newUrlBtn.addEventListener('click', () => addUrlRow());
        }

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

        // ==== Cover style selection ====

        UI.setCoverBtn.addEventListener("click", e => {
            const style = UI.coverSelect.value;
            document.documentElement.setAttribute("data-cover", style);
            Backend.backend.set_cover_settings(style);
            animationState.cover = e.target.checked;
            applyAnimationAttributes();
            saveAnimationSettings();
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

        // ==== Shortcut key capture ====

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

        Backend.backend.get_shortcuts().then(shortcuts => {
            for (const [action, combo] of Object.entries(shortcuts)) {
                if (shortcutMap[action]) {
                    shortcutMap[action].textContent = formatCombo(combo);
                }
            }
        });

        UI.shortcutPauseChangeBtn.addEventListener("click", () => enterCaptureMode("play_pause"));
        UI.shortcutNextChangeBtn.addEventListener("click", () => enterCaptureMode("next"));
        UI.shortcutPrevChangeBtn.addEventListener("click", () => enterCaptureMode("prev"));

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

        // ==== Lite theme handling ====

        Backend.backend.get_lite_mode().then(state => {
            Backend.isLiteMode = state;
            UI.liteThemeToggle.checked = state;
            
            Backend.backend.get_theme().then(theme => {
                applyTheme(theme); 
            });
        });

        Backend.backend.lite_mode_changed.connect(state => {
            Backend.isLiteMode = state;
            UI.liteThemeToggle.checked = state;
            applyTheme();
        });

        // ==== Tray mode handling ====
        
        Backend.backend.get_tray_mode().then(state => {
            UI.shortcutTray.checked = state;
        });

        Backend.backend.tray_mode_changed.connect(state => {
            UI.shortcutTray.checked = state;
        });

        UI.shortcutTray.addEventListener('change', (e) => {
            Backend.backend.set_tray_mode(e.target.checked);
        });
    });
});

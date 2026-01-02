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
            UI.playBtn.textContent = isPlaying ? '⏸' : '▶';

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
        });
    });
});

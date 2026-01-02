// playback.js

document.addEventListener('DOMContentLoaded', () => {
        // ==== Playback controls ====

    UI.playBtn.addEventListener('click', () => {
        if (!Backend.currentTrackPath) return;
        Backend.backend.toggle_pause();
        Backend.isPlaying = !Backend.isPlaying;
        UI.playBtn.textContent = Backend.isPlaying ? '⏸' : '▶';
    });

    UI.backBtn.addEventListener('click', () => {
        Backend.backend.prev_track().then(track => {
            if (track && track.path) {
                updateTrackInfo(track);
                Backend.currentTrackPath = track.path;
                Backend.isPlaying = true;
                UI.playBtn.textContent = '⏸';
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
    });

    UI.nextBtn.addEventListener('click', () => {
        Backend.backend.next_track().then(track => {
            if (track && track.path) {
                updateTrackInfo(track);
                Backend.currentTrackPath = track.path;
                Backend.isPlaying = true;
                UI.playBtn.textContent = '⏸';
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
    });

    // ==== Track progress update ====

    // Update progress bar every second
    setInterval(() => {
        if (!Backend.backend || !Backend.currentTrackPath) return;
        Backend.backend.get_playback_info().then(info => {
            const pos = info.position || 0;
            const dur = info.duration || 0;

            UI.progressBar.max = Math.floor(dur);
            UI.progressBar.value = Math.floor(pos);

            UI.currentTimeText.textContent = formatTime(pos);
            UI.totalTimeText.textContent = formatTime(dur);
        });
    }, 1000);

    // Seek when user changes the progress bar
    UI.progressBar.addEventListener('change', () => {
        if (!Backend.backend || !Backend.currentTrackPath) return;
        Backend.backend.seek(UI.progressBar.value);
    });

    // Format seconds to mm:ss
    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    }
});

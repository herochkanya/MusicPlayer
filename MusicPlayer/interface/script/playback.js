// playback.js

document.addEventListener('DOMContentLoaded', () => {
        // ==== Playback controls ====

    UI.playBtn.addEventListener('click', () => {
        if (!Backend.currentTrackPath) return;
        Backend.backend.toggle_pause();
        Backend.isPlaying = !Backend.isPlaying;
        UI.playBtn.textContent = Backend.isPlaying ? '||' : '►';
    });

    UI.backBtn.addEventListener('click', () => {
        Backend.backend.prev_track().then(track => {
            if (track && track.path) {
                updateTrackInfo(track);
                Backend.currentTrackPath = track.path;
                Backend.isPlaying = true;
                UI.playBtn.textContent = '||';
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
                UI.playBtn.textContent = '||';
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

            // Lyrics synchronisation
            if (currentLyrics.length > 0 && currentLyrics[0].time !== -1) {
                let activeIndex = -1;
                for (let i = 0; i < currentLyrics.length; i++) {
                    if (pos >= currentLyrics[i].time) {
                        activeIndex = i;
                    } else {
                        break;
                    }
                }

                if (activeIndex !== -1) {
                    document.querySelectorAll('.lyric-line').forEach(l => l.classList.remove('current'));
                    
                    const activeLine = document.getElementById(`lyric-line-${activeIndex}`);
                    if (activeLine) {
                        activeLine.classList.add('current');
                        
                        UI.lyricsPanel.scrollTo({
                            top: activeLine.offsetTop - UI.lyricsPanel.offsetHeight / 2,
                            behavior: 'smooth'
                        });
                    }
                }
            }
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

    // ==== Volume Controls ====

    // Listener for volume slider
    UI.volumeBar.addEventListener('input', () => {
        const vol = UI.volumeBar.value;
        // Update backend
        Backend.backend.set_volume(parseInt(vol));
        
        // Update icon based on volume level
        if (vol == 0) {
            UI.muteBtn.textContent = '🔇';
        } else if (vol < 50) {
            UI.muteBtn.textContent = '🔉';
        } else {
            UI.muteBtn.textContent = '🔊';
        }
    });

    // Listener for Mute button
    UI.muteBtn.addEventListener('click', () => {
        Backend.backend.toggle_mute().then(isMuted => {
            if (isMuted) {
                UI.muteBtn.textContent = '🔇';
                // We can visually dim the slider or set it to 0
                UI.volumeBar.style.opacity = '0.5';
            } else {
                // Restore icon based on current value
                const vol = UI.volumeBar.value;
                UI.muteBtn.textContent = vol < 50 ? '🔉' : '🔊';
                UI.volumeBar.style.opacity = '1';
            }
        });
    });
});


let currentLyrics = [];

async function loadLyrics(trackPath) {
    const lyricsRaw = await Backend.backend.get_lyrics(trackPath);
    const panel = UI.lyricsPanel;
    panel.innerHTML = '';
    currentLyrics = [];

    if (lyricsRaw === "NOT_FOUND" || lyricsRaw === "ERROR") {
        panel.innerHTML = `<div class="lyric-line" style="opacity: 1; margin-top: 20vh;">
            ${(lyricsRaw === "NOT_FOUND") ? "Lyrics not found" : "Error loading lyrics"}
        </div>`;
        return;
    }

    // LRC
    const lines = lyricsRaw.split('\n');
    const timeReg = /\[(\d{2}):(\d{2})\.(\d{2,3})\]/;

    lines.forEach(line => {
        const match = timeReg.exec(line);
        if (match) {
            const minutes = parseInt(match[1]);
            const seconds = parseInt(match[2]);
            const ms = parseInt(match[3]);
            const time = minutes * 60 + seconds + (ms > 99 ? ms / 1000 : ms / 100);
            const text = line.replace(timeReg, '').trim();
            if (text) {
                currentLyrics.push({ time, text });
            }
        } else if (line.trim()) {
            currentLyrics.push({ time: -1, text: line.trim() });
        }
    });

    currentLyrics.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'lyric-line';
        div.id = `lyric-line-${index}`;
        div.textContent = item.text;
        panel.appendChild(div);
    });
}
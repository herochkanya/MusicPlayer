document.addEventListener('DOMContentLoaded', () => {
    const downloaderScreen = document.getElementById('downloader-screen');
    const playerScreen = document.getElementById('player-screen');

    const openDownloaderBtn = document.getElementById('open-downloader-btn');
    const openPlayerBtn = document.getElementById('open-player-btn');

    const debugLog = document.getElementById('debug-log');
    const foldersList = document.getElementById('folders-list');
    const folderInput = document.getElementById('folder-input');
    const startDownloadBtn = document.getElementById('start-download-btn');
    const urlInput = document.getElementById('url-input');

    const folderSelect = document.getElementById('folder-select');
    const trackList = document.getElementById('track-list');

    const trackTitle = document.getElementById('track-title');
    const trackArtist = document.getElementById('track-artist');
    const trackCover = document.getElementById('track-cover');

    const playBtn = document.getElementById('playpause-btn');
    const progressBar = document.getElementById('progress-bar');
    const currentTimeText = document.getElementById('current-time');
    const totalTimeText = document.getElementById('total-time');
    const backBtn = document.getElementById('back-btn');
    const nextBtn = document.getElementById('next-btn');
    const cycleBtn = document.getElementById('cycle-btn');
    const randomBtn = document.getElementById('random-btn');

    let backend;
    let currentTrackPath = null;
    let isPlaying = false;

    openDownloaderBtn.addEventListener('click', () => showScreen('downloader-screen'));
    openPlayerBtn.addEventListener('click', () => showScreen('player-screen'));
    showScreen('player-screen');

    function showScreen(id) {
        [downloaderScreen, playerScreen].forEach(screen => screen.classList.remove('active'));
        document.getElementById(id).classList.add('active');
    }

    // ==== QWebChannel ====
    new QWebChannel(qt.webChannelTransport, function(channel) {
        backend = channel.objects.backend;

        backend.get_folders().then(folders => populateFolders(folders));

        backend.log_signal.connect(msg => {
            debugLog.textContent += msg + "\n";
            debugLog.scrollTop = debugLog.scrollHeight;
        });

        // build folder list; clicking a folder will set internal playlist (not just read disk)
        backend.get_folders().then(folders => {
            folderSelect.innerHTML = '';
            folders.forEach(folder => {
                const div = document.createElement('div');
                div.textContent = folder;
                div.addEventListener('click', () => {
                    Array.from(folderSelect.children).forEach(child => child.classList.remove('selected'));
                    div.classList.add('selected');

                    // встановлюємо playlist у backend і отримуємо playlist як список dict
                    backend.set_playlist(folder).then(tracks => {
                        populateTracks(tracks);
                    });

                    folderInput.value = folder;
                });
                folderSelect.appendChild(div);
            });
        });

        // коли бекенд каже що трек змінився — оновлюємо інфо та підсвічуємо у списку
        backend.track_changed.connect(track => {
            if (track) {
                updateTrackInfo(track);
                markPlaying(track.path);
            }
        });
    });

    // ==== Populate ====
    function populateFolders(folders) {
        foldersList.innerHTML = '';
        folders.forEach(folder => {
            const div = document.createElement('div');
            div.textContent = folder;
            div.addEventListener('click', () => {
                Array.from(foldersList.children).forEach(child => child.classList.remove('selected'));
                div.classList.add('selected');
                folderInput.value = folder;
            });
            foldersList.appendChild(div);
        });
    }

    function populateTracks(tracks) {
        trackList.innerHTML = '';
        tracks.forEach(track => {
            const div = document.createElement('div');
            div.classList.add('track-item');
            div.dataset.path = track.path; // зручно для пошуку
            const cover = track.cover_path 
                ? `<img src="${track.cover_path.startsWith('file://') ? track.cover_path : 'file://' + track.cover_path}" 
                        style="width:3rem;height:3rem;margin-right:0.5rem;border-radius:0.5rem;vertical-align:middle;">` 
                : '';
            div.innerHTML = `${cover} <span>${track.title || '—'} — ${track.artist || '—'}</span>`;

            div.addEventListener('click', () => {
                backend.play_track(track.path).then(info => {
                    if (info) {
                        updateTrackInfo(info);
                        currentTrackPath = track.path;
                        isPlaying = true;
                        playBtn.textContent = '⏸';
                        markPlaying(track.path);
                    }
                });
            });
            trackList.appendChild(div);
        });

        // після (ре)побудови списку — підсвітити поточний, якщо він відомий
        if (currentTrackPath) markPlaying(currentTrackPath);
    }

    function updateTrackInfo(track) {
        trackTitle.textContent = track.title || '—';
        trackArtist.textContent = track.artist || '—';
        trackCover.src = track.cover_path 
            ? (track.cover_path.startsWith('file://') ? track.cover_path : 'file://' + track.cover_path)
            : '';
    }

    function markPlaying(path) {
        // знімаємо клас playing з усіх
        Array.from(trackList.children).forEach(div => {
            div.classList.remove('playing');
        });
        if (!path) return;
        // знаходимо елемент з data-path
        const el = Array.from(trackList.children).find(div => div.dataset.path === path);
        if (el) {
            el.classList.add('playing');
            // прокрутимо трохи, щоб було видно
            el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    // ==== Download ====
    startDownloadBtn.addEventListener('click', () => {
        const url = urlInput.value.trim();
        const folder = folderInput.value.trim() || 'downloads';
        if (!url) return alert('Введіть URL!');
        debugLog.textContent += `Запуск завантаження...\n`;
        backend.start_download(url, folder);
    });

    // ==== Playback ====
    playBtn.addEventListener('click', () => {
        if (!currentTrackPath) return;
        backend.toggle_pause();
        isPlaying = !isPlaying;
        playBtn.textContent = isPlaying ? '⏸' : '▶';
    });

    // ==== Next / Prev ====
    backBtn.addEventListener('click', () => {
        backend.prev_track().then(track => {
            if (track && track.path) {
                updateTrackInfo(track);
                currentTrackPath = track.path;
                isPlaying = true;
                playBtn.textContent = '⏸';
                markPlaying(track.path);
            }
        });
    });

    nextBtn.addEventListener('click', () => {
        backend.next_track().then(track => {
            if (track && track.path) {
                updateTrackInfo(track);
                currentTrackPath = track.path;
                isPlaying = true;
                playBtn.textContent = '⏸';
                markPlaying(track.path);
            }
        });
    });

    // ==== Progress ====
    setInterval(() => {
        if (!backend || !currentTrackPath) return;
        backend.get_playback_info().then(info => {
            const pos = info.position || 0;
            const dur = info.duration || 0;

            progressBar.max = Math.floor(dur);
            progressBar.value = Math.floor(pos);

            currentTimeText.textContent = formatTime(pos);
            totalTimeText.textContent = formatTime(dur);
        });
    }, 1000);

    progressBar.addEventListener('change', () => {
        if (!backend || !currentTrackPath) return;
        backend.seek(progressBar.value);
    });

    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    }

    // ===== Cycle button =====
    let cycleMode = 0; // 0 = off, 1 = all, 2 = one
    cycleBtn.addEventListener('click', () => {
        cycleMode = (cycleMode + 1) % 3;
        switch (cycleMode) {
            case 0:
                cycleBtn.textContent = '🗘';
                backend.set_cycle_mode(0);
                break;
            case 1:
                cycleBtn.textContent = '🔁';
                backend.set_cycle_mode(1);
                break;
            case 2:
                cycleBtn.textContent = '🔂';
                backend.set_cycle_mode(2);
                break;
        }
    });

    // ===== Shuffle / Random =====
    randomBtn.addEventListener('click', () => {
        // toggle_shuffle повертає bool (on/off)
        backend.toggle_shuffle().then(shuffle_on => {
            // після зміни shuffle — отримуємо поточний internal playlist і перебудовуємо UI
            backend.get_playlist().then(tracks => {
                populateTracks(tracks);
                // якщо shuffle включився, змінюємо текст і підсвічуємо
                randomBtn.textContent = shuffle_on ? '🔀' : '🎵';
            });
        });
    });
});

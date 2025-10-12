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
    const searchInput = document.getElementById('text-input');

    const globalBtn = document.getElementById('open-global-btn');
    const setPlaylistBtn = document.getElementById('open-set-btn');

    const themeBtn = document.getElementById('theme-btn');

    let backend;
    let currentTrackPath = null;
    let isPlaying = false;
    let playerOriginalHeight = null;
    let setMode = false;
    let selectedPlaylists = new Set();
    const themes = ['green', 'dark', 'light'];
    let currentThemeIndex = 0;

    openDownloaderBtn.addEventListener('click', () => showScreen('downloader-screen'));
    openPlayerBtn.addEventListener('click', () => showScreen('player-screen'));
    showScreen('player-screen');

    function showScreen(id) {
        [downloaderScreen, playerScreen].forEach(screen => {
            screen.classList.remove('active');
        });
        const activeScreen = document.getElementById(id);
        activeScreen.style.display = 'flex';
        setTimeout(() => activeScreen.classList.add('active'), 10);
    }

    // ==== QWebChannel ====
    new QWebChannel(qt.webChannelTransport, function(channel) {
        backend = channel.objects.backend;

        backend.get_folders().then(folders => populateFolders(folders));

        backend.log_signal.connect(msg => {
            debugLog.textContent += msg + "\n";
            debugLog.scrollTop = debugLog.scrollHeight;
        });

        backend.get_folders().then(folders => {
            folderSelect.innerHTML = '';
            folders.forEach(folder => {
                const div = document.createElement('div');
                div.classList.add('playlist-item');
                div.dataset.name = folder;
                div.textContent = folder;

                div.addEventListener('click', (e) => {
                    if (setMode) {
                        e.preventDefault();
                        e.stopPropagation();
                        if (selectedPlaylists.has(folder)) {
                            selectedPlaylists.delete(folder);
                            div.classList.remove('selected-set');
                        } else {
                            selectedPlaylists.add(folder);
                            div.classList.add('selected-set');
                        }
                        // показуємо вміст плейлісту, як старе розгортання
                        backend.set_playlist(folder).then(tracks => {
                            populateTracks(tracks);
                        });
                    } else {
                        // Стара поведінка: виділяємо тільки один
                        Array.from(folderSelect.children).forEach(child => child.classList.remove('selected'));
                        div.classList.add('selected');

                        backend.set_playlist(folder).then(tracks => {
                            populateTracks(tracks);
                        });

                        folderInput.value = folder;
                    }
                });

                folderSelect.appendChild(div);
            });
        });

        backend.track_changed.connect(track => {
            if (track) {
                updateTrackInfo(track);
                markPlaying(track.path);
            }

            if (isPlaying) {
                trackCover.classList.add('rotating');
                trackCover.classList.remove('reset');
            } else {
                trackCover.classList.remove('rotating');
                trackCover.classList.add('reset');
            }
        });

        backend.playback_state_changed.connect((isPlaying) => {
            playBtn.textContent = isPlaying ? '⏸' : '▶';

            if (isPlaying) {
                trackCover.classList.add('rotating');
                trackCover.classList.remove('reset');
            } else {
                trackCover.classList.remove('rotating');
                trackCover.classList.add('reset');
            }
        });
    });

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
            div.dataset.path = track.path;
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

                    if (isPlaying) {
                        trackCover.classList.add('rotating');
                        trackCover.classList.remove('reset');
                    } else {
                        trackCover.classList.remove('rotating');
                        trackCover.classList.add('reset');
                    }
                });
            });
            trackList.appendChild(div);
        });

        if (currentTrackPath) markPlaying(currentTrackPath);
    }

    function updateTrackInfo(track) {
        trackCover.classList.remove('rotating', 'reset');
        trackCover.style.transform = 'rotate(0deg)';
        trackTitle.textContent = track.title || '—';
        trackArtist.textContent = track.artist || '—';
        trackCover.classList.add('change');
        setTimeout(() => {
            trackCover.src = track.cover_path 
                ? (track.cover_path.startsWith('file://') ? track.cover_path : 'file://' + track.cover_path)
                : '';
            trackCover.classList.remove('change');
        }, 300);
    }

    function markPlaying(path) {
        Array.from(trackList.children).forEach(div => div.classList.remove('playing'));
        if (!path) return;
        const el = Array.from(trackList.children).find(div => div.dataset.path === path);
        if (el) {
            el.classList.add('playing');
            el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    function toggleDownloader(show) {
        if (show) {
            if (!playerOriginalHeight)
                playerOriginalHeight = playerScreen.offsetHeight;

            playerScreen.style.transition = 'all 0.6s ease';
            playerScreen.style.transform = 'scale(0.9)';
            playerScreen.style.opacity = '0.5';
            playerScreen.style.pointerEvents = 'none';

            downloaderScreen.style.display = 'flex';
            setTimeout(() => downloaderScreen.classList.add('active'), 10);
        } else {
            downloaderScreen.classList.remove('active');
            setTimeout(() => {
                downloaderScreen.style.display = 'none';
                playerScreen.style.transition = 'all 0.6s ease';
                playerScreen.style.transform = 'scale(1)';
                playerScreen.style.opacity = '1';
                playerScreen.style.pointerEvents = 'auto';
            }, 400);
        }
    }

    openDownloaderBtn.addEventListener('click', () => toggleDownloader(true));
    openPlayerBtn.addEventListener('click', () => toggleDownloader(false));

    startDownloadBtn.addEventListener('click', () => {
        const url = urlInput.value.trim();
        const folder = folderInput.value.trim() || 'downloads';
        if (!url) return debugLog.textContent += 'Please enter a URL!\n';
        debugLog.textContent += `Download started... \nIt'll take a couple of minutes.\n`;
        backend.start_download(url, folder);
    });

    playBtn.addEventListener('click', () => {
        if (!currentTrackPath) return;
        backend.toggle_pause();
        isPlaying = !isPlaying;
        playBtn.textContent = isPlaying ? '⏸' : '▶';
    });

    backBtn.addEventListener('click', () => {
        backend.prev_track().then(track => {
            if (track && track.path) {
                updateTrackInfo(track);
                currentTrackPath = track.path;
                isPlaying = true;
                playBtn.textContent = '⏸';
                markPlaying(track.path);
            }

            if (isPlaying) {
                trackCover.classList.add('rotating');
                trackCover.classList.remove('reset');
            } else {
                trackCover.classList.remove('rotating');
                trackCover.classList.add('reset');
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

            if (isPlaying) {
                trackCover.classList.add('rotating');
                trackCover.classList.remove('reset');
            } else {
                trackCover.classList.remove('rotating');
                trackCover.classList.add('reset');
            }
        });
    });

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

    let cycleMode = 0;
    cycleBtn.addEventListener('click', () => {
        cycleMode = (cycleMode + 1) % 3;
        switch (cycleMode) {
            case 0:
                cycleBtn.textContent = '→';
                backend.set_cycle_mode(0);
                break;
            case 1:
                cycleBtn.textContent = '⇄';
                backend.set_cycle_mode(1);
                break;
            case 2:
                cycleBtn.textContent = '⥁';
                backend.set_cycle_mode(2);
                break;
        }
    });

    randomBtn.addEventListener('click', () => {
        backend.toggle_shuffle().then(shuffle_on => {
            backend.get_playlist().then(tracks => {
                populateTracks(tracks);
                randomBtn.textContent = shuffle_on ? '🔀' : '🎵';
            });
        });
    });

    searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim().toLowerCase();
        Array.from(trackList.children).forEach(div => {
            const title = div.querySelector('span')?.textContent.toLowerCase() || '';
            div.style.display = title.includes(query) ? '' : 'none';
        });
    });

    globalBtn.addEventListener('click', () => {
        Array.from(folderSelect.children).forEach(child => child.classList.remove('selected'));
        globalBtn.classList.add('selected');
        backend.set_global_playlist().then(tracks => populateTracks(tracks));
    });

    // ==== SET PLAYLIST MODE ====
    setPlaylistBtn.addEventListener('click', () => {
        if (setMode) {
            // вихід з режиму вибору
            setMode = false;
            setPlaylistBtn.classList.remove('active');

            const selected = Array.from(selectedPlaylists);
            selectedPlaylists.clear();

            if (selected.length > 0) {
                // створюємо тимчасовий плейліст на бекенді
                backend.create_temp_playlist(selected).then(tracks => {
                    // оновлюємо UI списком тимчасового плейліста
                    populateTracks(tracks);
                });
            }

            // прибираємо виділення на папках
            document.querySelectorAll('.playlist-item.selected-set')
                .forEach(el => el.classList.remove('selected-set'));

        } else {
            // вхід у режим вибору
            setMode = true;
            setPlaylistBtn.classList.add('active');
            selectedPlaylists.clear();
        }
    });

   themeBtn.addEventListener('click', () => {
        currentThemeIndex = (currentThemeIndex + 1) % themes.length;
        // Застосовуємо тему до кореневого елемента :root
        document.documentElement.setAttribute('data-theme', themes[currentThemeIndex]);

        // змінюємо іконку на кнопці відповідно до теми
        switch(themes[currentThemeIndex]){
            case 'green': themeBtn.textContent = '☘️'; break;
            case 'dark': themeBtn.textContent = '🌙'; break;
            case 'light': themeBtn.textContent = '☀️'; break;
        }
    });
});

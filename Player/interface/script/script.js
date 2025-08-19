document.addEventListener('DOMContentLoaded', () => {
    // ==== DOM elements ====
    const downloaderScreen = document.getElementById('downloader-screen');
    const playerScreen = document.getElementById('player-screen');

    const openDownloaderBtn = document.getElementById('open-downloader-btn');
    const openPlayerBtn = document.getElementById('open-player-btn');
    const closeBtn = document.getElementById('close-btn');

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

    const playBtn = document.getElementById('play-btn');
    const pauseBtn = document.getElementById('pause-btn');

    const progressBar = document.getElementById('progress-bar');
    const currentTimeText = document.getElementById('current-time');
    const totalTimeText = document.getElementById('total-time');

    let backend;
    let currentTrackPath = null;

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

        // Downloader
        backend.get_folders().then(folders => populateFolders(folders));
        backend.log_signal.connect(msg => {
            debugLog.textContent += msg + "\n";
            debugLog.scrollTop = debugLog.scrollHeight;
        });

        // Player folders
        backend.get_folders().then(folders => {
            folderSelect.innerHTML = '';
            folders.forEach(folder => {
                const div = document.createElement('div');
                div.textContent = folder;
                div.addEventListener('click', () => {
                    Array.from(folderSelect.children).forEach(child => child.classList.remove('selected'));
                    div.classList.add('selected');
                    backend.list_files(folder).then(tracks => populateTracks(tracks));
                });
                folderSelect.appendChild(div);
            });
        });
    });

    // ==== Populate functions ====
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
            div.textContent = `${track.title} — ${track.artist}`;
            div.addEventListener('click', () => {
                backend.play_track(track.path).then(info => {
                    trackTitle.textContent = info.title;
                    trackArtist.textContent = info.artist;
                    trackCover.src = info.cover_path || '';
                    currentTrackPath = track.path;
                });
            });
            trackList.appendChild(div);
        });
    }

    // ==== Download controls ====
    startDownloadBtn.addEventListener('click', () => {
        const url = urlInput.value.trim();
        const folder = folderInput.value.trim() || 'downloads';
        if (!url) return alert('Введіть URL!');
        debugLog.textContent += `Запуск завантаження...\n`;
        backend.start_download(url, folder);
    });

    // ==== Playback controls ====
    playBtn.addEventListener('click', () => {
        if (currentTrackPath) backend.play_track(currentTrackPath);
    });
    pauseBtn.addEventListener('click', () => backend.toggle_pause());
    closeBtn.addEventListener('click', () => backend.close_app());

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

    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    }
});

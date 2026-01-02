// global.js

window.UI = {
    downloaderScreen: document.getElementById('downloader-screen'),
    playerScreen: document.getElementById('player-screen'),
    settingsScreen: document.getElementById('settings-screen'),

    switchDownloaderPlayerBtn: document.getElementById('switch-downloader-player-btn'),
    openSettingsBtn: document.getElementById('open-settings-btn'),

    debugLog: document.getElementById('debug-log'),
    startDownloadBtn: document.getElementById('start-download-btn'),
    urlInput: document.getElementById('url-input'),

    foldersList: document.getElementById('folders-list'),
    folderInput: document.getElementById('folder-input'),
    folderSelect: document.getElementById('folder-select'),
    trackList: document.getElementById('track-list'),

    trackTitle: document.getElementById('track-title'),
    trackArtist: document.getElementById('track-artist'),
    trackCover: document.getElementById('track-cover'),

    playBtn: document.getElementById('playpause-btn'),
    backBtn: document.getElementById('back-btn'),
    nextBtn: document.getElementById('next-btn'),
    progressBar: document.getElementById('progress-bar'),
    currentTimeText: document.getElementById('current-time'),
    totalTimeText: document.getElementById('total-time'),
    
    cycleBtn: document.getElementById('cycle-btn'),
    randomBtn: document.getElementById('random-btn'),

    searchInput: document.getElementById('text-input'),

    globalBtn: document.getElementById('open-global-btn'),
    setPlaylistBtn: document.getElementById('open-set-btn'),

    themeBtnGrass: document.getElementById('theme-btn-grass'),
    themeBtnSun: document.getElementById('theme-btn-sun'),
    themeBtnMoon: document.getElementById('theme-btn-moon'),

    accountSettingsBtn: document.getElementById('account-settings-btn'),
    pathSettingsBtn: document.getElementById('path-settings-btn'),
    languageSettingsBtn: document.getElementById('language-settings-btn'),
    themeSettingsBtn: document.getElementById('theme-settings-btn'),

    settingsContentAccounts: document.getElementById('settings-content-accounts'),
    settingsContentPath: document.getElementById('settings-content-path'),
    settingsContentLanguage: document.getElementById('settings-content-language'),
    settingsContentTheme: document.getElementById('settings-content-theme'),
    
    pathSpan: document.getElementById('current-download-path'),
};

// globalState.js
window.Backend = {
    backend: null,
    currentTrackPath: null,
    isPlaying: false,
    playerOriginalHeight: null,
    setMode: false,
    selectedPlaylists: new Set(),
    cycleMode: 0
};

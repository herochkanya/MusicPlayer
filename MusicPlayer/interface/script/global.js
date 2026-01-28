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
    themeBtnDrakula: document.getElementById('theme-btn-drakula'),
    themeBtnGreentea: document.getElementById('theme-btn-greentea'),
    themeBtnDark: document.getElementById('theme-btn-dark'),
    themeBtnCustom: document.getElementById('theme-btn-custom'),    
    liteThemeToggle: document.getElementById('lite-toggle'),
    screenAnimationToggle: document.getElementById('screen-animation-toggle'),
    coverAnimationToggle: document.getElementById('cover-animation-toggle'),
    pulseAnimationToggle: document.getElementById('pulse-animation-toggle'),
    coverSelect: document.getElementById('cover-select'),
    setCoverBtn: document.getElementById('set-cover-btn'),

    pathSettingsBtn: document.getElementById('path-settings-btn'),
    languageSettingsBtn: document.getElementById('language-settings-btn'),
    themeSettingsBtn: document.getElementById('theme-settings-btn'),
    shortcutSettingsBtn: document.getElementById('shortcut-settings-btn'),
    shortcutEqualizerBtn: document.getElementById('shortcut-equalizer-btn'),

    settingsContentPath: document.getElementById('settings-content-path'),
    settingsContentLanguage: document.getElementById('settings-content-language'),
    settingsContentTheme: document.getElementById('settings-content-theme'),
    settingsContentShortcut: document.getElementById('settings-content-shortcut'),
    settingsContentEqualizer: document.getElementById('settings-content-equalizer'),
    
    pathSpan: document.getElementById('current-download-path'),

    shortcutPause: document.getElementById('shortcut-pause'),
    shortcutNext: document.getElementById('shortcut-next'),
    shortcutPrev: document.getElementById('shortcut-prev'),
    shortcutPauseChangeBtn: document.getElementById('shortcut-btn-pause'),
    shortcutNextChangeBtn: document.getElementById('shortcut-btn-next'),
    shortcutPrevChangeBtn: document.getElementById('shortcut-btn-prev'),
    shortcutTray: document.getElementById('tray-mode-toggle'),
};

// globalState.js
window.Backend = {
    backend: null,
    currentTrackPath: null,
    isPlaying: false,
    playerOriginalHeight: null,
    setMode: false,
    selectedPlaylists: new Set(),
    cycleMode: 0,
    currentBaseTheme: "dark", 
    isLiteMode: false
};

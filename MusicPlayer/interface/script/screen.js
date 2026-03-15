// screen.js

document.addEventListener('DOMContentLoaded', () => {
    // ==== Screen switching ====
    UI.switchDownloaderPlayerBtn.addEventListener('click', () => {
        if (UI.downloaderScreen.classList.contains('active') === false) {
            toggleDownloader(true);
            UI.switchDownloaderPlayerBtn.textContent = '🎵';
        }
        else {
            toggleDownloader(false);
            UI.switchDownloaderPlayerBtn.textContent = '⭳';
            showScreen('player-screen');
        }
    });
        
    UI.openSettingsBtn.addEventListener('click', () => {
        if (UI.settingsScreen.classList.contains('active') === false) {
            toggleDownloader(false);
            toggleSettings(true);
            UI.switchDownloaderPlayerBtn.style.visibility = 'hidden';
            UI.openSettingsBtn.textContent = '🔙';
        }
        else {
            toggleSettings(false);
            UI.switchDownloaderPlayerBtn.style.visibility = 'visible';
            UI.openSettingsBtn.textContent = '⚙️';
            showScreen('player-screen');
        }
    });
    showScreen('player-screen');

    // Function to clean inputs after swithing screens
    function resetSearchInputs() {
        UI.searchInput.value = '';
        UI.folderInput.value = '';

        const event = new Event('input');
        UI.searchInput.dispatchEvent(event);
        UI.folderInput.dispatchEvent(event);
    }

    // Function to switch between screens with animation
    function showScreen(id) {
        [UI.downloaderScreen, UI.playerScreen, UI.settingsScreen].forEach(screen => {
            screen.classList.remove('active');
        });
        const activeScreen = document.getElementById(id);
        activeScreen.style.display = 'flex';
        setTimeout(() => activeScreen.classList.add('active'), 10);
    }

    // Function to toggle downloader screen with animation
    function toggleDownloader(show) {
        if (show) {
            if (!Backend.playerOriginalHeight)
                Backend.playerOriginalHeight = UI.playerScreen.offsetHeight;

            UI.playerScreen.style.display = 'none';

            UI.downloaderScreen.style.display = 'flex';
            setTimeout(() => UI.downloaderScreen.classList.add('active'), 10);
        } else {
            UI.downloaderScreen.classList.remove('active');
            setTimeout(() => {
                UI.downloaderScreen.style.display = 'none';
                UI.playerScreen.style.transition = 'all 0.6s ease';
            }, 400);
        }
        resetSearchInputs()
    }

    // Function to toggle settings screen with animation
    function toggleSettings(show) {
        if (show) {
            if (!Backend.playerOriginalHeight)
                Backend.playerOriginalHeight = UI.playerScreen.offsetHeight;

            UI.playerScreen.style.display = 'none';

            UI.settingsScreen.style.display = 'flex';
            setTimeout(() => UI.settingsScreen.classList.add('active'), 10);
        } else {
            UI.settingsScreen.classList.remove('active');
            setTimeout(() => {
                UI.settingsScreen.style.display = 'none';
                UI.playerScreen.style.transition = 'all 0.6s ease';
            }, 400);
        }
    }

    // Settings subsections
    UI.pathSettingsBtn.addEventListener('click', () => {
        [UI.settingsContentPath, UI.settingsContentLanguage, 
            UI.settingsContentTheme, UI.settingsContentShortcut, 
            UI.settingsContentEqualizer].forEach(sec => sec.style.display = 'none');
        UI.settingsContentPath.style.display = 'flex';
    });
    UI.languageSettingsBtn.addEventListener('click', () => {
        [UI.settingsContentPath, UI.settingsContentLanguage, 
            UI.settingsContentTheme, UI.settingsContentShortcut, 
            UI.settingsContentEqualizer].forEach(sec => sec.style.display = 'none');
        UI.settingsContentLanguage.style.display = 'flex';
    });
    UI.themeSettingsBtn.addEventListener('click', () => {
        [UI.settingsContentPath, UI.settingsContentLanguage, 
            UI.settingsContentTheme, UI.settingsContentShortcut, 
            UI.settingsContentEqualizer].forEach(sec => sec.style.display = 'none');
        UI.settingsContentTheme.style.display = 'flex';
    });
    UI.shortcutSettingsBtn.addEventListener('click', () => {
        [UI.settingsContentPath, UI.settingsContentLanguage, 
            UI.settingsContentTheme, UI.settingsContentShortcut, 
            UI.settingsContentEqualizer].forEach(sec => sec.style.display = 'none');
        UI.settingsContentShortcut.style.display = 'flex';
    });
    UI.shortcutEqualizerBtn.addEventListener('click', () => {
        [UI.settingsContentPath, UI.settingsContentLanguage, 
            UI.settingsContentTheme, UI.settingsContentShortcut, 
            UI.settingsContentEqualizer].forEach(sec => sec.style.display = 'none');
        UI.settingsContentEqualizer.style.display = 'flex';
    });
    UI.pathSettingsBtn.click(); // Show accounts section by default

    // Lyrics switch
    UI.lyricsBtn.addEventListener('click', () => {
        const isLyricsHidden = UI.lyricsPanel.classList.contains('hide');
        const contentPanel = document.querySelector('.player-screen-content');
        const folderSection = document.querySelector('.player-screen-folder');
        const trackListSection = document.getElementById('track-list');
        const lyricsPanel = document.getElementById('lyrics-panel');

        const isLyricsVisible = lyricsPanel.classList.contains('active-panel');

        if (!isLyricsVisible) {
            contentPanel.style.display = 'flex';
            folderSection.style.display = 'none';
            trackListSection.style.display = 'none';
            lyricsPanel.style.display = 'block';
            lyricsPanel.classList.add('active-panel');
            UI.lyricsBtn.classList.add('active');
        } else {
            folderSection.style.display = 'flex';
            trackListSection.style.display = 'block';
            lyricsPanel.style.display = 'none';
            lyricsPanel.classList.remove('active-panel');
            UI.lyricsBtn.classList.remove('active');
            Backend.backend.is_fullscreen_mode().then(isFS => {
                if (isFS) {
                    contentPanel.style.display = 'none';
                }
            });
        }
    });

    UI.fullscreenBtn.addEventListener('click', () => {
        Backend.backend.toggle_frameless_mode().then(isFrameless => {
            const contentPanel = document.querySelector('.player-screen-content');
            const upperPanel = document.querySelector('header');
            
            if (isFrameless) {
                contentPanel.style.display = 'none';
                upperPanel.style.display = 'none';
            } else {
                contentPanel.style.display = 'flex';
                upperPanel.style.display = 'flex';
            }
        });
    });
});

    
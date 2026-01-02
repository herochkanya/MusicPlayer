// screen.js

document.addEventListener('DOMContentLoaded', () => {
    // ==== Screen switching ====
    UI.switchDownloaderPlayerBtn.addEventListener('click', () => {
        if (UI.downloaderScreen.classList.contains('active')) {
            toggleDownloader(false);
            UI.switchDownloaderPlayerBtn.textContent = '⭳';}
        else {
            toggleDownloader(true);
            UI.switchDownloaderPlayerBtn.textContent = '🎵';}
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

            UI.playerScreen.style.display = 'flex';
            UI.playerScreen.style.transition = 'all 0.6s ease';
            UI.playerScreen.style.transform = 'scale(0.9)';
            UI.playerScreen.style.opacity = '0.5';
            UI.playerScreen.style.pointerEvents = 'none';

            UI.downloaderScreen.style.display = 'flex';
            setTimeout(() => UI.downloaderScreen.classList.add('active'), 10);
        } else {
            UI.downloaderScreen.classList.remove('active');
            setTimeout(() => {
                UI.downloaderScreen.style.display = 'none';
                UI.playerScreen.style.transition = 'all 0.6s ease';
                UI.playerScreen.style.transform = 'scale(1)';
                UI.playerScreen.style.opacity = '1';
                UI.playerScreen.style.pointerEvents = 'auto';
            }, 400);
        }
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
    UI.accountSettingsBtn.addEventListener('click', () => {
        [UI.settingsContentAccounts, UI.settingsContentPath, UI.settingsContentLanguage, 
            UI.settingsContentTheme].forEach(sec => sec.style.display = 'none');
        UI.settingsContentAccounts.style.display = 'flex';
    });
    UI.pathSettingsBtn.addEventListener('click', () => {
        [UI.settingsContentAccounts, UI.settingsContentPath, UI.settingsContentLanguage, 
            UI.settingsContentTheme].forEach(sec => sec.style.display = 'none');
        UI.settingsContentPath.style.display = 'flex';
    });
    UI.languageSettingsBtn.addEventListener('click', () => {
        [UI.settingsContentAccounts, UI.settingsContentPath, UI.settingsContentLanguage, 
            UI.settingsContentTheme].forEach(sec => sec.style.display = 'none');
        UI.settingsContentLanguage.style.display = 'flex';
    });
    UI.themeSettingsBtn.addEventListener('click', () => {
        [UI.settingsContentAccounts, UI.settingsContentPath, UI.settingsContentLanguage, 
            UI.settingsContentTheme].forEach(sec => sec.style.display = 'none');
        UI.settingsContentTheme.style.display = 'flex';
    });
    UI.accountSettingsBtn.click(); // Show accounts section by default
});

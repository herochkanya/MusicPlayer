// buttons.js

document.addEventListener('DOMContentLoaded', () => {
        // ==== Other buttons ====

    // Cycle mode: 0 - no cycle, 1 - cycle all, 2 - cycle one
    UI.cycleBtn.addEventListener('click', () => {
        Backend.cycleMode = (Backend.cycleMode + 1) % 3;
        switch (Backend.cycleMode) {
            case 0:
                UI.cycleBtn.textContent = '→';
                Backend.backend.set_cycle_mode(0);
                break;
            case 1:
                UI.cycleBtn.textContent = '⇄';
                Backend.backend.set_cycle_mode(1);
                break;
            case 2:
                UI.cycleBtn.textContent = '⥁';
                Backend.backend.set_cycle_mode(2);
                break;
        }
    });

    // Shuffle toggle
    function refreshTrackList(tracks) {
        UI.trackList.innerHTML = '';

        requestAnimationFrame(() => {
            populateTracks(tracks);
            if (Backend.currentTrackPath) {
                markPlaying(Backend.currentTrackPath);
            }
        });
    }

    UI.randomBtn.addEventListener('click', () => {
        Backend.backend.toggle_shuffle().then(shuffle_on => {
            Backend.backend.get_playlist().then(tracks => {
                refreshTrackList(tracks);
                UI.randomBtn.textContent = shuffle_on ? '🔀' : '🎵';
            });
        });
    });

    // Global playlist button
    UI.globalBtn.addEventListener('click', () => {
        Array.from(UI.folderSelect.children).forEach(child => child.classList.remove('selected'));
        UI.globalBtn.classList.add('selected');
        Backend.backend.set_global_playlist().then(tracks => populateTracks(tracks));
    });

    // Search input filtering
    UI.searchInput.addEventListener('input', () => {
        const query = UI.searchInput.value.trim().toLowerCase();
        Array.from(UI.trackList.children).forEach(div => {
            const title = div.querySelector('span')?.textContent.toLowerCase() || '';
            div.style.display = title.includes(query) ? '' : 'none';
        });
    });

    // Set playlist button
    UI.setPlaylistBtn.addEventListener('click', () => {
        if (Backend.setMode) {
            Backend.setMode = false;
            UI.setPlaylistBtn.classList.remove('active');

            const selected = Array.from(Backend.selectedPlaylists);
            Backend.selectedPlaylists.clear();

            if (selected.length > 0) {
                Backend.backend.create_temp_playlist(selected).then(tracks => {
                    populateTracks(tracks);
                });
            }

            document.querySelectorAll('.playlist-item.selected-set')
                .forEach(el => el.classList.remove('selected-set'));

        } else {
            Backend.setMode = true;
            UI.setPlaylistBtn.classList.add('active');
            Backend.selectedPlaylists.clear();
        }
    });

    // Start download button
    UI.startDownloadBtn.addEventListener('click', () => {
        const url = UI.urlInput.value.trim();
        const folder = UI.folderInput.value.trim() || 'downloads';
        if (!url) return UI.debugLog.textContent += 'Please enter a URL!\n';
        UI.debugLog.textContent += `Download started... \nIt'll take a couple of minutes.\n`;
        Backend.backend.start_download(url, folder);
    });
});
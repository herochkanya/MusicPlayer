// buttons.js

const MAX_LINES = 20;

document.addEventListener('DOMContentLoaded', () => {
        // ==== Other buttons ====

    // Cycle mode: 0 - no cycle, 1 - cycle all, 2 - cycle one
    UI.cycleBtn.addEventListener('click', () => {
        Backend.cycleMode = (Backend.cycleMode + 1) % 3;
        switch (Backend.cycleMode) {
            case 0:
                UI.cycleBtn.textContent = '➜';
                Backend.backend.set_cycle_mode(0);
                break;
            case 1:
                UI.cycleBtn.textContent = '↳↰';
                Backend.backend.set_cycle_mode(1);
                break;
            case 2:
                UI.cycleBtn.textContent = '⟳';
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
                UI.randomBtn.textContent = shuffle_on ? '⤭' : '⇉';
            });
        });
    });

    // Global playlist button
    UI.globalBtn.addEventListener('click', () => {
        Array.from(UI.folderSelect.children).forEach(child => child.classList.remove('selected'));
        UI.globalBtn.classList.add('selected');
        Backend.backend.set_global_playlist().then(tracks => populateTracks(tracks));
    });

    // Search input filtering for both Tracks and Folders
    UI.searchInput.addEventListener('input', () => {
        const query = UI.searchInput.value.trim().toLowerCase();
        const trackItems = Array.from(UI.trackList.children);
        const folderContainers = [UI.foldersList, UI.folderSelect];
        
        // Track
        trackItems.forEach(div => {
            if (div.classList.contains('album-separator')) return;

            const content = div.textContent.toLowerCase();
            const album = div.dataset.album ? div.dataset.album.toLowerCase() : '';

            const isVisible = content.includes(query) || album.includes(query);
            div.style.display = isVisible ? '' : 'none';
        });

        // Album
        let lastHeader = null;
        let hasVisibleTracksInAlbum = false;

        trackItems.forEach(div => {
            if (div.classList.contains('album-separator')) {
                if (lastHeader && !hasVisibleTracksInAlbum) {
                    lastHeader.style.display = 'none';
                }
                lastHeader = div;
                lastHeader.style.display = ''; 
                hasVisibleTracksInAlbum = false;
            } else if (div.style.display !== 'none') {
                hasVisibleTracksInAlbum = true;
            }
        });
        
        if (lastHeader && !hasVisibleTracksInAlbum) {
            lastHeader.style.display = 'none';
        }

        // Folders
        folderContainers.forEach(container => {
            if (container) {
                Array.from(container.children).forEach(folderDiv => {
                    const folderName = folderDiv.textContent.toLowerCase();
                    
                    if (folderName.includes(query)) {
                        folderDiv.style.display = ''; 
                    } else {
                        folderDiv.style.display = 'none';
                    }
                });
            }
        });
    });

    UI.folderInput.addEventListener('input', () => {
        const query = UI.folderInput.value.trim().toLowerCase();
        const folderContainers = [UI.foldersList, UI.folderSelect];

        // Folders filtrating
        folderContainers.forEach(container => {
            if (container) {
                Array.from(container.children).forEach(folderDiv => {
                    const folderName = folderDiv.textContent.toLowerCase();
                    
                    if (folderName.includes(query)) {
                        folderDiv.style.display = ''; 
                    } else {
                        folderDiv.style.display = 'none';
                    }
                });
            }
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
});
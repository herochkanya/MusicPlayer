// folders.js

// ==== UI Interactions ====
// Populate folders and tracks
function populateFolders(folders) {
    UI.foldersList.innerHTML = '';
    folders.forEach(folder => {
        const div = document.createElement('div');
        div.textContent = folder;
        div.addEventListener('click', () => {
            Array.from(UI.foldersList.children).forEach(child => child.classList.remove('selected'));
            div.classList.add('selected');
            UI.folderInput.value = folder;
        });
        UI.foldersList.appendChild(div);
    });
}

function populateTracks(tracks) {
    UI.trackList.innerHTML = '';
    let lastAlbum = null;

    tracks.forEach(track => {
        const currentAlbum = track.album || 'Unknown Album';
        if (currentAlbum !== lastAlbum) {
            const albumHeader = document.createElement('div');
            albumHeader.classList.add('album-separator');
            albumHeader.innerHTML = `<span>${currentAlbum}</span>`;
            UI.trackList.appendChild(albumHeader);
            lastAlbum = currentAlbum;
        }

        const div = document.createElement('div');
        div.classList.add('track-item');
        div.dataset.path = track.path;
        div.dataset.album = (track.album || '').toLowerCase();
        const cover = track.cover_path 
            ? `<img src="${track.cover_path.startsWith('file://') ? track.cover_path : 'file://' + track.cover_path}" 
                    style="width:3rem;height:3rem;margin-right:0.5rem;border-radius:0.5rem;vertical-align:middle;">` 
            : '';
        div.innerHTML = `${cover} <span>${track.title || '—'} — ${track.artist || '—'}</span>`;

        div.addEventListener('click', () => {
            Backend.backend.play_track(track.path).then(info => {
                if (info) {
                    updateTrackInfo(info);
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
        UI.trackList.appendChild(div);
    });

    if (Backend.currentTrackPath) markPlaying(Backend.currentTrackPath);
}

// Update track info display
function updateTrackInfo(track) {
    UI.trackCover.classList.remove('rotating', 'reset');
    UI.trackCover.style.transform = 'rotate(0deg)';
    UI.trackTitle.textContent = track.title || '—';
    UI.trackArtist.textContent = track.artist || '—';
    UI.trackCover.classList.add('change');
    setTimeout(() => {
        UI.trackCover.src = track.cover_path 
            ? (track.cover_path.startsWith('file://') ? track.cover_path : 'file://' + track.cover_path)
            : '';
        UI.trackCover.classList.remove('change');
    }, 300);
    loadLyrics(track.path);
}

// Highlight currently playing track
function markPlaying(path) {
    Array.from(UI.trackList.children).forEach(div => div.classList.remove('playing'));
    if (!path) return;
    const el = Array.from(UI.trackList.children).find(div => div.dataset.path === path);
    if (el) {
        el.classList.add('playing');
        el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
}

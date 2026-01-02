// settings.js

// ==== Download path management ====

// Open download path on click
UI.pathSpan.addEventListener('click', () => {
    const path = UI.pathSpan.textContent.trim();
    Backend.backend.open_path(path);
});

// Choose new download path
document.getElementById('set-download-path-btn')
    .addEventListener('click', () => {
        Backend.backend.choose_download_path()
        .then(() => {
            Backend.backend.clear_library_index().then(() => {
            Backend.backend.get_folders().then(folders => populateFolders(folders));
            Backend.backend.get_folders().then(folders => {
                UI.folderSelect.innerHTML = '';
                folders.forEach(folder => {
                    const div = document.createElement('div');
                    div.classList.add('playlist-item');
                    div.dataset.name = folder;
                    div.textContent = folder;

                    div.addEventListener('click', (e) => {
                        if (Backend.setMode) {
                            e.preventDefault();
                            e.stopPropagation();
                            if (Backend.selectedPlaylists.has(folder)) {
                                Backend.selectedPlaylists.delete(folder);
                                div.classList.remove('selected-set');
                            } else {
                                Backend.selectedPlaylists.add(folder);
                                div.classList.add('selected-set');
                            }
                            Backend.backend.set_playlist(folder).then(tracks => {
                                populateTracks(tracks);
                            });
                        } else {
                            Array.from(UI.folderSelect.children).forEach(
                                child => child.classList.remove('selected'));
                            div.classList.add('selected');

                            Backend.backend.set_playlist(folder).then(tracks => {
                                populateTracks(tracks);
                            });

                            UI.folderInput.value = folder;
                        }
                    });

                    UI.folderSelect.appendChild(div);
                });
            });
            Backend.backend.get_download_path().then(path => {
                UI.pathSpan.textContent = path;
        });});});
    });

// ==== Theme cycling ====

// Apply theme to document
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

// Theme button event listeners
[UI.themeBtnGrass, UI.themeBtnMoon, UI.themeBtnSun].forEach(btn => {
    btn.addEventListener('click', () => {
        const theme = btn.dataset.theme;
        applyTheme(theme);

        [UI.themeBtnGrass, UI.themeBtnMoon, UI.themeBtnSun].forEach(b => 
            b.classList.toggle('active-theme', b === btn)
        );

        Backend.backend.set_theme(theme);
    });
});

// ==== Language selection ====

document.getElementById("set-language-btn").addEventListener("click", () => {
    const lang = document.getElementById("language-select").value;
    Backend.backend.set_language(lang);
});
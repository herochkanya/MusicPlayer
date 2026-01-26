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

function applyTheme(theme) {
    if (theme) Backend.currentBaseTheme = theme;
    let finalTheme = Backend.currentBaseTheme;
    if (Backend.isLiteMode) {
        finalTheme += "_lite";
    }
    
    document.documentElement.setAttribute('data-theme', finalTheme);
}

// Lite theme toggle
UI.liteThemeToggle.addEventListener('change', (e) => {
    Backend.isLiteMode = e.target.checked;
    Backend.backend.set_lite_mode(Backend.isLiteMode);
    applyTheme(Backend.currentBaseTheme);
});

// Theme button event listeners
[UI.themeBtnGrass, UI.themeBtnMoon, UI.themeBtnSun, UI.themeBtnDrakula,
    UI.themeBtnGreentea, UI.themeBtnDark
].forEach(btn => {
    btn.addEventListener('click', () => {
        const theme = btn.dataset.theme;
        applyTheme(theme);

        [UI.themeBtnGrass, UI.themeBtnMoon, UI.themeBtnSun, UI.themeBtnDrakula,
            UI.themeBtnGreentea, UI.themeBtnDark
        ].forEach(b => 
            b.classList.toggle('active-theme', b === btn)
        );

        Backend.backend.set_theme(theme);
    });
});

UI.themeBtnCustom.addEventListener('click', async () => {
    const path = await Backend.backend.choose_custom_background();
    if (!path) return;

    const cssPath = path.replace(/\\/g, "/"); // Windows → CSS

    document.documentElement.style.setProperty(
        "--custom-bg-image",
        `url("${cssPath}")`
    );

    applyTheme("custom");
    Backend.backend.set_theme("custom");
});

// ==== Language selection ====

document.getElementById("set-language-btn").addEventListener("click", () => {
    const lang = document.getElementById("language-select").value;
    Backend.backend.set_language(lang);
});

// ==== Equalizer settings ====

const sliders = [
  document.getElementById("eq-60"),
  document.getElementById("eq-150"),
  document.getElementById("eq-400"),
  document.getElementById("eq-1000"),
  document.getElementById("eq-2400"),
  document.getElementById("eq-15000"),
];

const path = document.getElementById("eq-path");
const dots = document.querySelectorAll(".eq-dot");
const resetBtn = document.getElementById("reset-equalizer-btn");
const svg = document.getElementById("eq-curve");

const MIN_DB = -12;
const MAX_DB = 12;
const HEIGHT = 160;
const WIDTH = 600;

function dbToY(db) {
  return HEIGHT - ((db - MIN_DB) / (MAX_DB - MIN_DB)) * HEIGHT;
}

function yToDb(y) {
  const ratio = 1 - y / HEIGHT;
  return MIN_DB + ratio * (MAX_DB - MIN_DB);
}

function updateCurve() {
  const values = sliders.map(s => parseFloat(s.value));
  const step = WIDTH / (values.length - 1);

  const pts = values.map((v, i) => ({
    x: i * step,
    y: dbToY(v),
  }));

  dots.forEach((d, i) => {
    d.setAttribute("cx", pts[i].x);
    d.setAttribute("cy", pts[i].y);
  });

  let d = `M ${pts[0].x} ${pts[0].y}`;
  for (let i = 1; i < pts.length; i++) {
    const prev = pts[i - 1];
    const cur = pts[i];
    const cx = (prev.x + cur.x) / 2;
    d += ` C ${cx} ${prev.y}, ${cx} ${cur.y}, ${cur.x} ${cur.y}`;
  }

  path.setAttribute("d", d);
  saveEqSettings();
}

let activeDot = null;

dots.forEach((dot, index) => {
  dot.addEventListener("pointerdown", e => {
    activeDot = index;
    svg.setPointerCapture(e.pointerId);
  });
});

svg.addEventListener("pointermove", e => {
  if (activeDot === null) return;

  const rect = svg.getBoundingClientRect();
  let y = e.clientY - rect.top;
  y = Math.max(0, Math.min(HEIGHT, y));

  const db = Math.round(yToDb(y));
  sliders[activeDot].value = db;
  updateCurve();
});

svg.addEventListener("pointerup", () => activeDot = null);
svg.addEventListener("pointerleave", () => activeDot = null);


resetBtn.addEventListener("click", () => {
  sliders.forEach(s => s.value = 0);
  updateCurve();
});

function saveEqSettings() {
    const eq = {
        "60": parseFloat(sliders[0].value),
        "150": parseFloat(sliders[1].value),
        "400": parseFloat(sliders[2].value),
        "1000": parseFloat(sliders[3].value),
        "2400": parseFloat(sliders[4].value),
        "15000": parseFloat(sliders[5].value),
    };
    Backend.backend.set_equalizer_settings(eq);
}

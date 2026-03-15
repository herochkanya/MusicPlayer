// downloader.js

/**
 * Creates a new URL input row and appends it to the list
 * @param {string} value - Initial URL value (optional)
 */
function addUrlRow(value = "") {
    const row = document.createElement('div');
    row.className = 'url-input-row'; // Use class for styling
    row.style.display = 'flex';
    row.style.flexDirection = 'row';
    row.style.alignItems = 'baseline';
    row.style.marginBottom = '5px';

    row.innerHTML = `
        <button class="emoji-button remove-url-btn" style="font-size: 1rem; width: 2.6vw;">🗑️</button>
        <input type="text" class="url-field" data-i18n-placeholder="downloader.url" value="${value}" />
    `;

    // Handle row removal
    row.querySelector('.remove-url-btn').addEventListener('click', () => {
        // Keep at least one input field
        if (document.querySelectorAll('.url-field').length > 1) {
            row.remove();
        } else {
            row.querySelector('.url-field').value = '';
        }
    });

    UI.urlListContainer.appendChild(row);
    
    // Apply translations to the new placeholder
    if (window.applyTranslations) applyTranslations();
}

/**
 * Collects all URLs from the input fields
 * @returns {string[]} Array of non-empty URLs
 */
function getDownloadQueue() {
    return Array.from(document.querySelectorAll('.url-field'))
        .map(input => input.value.trim())
        .filter(url => url !== "");
}



// Start download button
UI.startDownloadBtn.addEventListener('click', () => {
    const urls = getDownloadQueue();
    const folder = UI.folderInput.value.trim() || 'downloads';

    if (urls.length === 0) {
        UI.debugLog.textContent = "❌ No URLs to download!";
        return;
    }

    UI.debugLog.textContent = "🚀 Starting queue...";
    Backend.backend.start_queue_download(urls, folder);
});
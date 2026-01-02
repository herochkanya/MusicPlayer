// i18n.js - Internationalization module

let TRANSLATIONS = {};
let CURRENT_LANG = "en";

async function loadLanguage(lang) {
    const res = await fetch(`locales/${lang}.json`);
    TRANSLATIONS = await res.json();
    CURRENT_LANG = lang;
    applyTranslations();
}

function t(key) {
    return TRANSLATIONS[key] || key;
}

function applyTranslations() {
    document.querySelectorAll("[data-i18n]").forEach(el => {
        el.textContent = t(el.dataset.i18n);
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
        el.placeholder = t(el.dataset.i18nPlaceholder);
    });
}

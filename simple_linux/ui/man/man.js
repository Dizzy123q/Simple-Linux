let panelOpen = false;
let lastSelectedText = '';
let lastTranslatedText = '';

window.addEventListener('pywebviewready', async () => {

    // Citim query din URL
    const params = new URLSearchParams(window.location.search);
    const query = params.get('query') || '';

    document.getElementById('manTitle').textContent = query;
    document.title = `Man — ${query}`;

    document.getElementById('backBtn').addEventListener('click', () => {
        window.pywebview.api.navigate('main');
    });

    document.getElementById('translateBtn').addEventListener('click', () => {
        onTranslate();
    });

    // Shortcut Ctrl+T
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 't') {
            e.preventDefault();
            onTranslate();
        }
    });

    await loadManPage(query);
});


async function loadManPage(query) {
    const content = document.getElementById('manContent');
    const spinner = document.getElementById('spinnerWrap');

    spinner.style.display = 'flex';

    const result = await window.pywebview.api.get_man_page(query);

    content.innerHTML = '';

    if (!result.success) {
        const err = document.createElement('p');
        err.className = 'man-paragraph text-muted';
        err.textContent = result.error;
        content.appendChild(err);
        return;
    }

    result.sections.forEach(section => {
        const titleEl = document.createElement('p');
        titleEl.className = 'man-section-title';
        titleEl.textContent = section.title;
        content.appendChild(titleEl);

        const contentEl = document.createElement('p');
        contentEl.className = 'man-paragraph';
        contentEl.textContent = section.content;
        content.appendChild(contentEl);
    });
}


function getSelectedText() {
    return window.getSelection().toString().trim();
}


async function onTranslate() {
    const selected = getSelectedText();

    if (!selected) {
        setTranslation('Selectează text înainte de a traduce.');
        openPanel();
        return;
    }

    openPanel();

    // Nu retrimitem același text
    if (selected === lastTranslatedText) return;

    lastTranslatedText = selected;
    setTranslation('Se traduce...');

    const result = await window.pywebview.api.translate(selected);

    if (result.success) {
        setTranslation(result.translation);
    } else {
        setTranslation(`Eroare: ${result.error}`);
    }
}


function openPanel() {
    const panel = document.getElementById('translatePanel');
    if (!panelOpen) {
        panel.classList.add('open');
        panelOpen = true;
    }
}


function closePanel() {
    const panel = document.getElementById('translatePanel');
    panel.classList.remove('open');
    panelOpen = false;
}


function setTranslation(text) {
    document.getElementById('translationText').textContent = text;
}


// Click în afara panoului îl închide
document.addEventListener('click', (e) => {
    const panel = document.getElementById('translatePanel');
    const translateBtn = document.getElementById('translateBtn');
    if (panelOpen && !panel.contains(e.target) && e.target !== translateBtn) {
        closePanel();
    }
});
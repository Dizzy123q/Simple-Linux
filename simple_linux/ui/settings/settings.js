const LANGUAGES = {
    "Română":   "RO",
    "Engleză":  "EN",
    "Franceză": "FR",
    "Germană":  "DE",
    "Spaniolă": "ES",
    "Italiană": "IT",
};

let selectedLang = "RO";

window.addEventListener('pywebviewready', async () => {

    document.getElementById('backBtn').addEventListener('click', () => {
        window.pywebview.api.navigate('main');
    });

    // Show/hide API key
    const apiKeyInput = document.getElementById('apiKeyInput');
    const toggleKeyBtn = document.getElementById('toggleKeyBtn');
    toggleKeyBtn.addEventListener('click', () => {
        const isPassword = apiKeyInput.type === 'password';
        apiKeyInput.type = isPassword ? 'text' : 'password';
        toggleKeyBtn.textContent = isPassword ? 'Hide' : 'Show';
    });

    // Save
    document.getElementById('saveBtn').addEventListener('click', () => {
        onSave();
    });

    // Construim lista de limbi
    buildLangList();

    // Încărcăm config existent
    await loadSettings();
});


function buildLangList() {
    const list = document.getElementById('langList');
    list.innerHTML = '';

    Object.entries(LANGUAGES).forEach(([name, code]) => {
        const item = document.createElement('div');
        item.className = 'lang-item';
        item.dataset.code = code;
        item.innerHTML = `
            <div class="lang-dot"></div>
            <span>${name}</span>
        `;
        item.addEventListener('click', () => selectLang(code));
        list.appendChild(item);
    });
}


function selectLang(code) {
    selectedLang = code;
    document.querySelectorAll('.lang-item').forEach(item => {
        item.classList.toggle('selected', item.dataset.code === code);
    });
}


async function loadSettings() {
    const config = await window.pywebview.api.get_settings();

    document.getElementById('apiKeyInput').value = config.deepl_key || '';
    selectLang(config.target_lang || 'RO');
}


async function onSave() {
    const key = document.getElementById('apiKeyInput').value.trim();

    const result = await window.pywebview.api.save_settings({
        deepl_key: key,
        target_lang: selectedLang,
    });

    const confirmMsg = document.getElementById('confirmMsg');
    confirmMsg.classList.remove('hidden');

    if (result.success) {
        confirmMsg.textContent = '✓ Salvat cu succes.';
        confirmMsg.style.color = 'var(--accent-green)';
    } else {
        confirmMsg.textContent = `✗ Eroare: ${result.error}`;
        confirmMsg.style.color = 'var(--accent-red)';
    }

    setTimeout(() => confirmMsg.classList.add('hidden'), 3000);
}
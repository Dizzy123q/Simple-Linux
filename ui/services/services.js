let currentService = null;
let allCards = [];

window.addEventListener('pywebviewready', async () => {

    document.getElementById('backBtn').addEventListener('click', () => {
        window.pywebview.api.navigate('main');
    });

    document.getElementById('searchBar').addEventListener('input', (e) => {
        filterCards(e.target.value.trim().toLowerCase());
    });

    document.getElementById('manBtn').addEventListener('click', () => {
        if (currentService) {
            window.pywebview.api.navigate('man', { query: currentService });
        }
    });

    await loadServices();
});


async function loadServices() {
    const list = document.getElementById('servicesList');
    const spinner = document.getElementById('spinnerWrap');

    spinner.style.display = 'flex';
    const services = await window.pywebview.api.get_services();
    spinner.style.display = 'none';

    const total = services.length;
    const active = services.filter(s => s.status === 'active').length;
    const failed = services.filter(s => s.status === 'failed').length;

    document.getElementById('statTotal').textContent = total;
    document.getElementById('statActive').textContent = active;
    document.getElementById('statFailed').textContent = failed;

    allCards = [];
    services.forEach(service => {
        const card = createCard(service);
        list.appendChild(card);
        allCards.push({ el: card, name: service.name });
    });
}


function createCard(service) {
    const card = document.createElement('div');
    card.className = 'service-card';

    const dotClass = `dot-${service.status === 'active' ? 'active' : service.status === 'failed' ? 'failed' : 'inactive'}`;

    card.innerHTML = `
        <div class="card-left">
            <div class="status-dot ${dotClass}"></div>
            <span class="service-name">${service.name}</span>
        </div>
        <span class="service-status-text">${service.status}</span>
    `;

    card.addEventListener('click', () => selectService(card, service.name, service.status));
    return card;
}


function filterCards(query) {
    allCards.forEach(({ el, name }) => {
        el.style.display = name.toLowerCase().includes(query) ? '' : 'none';
    });
}


async function selectService(cardEl, name, status) {
    allCards.forEach(({ el }) => el.classList.remove('active-card'));
    cardEl.classList.add('active-card');

    currentService = name;

    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('detailsPanel').classList.remove('hidden');
    document.getElementById('manBlock').classList.add('hidden');

    document.getElementById('detailsName').textContent = name;
    document.getElementById('detailsDesc').textContent = 'Se încarcă...';
    document.getElementById('detailsPid').textContent = '...';

    const badgeEl = document.getElementById('detailsBadge');
    badgeEl.textContent = status;
    badgeEl.className = `status-badge badge-${status === 'active' ? 'active' : status === 'failed' ? 'failed' : 'inactive'}`;

    setCommands(name);

    const result = await window.pywebview.api.get_service_details(name);

    if (result.success) {
        document.getElementById('detailsDesc').textContent = result.description;
        document.getElementById('detailsPid').textContent =
            result.pid && result.pid !== '0' ? result.pid : '—';
    } else {
        document.getElementById('detailsDesc').textContent = result.error;
        document.getElementById('detailsPid').textContent = '—';
    }

    if (result.has_man) {
        document.getElementById('manBlock').classList.remove('hidden');
    }
}


function setCommands(name) {
    const list = document.getElementById('commandsList');
    const commands = [
        `sudo systemctl start ${name}`,
        `sudo systemctl stop ${name}`,
        `sudo systemctl restart ${name}`,
    ];

    list.innerHTML = commands.map(cmd => `
        <div class="cmd-row">
            <span class="cmd-text">${cmd}</span>
            <button class="copy-btn" onclick="copyCmd(this, '${cmd}')">Copy</button>
        </div>
    `).join('');
}


function copyCmd(btn, text) {
    navigator.clipboard.writeText(text);
    btn.textContent = '✓';
    setTimeout(() => btn.textContent = 'Copy', 1500);
}
window.addEventListener('pywebviewready', () => {
    window.pywebview.api.show_window();  

    const input = document.getElementById('mainInput');
    const dashboardBtn = document.getElementById('dashboardBtn');
    const infoBtn = document.getElementById('infoBtn');
    const settingsBtn = document.getElementById('settingsBtn');

    // Placeholder random
    const placeholders = [
        "Scrie o comandă sau un serviciu...",
        "Ce pot să fac pentru tine?",
        "Încearcă: ls, nginx, ssh...",
        "Scrie o comandă...",
    ];
    input.placeholder = placeholders[Math.floor(Math.random() * placeholders.length)];

    // Enter → man page
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const query = input.value.trim();
            if (query) {
                window.pywebview.api.navigate('man', { query });
            }
        }
    });

    // Butoane
    dashboardBtn.addEventListener('click', () => {
        window.pywebview.api.navigate('services');
    });

    infoBtn.addEventListener('click', () => {
        window.pywebview.api.navigate('help');
    });

    settingsBtn.addEventListener('click', () => {
        window.pywebview.api.navigate('settings');
    });

});
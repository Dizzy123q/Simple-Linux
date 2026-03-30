window.addEventListener('pywebviewready', () => {
    document.getElementById('backBtn').addEventListener('click', () => {
        window.pywebview.api.navigate('main');
    });
});

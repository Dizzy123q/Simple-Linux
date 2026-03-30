from simple_linux.logic.services_manager import get_all_services, get_service_details, service_action
from simple_linux.logic.man_parser import get_man_page
from simple_linux.logic.translator import translate
from simple_linux.logic.config import load_config, save_config
import subprocess


class Api:

    # ─── SERVICES ────────────────────────────────────────────

    def get_services(self) -> list:
        return get_all_services()

    def get_service_details(self, name: str) -> dict:
        result = get_service_details(name)
        result["has_man"] = self._has_man(name)
        return result

    def service_action(self, name: str, action: str) -> dict:
        return service_action(name, action)

    # ─── MAN PAGE ────────────────────────────────────────────

    def get_man_page(self, query: str) -> dict:
        return get_man_page(query)

    # ─── TRANSLATE ───────────────────────────────────────────

    def translate(self, text: str) -> dict:
        return translate(text)

    # ─── SETTINGS ────────────────────────────────────────────

    def get_settings(self) -> dict:
        return load_config()

    def save_settings(self, data: dict) -> dict:
        try:
            save_config(data)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ─── NAVIGARE ────────────────────────────────────────────

    def navigate(self, page: str, params: dict = None) -> None:
        import webview
        import urllib.parse

        port = 8765
        pages = {
            "main":     "main/index.html",
            "services": "services/services.html",
            "man":      "man/man.html",
            "settings": "settings/settings.html",
            "help":     "help/help.html",
        }

        if page not in pages:
            return None

        url = f"http://127.0.0.1:{port}/{pages[page]}"

        if params:
            query = urllib.parse.urlencode(params)
            url = f"{url}?{query}"

        window = webview.active_window()
        # Navigăm din JS direct, fără callback
        window.evaluate_js(f"window.location.href = '{url}'")
        self.window.load_url(url) 
        return None
        
    # ─── HELPERS ─────────────────────────────────────────────

    def _has_man(self, name: str) -> bool:
        try:
            result = subprocess.run(
                ["man", "-w", name],
                capture_output=True, text=True, timeout=3
            )
            return result.returncode == 0
        except Exception:
            return False
    
    
    def show_window(self) -> None:
        self.window.show()
        return None

import os
os.environ['PYWEBVIEW_GUI'] = 'qt'

import webview
import threading
import http.server
import functools
import time


def resource_path(relative: str) -> str:
    import sys
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative)


def main():
    from simple_linux.api import Api

    api = Api()

    ui_path = resource_path("ui")
    port = 8765

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=ui_path
    )
    server = http.server.HTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    time.sleep(0.3)

    window = webview.create_window(
        title="Simple Linux",
        url=f"http://127.0.0.1:{port}/main/index.html",
        js_api=api,
        width=900,
        height=650,
        min_size=(700, 500),
        resizable=True,
        background_color='#0f0f0f',
    )

    api.window = window
    webview.start(debug=False)


if __name__ == "__main__":
    main()

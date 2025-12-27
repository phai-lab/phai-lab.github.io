import contextlib
import socket
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
TARGET_HTML = "index.html"
OUT_PNG = ROOT / "preview.png"


def _pick_free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def main() -> None:
    if not (ROOT / TARGET_HTML).exists():
        raise FileNotFoundError(f"Missing {TARGET_HTML} in {ROOT}")

    port = _pick_free_port()

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT), **kwargs)

        def log_message(self, format, *args):  # noqa: A003
            # Keep output clean for scripted use.
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    url = f"http://127.0.0.1:{port}/{TARGET_HTML.replace(' ', '%20')}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(url, wait_until="load", timeout=60_000)
            # Let fonts / sticky header / AOS settle.
            time.sleep(1.5)
            page.screenshot(path=str(OUT_PNG), full_page=True)
            browser.close()
    finally:
        httpd.shutdown()
        httpd.server_close()

    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()




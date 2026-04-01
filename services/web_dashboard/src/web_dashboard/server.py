from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = os.getenv("WEB_DASHBOARD_HOST", "0.0.0.0")
PORT = int(os.getenv("WEB_DASHBOARD_PORT", "4000"))

BASE_DIR = Path(__file__).resolve().parent
# STATIC_DIR = BASE_DIR / "static"
STATIC_DIR = Path("/app/static")


class StaticHandler(BaseHTTPRequestHandler):
    def _send_file(self, path: Path, content_type: str) -> None:
        print(f"[web] serve file: {path}")
        if not path.exists() or not path.is_file():
            print(f"[web] 404 file missing: {path}")
            self.send_error(404, "File not found")
            return

        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path
        print(f"[web] GET {route}")

        if route == "/":
            return self._send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")

        if route == "/metrics-dashboard.js":
            return self._send_file(STATIC_DIR / "metrics-dashboard.js", "application/javascript; charset=utf-8")
        
        if route == "/chart.js":
            return self._send_file(STATIC_DIR / "chart.js", "application/javascript; charset=utf-8")
        
        if route == "/luxon@3":
            return self._send_file(STATIC_DIR / "luxon@3", "application/javascript; charset=utf-8")
        
        if route == "/chartjs-adapter-luxon":
            return self._send_file(STATIC_DIR / "chartjs-adapter-luxon", "application/javascript; charset=utf-8")
        
        self.send_error(404, "Not Found")

    def log_message(self, format: str, *args) -> None:
        return


def run_server(host: str = HOST, port: int = PORT) -> None:
    httpd = HTTPServer((host, port), StaticHandler)
    print(f"Serving web dashboard at http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
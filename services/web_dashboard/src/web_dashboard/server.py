#!/usr/bin/env python3
"""
Минимальный HTTP-сервер для отдачи дашборда.

Запускает статический файловый сервер для веб-интерфейса мониторинга.
Поддерживает CORS для запросов с других доменов.

Запуск:
    python -m web_dashboard.server --host 0.0.0.0 --port 4000
"""

import os
import socketserver
from http.server import SimpleHTTPRequestHandler, HTTPServer
import argparse
from pathlib import Path


class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP‑сервер с CORS для статических файлов."""

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()


def find_static_dir():
    """Ищет папку static относительно server.py."""
    # Ищем static в текущей папке или в src/web_dashboard/static
    candidates = [
        Path(__file__).parent / 'static',
        Path(__file__).parent.parent / 'static',
        Path(__file__).parent / '..' / '..' / 'static'
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return str(candidate.absolute())
    
    raise FileNotFoundError("Не найдена папка static")


def main():
    
    parser = argparse.ArgumentParser(description="Metrics Web Dashboard")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=4000, help='Port to bind')

    args = parser.parse_args()

    # Находим и переходим в static
    static_dir = find_static_dir()
    print(f"Static files found at: {static_dir}")
    
    os.chdir(static_dir)
    print(f"Serving http://{args.host}:{args.port}")
    print("Dashboard available at http://localhost:4000")
    print("Press Ctrl+C to stop")

    with HTTPServer((args.host, args.port), CORSHTTPRequestHandler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
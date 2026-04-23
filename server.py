#!/usr/bin/env python3
"""
Простой HTTP сервер для раздачи Mini App
"""
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PORT = int(os.getenv("PORT", 8080))

class MyHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Убираем query string
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        
        # Если путь начинается с /miniapp/, берём файл из папки miniapp/
        if path.startswith('/miniapp/'):
            # Убираем /miniapp/ из пути
            file_path = path[9:]  # len('/miniapp/') = 9
            full_path = Path('miniapp') / file_path.lstrip('/')
            return str(full_path.resolve())
        
        # Для остальных путей используем стандартную логику
        return super().translate_path(path)

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), MyHandler)
    print(f"🌐 HTTP сервер запущен на порту {PORT}")
    print(f"📂 Маршрут /miniapp/* → папка miniapp/")
    server.serve_forever()

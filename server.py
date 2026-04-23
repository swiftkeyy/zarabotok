#!/usr/bin/env python3
"""
Простой HTTP сервер для раздачи Mini App
"""
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.getenv("PORT", 8080))

class MyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="miniapp", **kwargs)

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), MyHandler)
    print(f"🌐 HTTP сервер запущен на порту {PORT}")
    print(f"📂 Раздаём файлы из папки miniapp/")
    server.serve_forever()

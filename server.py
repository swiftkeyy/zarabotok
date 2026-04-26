#!/usr/bin/env python3
"""
Простой HTTP сервер для раздачи Mini App с проксированием API
"""
import os
import urllib.request
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PORT = int(os.getenv("PORT", 8080))
API_PORT = 8081

class MyHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Убираем query string
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        
        # Админ-панель
        if path == '/admin' or path == '/admin/':
            return str(Path('miniapp/admin.html').resolve())
        
        # Если путь начинается с /miniapp/, берём файл из папки miniapp/
        if path.startswith('/miniapp/'):
            # Убираем /miniapp/ из пути
            file_path = path[9:]  # len('/miniapp/') = 9
            full_path = Path('miniapp') / file_path.lstrip('/')
            return str(full_path.resolve())
        
        # Для остальных путей используем стандартную логику
        return super().translate_path(path)
    
    def do_POST(self):
        # Проксируем POST запросы к API
        if self.path.startswith('/api/'):
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                
                # Читаем multipart данные
                content_type = self.headers.get('Content-Type', '')
                
                # Проксируем на API сервер
                api_url = f'http://localhost:{API_PORT}{self.path}'
                
                req = urllib.request.Request(
                    api_url,
                    data=self.rfile.read(content_length),
                    headers={'Content-Type': content_type},
                    method='POST'
                )
                
                with urllib.request.urlopen(req) as response:
                    self.send_response(response.status)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(response.read())
            
            except Exception as e:
                print(f"Proxy error: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), MyHandler)
    print(f"🌐 HTTP сервер запущен на порту {PORT}")
    print(f"📂 Маршрут /miniapp/* → папка miniapp/")
    print(f"🛠️ Админ-панель доступна на /admin")
    print(f"🔄 Проксирование /api/* → localhost:{API_PORT}")
    server.serve_forever()

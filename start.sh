#!/bin/bash
# Запуск бота, веб-сервера и API одновременно

# Запускаем веб-сервер в фоне
python3 server.py &

# Запускаем API сервер в фоне
python3 api_server.py &

# Запускаем бота
python3 main.py

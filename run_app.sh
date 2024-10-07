#!/bin/bash

# Завершить старый процесс, использующий порт (например, 8000)
PORT=8000
PID=$(lsof -t -i:$PORT)

if [ -n "$PID" ]; then
  echo "Завершаю процесс на порту $PORT (PID: $PID)"
  kill -9 $PID
fi

# Запустить приложение (замените на вашу команду запуска)
echo "Запускаю приложение..."
python3 backend/main.py
chmod +x run_app.sh

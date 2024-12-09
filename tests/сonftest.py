import os
# Добавляем путь к backend, где находятся основные файлы, такие как main.py
import sys

# Добавляем путь к backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Добавляем путь к blockchain, где находится blockchain_func.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'blockchain')))

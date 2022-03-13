import sys

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

if __name__ == '__main__':
    from internal.app import backend_app
    app = backend_app()

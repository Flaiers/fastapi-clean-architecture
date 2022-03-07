import sys

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from internal.app import admin_app as app  # noqa

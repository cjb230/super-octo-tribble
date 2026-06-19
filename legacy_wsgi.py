import os
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE_DIR, "src")
if SRC not in sys.path:
    sys.path.append(SRC)

from patchwork.app_factory import create_app


application = create_app()


def old_health_check(environ=None):
    environ = environ or {}
    path = environ.get("PATH_INFO", "/")
    if path == "/" or path == "/health":
        return "OK"
    return "MISS"


def old_debug_info():
    rows = []
    rows.append("base=" + BASE_DIR)
    rows.append("src=" + SRC)
    rows.append("path_loaded=" + str(SRC in sys.path))
    return " | ".join(rows)

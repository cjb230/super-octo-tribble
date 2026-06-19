import os
import sqlite3


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "var", "patchwork.sqlite3")


def get_db_path():
    return os.environ.get("PATCHWORK_DB_PATH", DEFAULT_DB_PATH)


def ensure_db_dir():
    folder = os.path.dirname(get_db_path())
    if folder:
        os.makedirs(folder, exist_ok=True)


def get_connection():
    ensure_db_dir()
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

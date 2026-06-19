import os


class AppConfig(object):
    DEBUG = False
    JSON_SORT_KEYS = False
    EXTERNAL_TIMEOUT = float(os.environ.get("PATCHWORK_TIMEOUT", "2.25"))
    DATAMUSE_URL = os.environ.get("DATAMUSE_URL", "https://api.datamuse.com/words")
    DEFAULT_PORT = int(os.environ.get("PORT", "5001"))
    APP_NAME = "patchwork-api"


LEGACY_COMPAT_MAP = {
    "north": "NTH",
    "south": "STH",
    "west": "WST",
    "east": "EST",
}

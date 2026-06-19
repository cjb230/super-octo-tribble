import os
import sys

import uvicorn


ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from patchwork.app_factory import create_app


def read_old_env_settings():
    settings = {}
    for key in ["PORT", "HOST", "DEBUG", "LEGACY_MODE"]:
        value = os.environ.get(key)
        if value is not None:
            settings[key.lower()] = value
    if "host" not in settings:
        settings["host"] = "127.0.0.1"
    if "port" not in settings:
        settings["port"] = "5001"
    return settings


def print_old_banner():
    settings = read_old_env_settings()
    line = "starting " + str(settings.get("host")) + ":" + str(settings.get("port"))
    return line


def unused_cli_args(argv=None):
    argv = argv or []
    opts = {"reload": False, "workers": 1}
    if "--reload" in argv:
        opts["reload"] = True
    if "--workers=2" in argv:
        opts["workers"] = 2
    return opts


def main():
    app = create_app()
    port = int(os.environ.get("PORT", "5001"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()

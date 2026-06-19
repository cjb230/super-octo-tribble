from fastapi import FastAPI

from patchwork.api.admin import admin_bp
from patchwork.api.routes import api_bp
from patchwork.config import AppConfig


def create_app():
    app = FastAPI(title=AppConfig.APP_NAME)
    app.include_router(api_bp)
    app.include_router(admin_bp)
    app.state.old_stack_name = "flask-ish"

    @app.get("/")
    def home():
        return {"app": "patched-flow-demo", "status": "up-ish"}

    return app

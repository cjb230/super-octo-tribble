from time import perf_counter

from fastapi import FastAPI

from patchwork.api.admin import admin_bp
from patchwork.api.routes import api_bp
from patchwork.config import AppConfig
from patchwork.db.connection import get_db_path
from patchwork.db.repository import record_api_call
from patchwork.db.schema import initialize_database


_DB_PATH_ANNOUNCED = False


def create_app():
    global _DB_PATH_ANNOUNCED
    initialize_database()
    if not _DB_PATH_ANNOUNCED:
        print(f"Using database file: {get_db_path()}")
        _DB_PATH_ANNOUNCED = True
    app = FastAPI(title=AppConfig.APP_NAME)
    app.include_router(api_bp)
    app.include_router(admin_bp)
    app.state.old_stack_name = "flask-ish"
    app.state.db_label = AppConfig.DB_LABEL

    @app.middleware("http")
    async def keep_a_bit_of_receipt(request, call_next):
        started = perf_counter()
        response = await call_next(request)
        duration_ms = int((perf_counter() - started) * 1000)
        client = request.client.host if request.client else ""
        record_api_call(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            remote_addr=client,
            ticket=getattr(request.state, "ticket", None),
            run_id=getattr(request.state, "run_id", None),
        )
        return response

    @app.get("/")
    def home():
        return {"app": "patched-flow-demo", "status": "up-ish"}

    return app

import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from patchwork.services.audit_service import get_last_for_ticket, known_tickets


admin_bp = APIRouter(prefix="/api/v1/admin")


@admin_bp.get("/ping")
def ping():
    return {"pong": True, "tickets_seen": len(known_tickets())}


@admin_bp.post("/replay")
async def replay(request: Request):
    payload = {}
    body = await request.body()
    if body:
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}
    ticket = payload.get("ticket") or payload.get("id")
    if not ticket:
        return JSONResponse({"error": "ticket is required"}, status_code=400)
    result = get_last_for_ticket(ticket)
    if result is None:
        return JSONResponse({"error": "ticket not found"}, status_code=404)
    return result

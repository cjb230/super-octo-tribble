import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from patchwork.models.envelope import MessageEnvelope
from patchwork.parsers.normalizer import normalize_payload
from patchwork.parsers.oddtext import parse_weird_text
from patchwork.services.audit_service import remember_result
from patchwork.services.flag_service import build_flags
from patchwork.services.meaning_service import shift_meaning


api_bp = APIRouter(prefix="/api/v1")


EXAMPLES = {
    "basic": "META:: ticket=>A-100 ;; source=>fax ;; region=>north\nWORDS:: raw=>customer says package late and needs rapid lane ;; tone=>angry\nFACTS:: amount=>1450 ;; retry=>yes ;; vip=>no",
    "happy": "META:: ticket=>B-222 ;; source=>portal ;; region=>south\nWORDS:: raw=>client asks for quick change and says thanks ;; tone=>calm\nFACTS:: amount=>40 ;; retry=>no ;; vip=>yes",
}


async def _read_raw_text(request):
    payload = {}
    body = await request.body()
    if body:
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}
    if isinstance(payload, dict) and payload.get("raw_text"):
        return payload.get("raw_text"), payload
    text_body = body.decode("utf-8") if body else ""
    return text_body, payload


@api_bp.get("/health")
def health():
    return {"ok": True, "service": "patchwork", "version": "v1"}


@api_bp.get("/examples/{name}")
def get_example(name):
    example = EXAMPLES.get(name)
    if example is None:
        return JSONResponse({"error": "example not found", "known": sorted(EXAMPLES.keys())}, status_code=404)
    return {"name": name, "raw_text": example}


async def preview_transform(request: Request):
    raw_text, payload = await _read_raw_text(request)
    if not raw_text:
        return JSONResponse({"error": "raw_text is required"}, status_code=400)

    parsed = parse_weird_text(raw_text)
    normalized = normalize_payload(parsed, payload)
    envelope = MessageEnvelope.from_parts(raw_text, normalized)
    meaning = shift_meaning(envelope.to_dict())
    return {
        "ticket": envelope.ticket,
        "preview": meaning.get("shifted_text", ""),
        "swaps": meaning.get("word_swaps", []),
    }


@api_bp.post("/transform")
async def transform(request: Request):
    raw_text, payload = await _read_raw_text(request)
    if not raw_text:
        return JSONResponse({"error": "raw_text is required"}, status_code=400)

    parsed = parse_weird_text(raw_text)
    normalized = normalize_payload(parsed, payload)
    envelope = MessageEnvelope.from_parts(raw_text, normalized)
    meaning = shift_meaning(envelope.to_dict())
    flags = build_flags(meaning)

    final_doc = {
        "input": envelope.to_dict(),
        "meaning": meaning,
        "flags": flags,
    }
    stored = remember_result(final_doc, endpoint_name="transform")
    request.state.run_id = stored.get("run_id")
    request.state.ticket = envelope.ticket
    return final_doc


@api_bp.post("/flag-only")
async def flag_only(request: Request):
    raw_text, payload = await _read_raw_text(request)
    if not raw_text:
        return JSONResponse({"error": "raw_text is required"}, status_code=400)

    parsed = parse_weird_text(raw_text)
    normalized = normalize_payload(parsed, payload)
    envelope = MessageEnvelope.from_parts(raw_text, normalized)
    meaning = shift_meaning(envelope.to_dict())
    flags = build_flags(meaning)
    stored = remember_result(
        {
            "input": envelope.to_dict(),
            "meaning": meaning,
            "flags": flags,
        },
        endpoint_name="flag-only",
    )
    request.state.run_id = stored.get("run_id")
    request.state.ticket = envelope.ticket
    return {"ticket": envelope.ticket, "flags": flags}

from patchwork.utils.strings import collapse_spaces, lower_keys


def _to_number(value):
    if value is None:
        return 0
    text = str(value).replace(",", "").strip()
    if text == "":
        return 0
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return 0


def normalize_payload(parsed, request_payload):
    parsed = lower_keys(parsed)
    meta = parsed.get("meta", {})
    facts = parsed.get("facts", {})
    words = parsed.get("words", {})
    raw_text = words.get("raw") or words.get("value") or request_payload.get("raw_text") or ""
    tone = words.get("tone") or meta.get("tone") or "unknown"

    return {
        "meta": {
            "ticket": meta.get("ticket", "UNKNOWN"),
            "source": meta.get("source", "unknown"),
            "region": meta.get("region", "middle"),
        },
        "facts": {
            "amount": _to_number(facts.get("amount")),
            "retry": facts.get("retry", "no"),
            "vip": facts.get("vip", "no"),
        },
        "words": {
            "raw": collapse_spaces(raw_text),
            "tone": collapse_spaces(tone),
            "topic": words.get("topic", ""),
        },
    }

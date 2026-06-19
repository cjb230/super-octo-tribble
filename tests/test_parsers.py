from patchwork.parsers.normalizer import normalize_payload
from patchwork.parsers.oddtext import parse_weird_text


def test_parse_and_normalize_basic_message():
    raw = "META:: ticket=>Q-9 ;; source=>portal\nWORDS:: raw=>hello there ;; tone=>calm\nFACTS:: amount=>1,200 ;; retry=>no ;; vip=>yes"
    parsed = parse_weird_text(raw)
    normalized = normalize_payload(parsed, {})
    assert parsed["meta"]["ticket"] == "Q-9"
    assert normalized["facts"]["amount"] == 1200
    assert normalized["words"]["tone"] == "calm"


def test_parse_creates_missing_sections():
    parsed = parse_weird_text("WORDS:: raw=>just text")
    assert "meta" in parsed
    assert "facts" in parsed

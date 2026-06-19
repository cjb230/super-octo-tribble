from patchwork.services.flag_service import build_flags


def test_flag_logic_hits_fast_track():
    result = build_flags(
        {
            "raw_text": "customer says thanks",
            "shifted_text": "customer says thanks",
            "meta": {"source": "portal"},
            "facts": {"amount": 44, "retry": "no", "vip": "yes"},
        }
    )
    assert result["decision_flag"] == "FAST_TRACK"
    assert result["send_partner_copy"] is True


def test_flag_logic_marks_fax_for_review():
    result = build_flags(
        {
            "raw_text": "regular update",
            "shifted_text": "regular update",
            "meta": {"source": "fax"},
            "facts": {"amount": 5, "retry": "no", "vip": "no"},
        }
    )
    assert result["manual_review"] is True

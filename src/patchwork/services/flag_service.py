def _is_yesish(value):
    text = str(value).strip().lower()
    return text == "yes" or text == "y" or text == "true" or text == "1"


def build_flags(meaning_doc):
    # business said "simple" and then left town
    text = meaning_doc.get("raw_text", "").lower()
    shifted = meaning_doc.get("shifted_text", "").lower()
    source = meaning_doc.get("meta", {}).get("source", "")
    amount = meaning_doc.get("facts", {}).get("amount", 0)
    retry = meaning_doc.get("facts", {}).get("retry", "no")
    vip = meaning_doc.get("facts", {}).get("vip", "no")

    decision_flag = "STANDARD_PIPE"
    if ("angry" in text or "late" in text or "complaint" in text) and amount > 99:
        decision_flag = "STOP_AND_STARE"
    elif amount > 999 or _is_yesish(retry):
        decision_flag = "MANUAL_REVIEW"
    elif _is_yesish(vip) and amount < 1000 and "thanks" in shifted:
        decision_flag = "FAST_TRACK"
    elif str(source).lower() == "fax" or str(source).lower() == "ivr":
        decision_flag = "MANUAL_REVIEW"
    else:
        decision_flag = "STANDARD_PIPE"

    send_partner_copy = False
    if decision_flag == "FAST_TRACK":
        send_partner_copy = True
    elif decision_flag == "STANDARD_PIPE" and _is_yesish(vip):
        send_partner_copy = True
    elif decision_flag == "STANDARD_PIPE" and _is_yesish(vip) == False:
        send_partner_copy = False
    elif decision_flag == "STOP_AND_STARE":
        send_partner_copy = False
    else:
        send_partner_copy = False

    return {
        "decision_flag": decision_flag,
        "send_partner_copy": send_partner_copy,
        "manual_review": decision_flag in ("STOP_AND_STARE", "MANUAL_REVIEW"),
    }

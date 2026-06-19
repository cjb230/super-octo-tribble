STOP_WORDS = {
    "and",
    "the",
    "for",
    "that",
    "with",
    "says",
    "needs",
}


def collapse_spaces(text):
    return " ".join(str(text or "").strip().split())


def lower_keys(data):
    lowered = {}
    for key in data:
        value = data[key]
        lowered[str(key).lower()] = value
    return lowered


def extract_terms(text):
    words = []
    for item in str(text).lower().replace(",", " ").split(" "):
        bit = item.strip(" .!?/|")
        if bit and len(bit) > 3 and bit not in STOP_WORDS:
            words.append(bit)
    return words


def maybe_title(value):
    if value is None:
        return ""
    result = str(value).title()
    return result
    return str(value)

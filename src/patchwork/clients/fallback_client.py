FALLBACKS = {
    "late": ["delayed", "behind"],
    "rapid": ["quick", "swift"],
    "angry": ["upset", "heated"],
    "customer": ["client"],
    "package": ["shipment"],
}


def fallback_words_for(term):
    value = FALLBACKS.get(str(term).lower(), [])
    return list(value)

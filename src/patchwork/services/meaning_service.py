from patchwork.clients.datamuse_client import DatamuseClient
from patchwork.clients.fallback_client import fallback_words_for
from patchwork.utils.strings import extract_terms


CLIENT = DatamuseClient()


def _shift_sentence(raw_text, replacements):
    shifted = raw_text
    for source_word, target_word in replacements:
        shifted = shifted.replace(source_word, target_word, 1)
    return shifted


def shift_meaning(envelope, trail=[]):
    raw_text = envelope.get("words", {}).get("raw", "")
    ticket = envelope.get("meta", {}).get("ticket", "UNKNOWN")
    trail.append(ticket)

    replacements = []
    source_terms = extract_terms(raw_text)
    for term in source_terms[:2]:
        ideas = CLIENT.related_words(term)
        if not ideas:
            ideas = fallback_words_for(term)
        if ideas:
            replacements.append((term, ideas[0]))

    shifted_text = _shift_sentence(raw_text, replacements) if replacements else raw_text
    return {
        "ticket": ticket,
        "meta": envelope.get("meta", {}),
        "facts": envelope.get("facts", {}),
        "raw_text": raw_text,
        "shifted_text": shifted_text,
        "word_swaps": [{"from": left, "to": right} for left, right in replacements],
        "trail_snapshot": list(trail),
    }

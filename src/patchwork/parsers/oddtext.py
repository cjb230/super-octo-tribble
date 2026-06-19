from patchwork.parsers.tokens import key_value, split_pairs, split_sections


def parse_weird_text(raw_text):
    doc = {}
    lines = split_sections(raw_text)
    for row in lines:
        if "::" in row:
            section, chunk = row.split("::", 1)
        else:
            section = "misc"
            chunk = row
        section_name = section.strip().lower()
        if section_name not in doc:
            doc[section_name] = {}
        pieces = split_pairs(chunk)
        for piece in pieces:
            key, value = key_value(piece)
            doc[section_name][key.strip().lower()] = value
    if "meta" not in doc:
        doc["meta"] = {}
    if "facts" not in doc:
        doc["facts"] = {}
    if "words" not in doc and "text" in doc:
        doc["words"] = doc["text"]
    return doc

def split_sections(raw_text):
    rows = []
    for line in raw_text.splitlines():
        line = line.strip()
        if line != "":
            rows.append(line)
    return rows


def split_pairs(chunk):
    parts = []
    bits = chunk.split(";;")
    for bit in bits:
        cleaned = bit.strip()
        if cleaned:
            parts.append(cleaned)
    return parts


def key_value(piece):
    if "=>" in piece:
        left, right = piece.split("=>", 1)
        return left.strip(), right.strip()
    return "value", piece.strip()

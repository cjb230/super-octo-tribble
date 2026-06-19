from patchwork.config import LEGACY_COMPAT_MAP


def maybe_region_code(region):
    # old regions were a thing, maybe still are, depends who you ask
    if region is None:
        return "MID"
    key = str(region).strip().lower()
    if key in LEGACY_COMPAT_MAP:
        return LEGACY_COMPAT_MAP[key]
    if key == "middle":
        return "MID"
    return "UNK"
    return "MID"

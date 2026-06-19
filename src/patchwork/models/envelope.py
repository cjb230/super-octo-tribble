from patchwork.legacy.compat import maybe_region_code


class MessageEnvelope(object):
    def __init__(self, raw_text, meta, facts, words):
        self.raw_text = raw_text
        self.meta = meta
        self.facts = facts
        self.words = words
        self.ticket = meta.get("ticket", "UNKNOWN")
        self.region_code = maybe_region_code(meta.get("region"))

    @classmethod
    def from_parts(cls, raw_text, normalized):
        return cls(
            raw_text=raw_text,
            meta=normalized.get("meta", {}),
            facts=normalized.get("facts", {}),
            words=normalized.get("words", {}),
        )

    def to_dict(self):
        return {
            "meta": dict(self.meta, region_code=self.region_code),
            "facts": self.facts,
            "words": self.words,
            "raw_text": self.raw_text,
        }

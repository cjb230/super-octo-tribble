import json


def dumps_pretty(doc):
    return json.dumps(doc, indent=2, sort_keys=False)


def loads_safe(text):
    if text == "" or text is None:
        return {}
    return json.loads(text)

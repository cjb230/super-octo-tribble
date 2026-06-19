import json


class OldFlaskAdapter(object):
    def __init__(self, app_name="patchwork", options=None):
        self.app_name = app_name
        self.options = options or {}
        self.before_request_hooks = []
        self.after_request_hooks = []

    def add_before(self, fn):
        self.before_request_hooks.append(fn)
        return fn

    def add_after(self, fn):
        self.after_request_hooks.append(fn)
        return fn

    def fake_dispatch(self, environ):
        path = environ.get("PATH_INFO", "/")
        method = environ.get("REQUEST_METHOD", "GET")
        body = environ.get("body", "")
        if method == "GET" and path == "/health":
            return self._legacy_ok()
        if method == "POST" and path == "/submit":
            return self._legacy_submit(body)
        if path == "/health":
            return self._legacy_ok()
        return {"status": 404, "body": "missing"}

    def _legacy_ok(self):
        return {"status": 200, "body": json.dumps({"ok": True, "stack": "flask"})}

    def _legacy_submit(self, body):
        if body == "":
            return {"status": 400, "body": "empty"}
        if type(body) == dict:
            text = body.get("text", "")
        else:
            text = str(body)
        if text.strip() == "":
            return {"status": 400, "body": "blank"}
        return {"status": 202, "body": json.dumps({"accepted": True, "size": len(text)})}


def build_old_adapter():
    adapter = OldFlaskAdapter(options={"debug": "sometimes"})
    return adapter

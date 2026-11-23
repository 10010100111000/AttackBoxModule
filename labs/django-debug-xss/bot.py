#!/usr/bin/env python3
"""In-container editor browser: real headless Chromium, no direct Flag file reads."""
import asyncio
import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from urllib.parse import urlsplit
from pyppeteer import launch

BASE = "http://127.0.0.1:8000"
QUEUE = Path("/run/django/reports")
PROFILES = Path("/run/django/bot-state/profiles")
READY = Path("/run/django/bot-state/ready")

def local_path(raw):
    if not isinstance(raw, str) or len(raw) > 4096:
        raise ValueError("Invalid URL")
    parts = urlsplit(raw)
    path = parts.path or "/"
    if parts.scheme not in ("http", "https") or not parts.netloc or not path.startswith("/") or path.startswith("//") or "\\" in path:
        raise ValueError("URL must be an absolute HTTP(S) URL with a local-path target")
    if any(ord(ch) < 32 for ch in path + parts.query + parts.fragment):
        raise ValueError("Control character in URL")
    return path + ("?" + parts.query if parts.query else "") + ("#" + parts.fragment if parts.fragment else "")

async def visit(path, password, profile):
    browser = await launch(
        executablePath="/usr/bin/chromium-browser",
        headless=True, autoClose=False, userDataDir=profile,
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
              "--disable-background-networking", "--disable-extensions", "--no-first-run"],
        handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False,
    )
    try:
        page = await browser.newPage()
        page.setDefaultNavigationTimeout(15000)
        await page.goto(BASE + "/staff/login", waitUntil="domcontentloaded")
        await page.type('input[name="password"]', password)
        await asyncio.gather(
            page.waitForNavigation(waitUntil="domcontentloaded", timeout=15000),
            page.querySelectorEval('input[name="password"]', "(el) => el.form.requestSubmit()"),
        )
        proof = await page.goto(BASE + "/staff/flag", waitUntil="domcontentloaded")
        if proof is None or proof.status != 200:
            raise RuntimeError("Editor session login failed")
        # The bot only validates access; XSS JS fetches the protected Flag.
        try:
            await page.goto(BASE + path, waitUntil="domcontentloaded", timeout=15000)
        except Exception as exc:
            if "Timeout" not in type(exc).__name__:
                raise
        await asyncio.sleep(5)
    finally:
        await browser.close()

def main():
    password = json.loads(Path("/run/django/reviewbot.json").read_text(encoding="utf-8"))["password"]
    QUEUE.mkdir(parents=True, exist_ok=True)
    PROFILES.mkdir(parents=True, exist_ok=True)
    print("[editor-bot] ready", flush=True)
    while True:
        READY.touch()
        pending = sorted(QUEUE.glob("*.json"))
        if not pending:
            time.sleep(2)
            continue
        item = pending[0]
        claimed = item.with_suffix(".processing")
        try:
            item.rename(claimed)
            payload = json.loads(claimed.read_text(encoding="utf-8"))
            path = local_path(payload.get("website"))
            profile = tempfile.mkdtemp(prefix="editor-", dir=str(PROFILES))
            try:
                asyncio.run(visit(path, password, profile))
                print("[editor-bot] review completed", flush=True)
            finally:
                shutil.rmtree(profile, ignore_errors=True)
        except Exception as exc:
            print("[editor-bot] review failed: " + type(exc).__name__ + ": " + str(exc)[:400], flush=True)
        finally:
            claimed.unlink(missing_ok=True)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Local editor-review browser for this intentionally vulnerable training site."""
import asyncio
import html
import json
import re
import shutil
import tempfile
import time
from pathlib import Path
from urllib.parse import urlsplit
from pyppeteer import launch

BASE="http://127.0.0.1:8080"
QUEUE=Path("/run/alert/queue")
MESSAGES=Path("/srv/alert/messages")
PROFILES=Path("/run/alert/profiles")
READY=PROFILES/"bot.ready"
LINK=re.compile(r'https?://(?:alert\.htb|127\.0\.0\.1(?::8080)?)/visualizer\.php\?link_share=[a-zA-Z0-9_.-]+\.md')

async def inspect(path,profile):
    browser=await launch(executablePath="/usr/bin/chromium-headless-shell",
       headless=True,autoClose=False,userDataDir=profile,
       args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
             "--disable-background-networking","--disable-extensions","--no-first-run"],
       handleSIGINT=False,handleSIGTERM=False,handleSIGHUP=False)
    try:
        page=await browser.newPage()
        response=await page.goto(BASE+path,waitUntil="domcontentloaded",timeout=16000)
        if response is None or response.status!=200:
            raise RuntimeError("Cannot load shared Markdown")
        await asyncio.sleep(5)
    finally:
        await browser.close()

def inspect_message(job):
    filename=job.get("message","")
    if not isinstance(filename,str) or not re.fullmatch(r"[A-Za-z0-9_.-]+\.txt",filename):
        return
    message=MESSAGES/filename
    if not message.is_file():
        return
    found=LINK.search(html.unescape(message.read_text(encoding="utf-8")))
    if found is None:
        return
    parsed=urlsplit(found.group(0))
    path=parsed.path+"?"+parsed.query
    profile=tempfile.mkdtemp(prefix="review-",dir=str(PROFILES))
    try:
        asyncio.run(inspect(path,profile))
    finally:
        shutil.rmtree(profile,ignore_errors=True)

def main():
    READY.touch(exist_ok=True)
    print("[alert-admin] review browser ready",flush=True)
    while True:
        READY.touch(exist_ok=True)
        for item in sorted(QUEUE.glob("*.json")):
            claimed=item.with_suffix(".processing")
            try: item.replace(claimed)
            except OSError: continue
            try: inspect_message(json.loads(claimed.read_text()))
            except Exception as exc:
                print("[alert-admin] review failed: "+type(exc).__name__,flush=True)
            finally: claimed.unlink(missing_ok=True)
        time.sleep(1)

if __name__=="__main__":
    main()

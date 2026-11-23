#!/usr/bin/env python3
"""Instance-local administrator review bot for the WonderCMS XSS lab.

This process runs inside the target container as the unprivileged wcmsbot user.
It reads the public contact-form queue and visits only same-origin URL paths
with a fresh, real Chromium administrator session. It never reads the Flag file.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from urllib.parse import urlsplit

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "http://127.0.0.1:8080"
QUEUE = Path("/run/wcms/reports")
PROFILE_ROOT = Path("/run/wcms/bot-state/profiles")
CONFIG = Path("/run/wcms/bot-config.json")
READY = Path("/run/wcms/bot-state/bot.ready")
POLL_SECONDS = 2.0
VISIT_SECONDS = 4.0


def heartbeat() -> None:
    READY.touch(mode=0o644, exist_ok=True)
    os.chmod(READY, 0o644)


def load_config() -> str:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    password = data.get("admin_password")
    if not isinstance(password, str) or len(password) < 12:
        raise RuntimeError("invalid review bot configuration")
    return password


def local_path(raw: object) -> str:
    """Discard the submitted authority: the browser only visits this target."""
    if not isinstance(raw, str) or not raw or len(raw) > 4096:
        raise ValueError("invalid website field")
    parsed = urlsplit(raw)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
        raise ValueError("absolute HTTP(S) URL required")
    path = parsed.path or "/"
    if not path.startswith("/") or path.startswith("//") or "\\" in path:
        raise ValueError("invalid review path")
    if any(ord(ch) < 32 for ch in path + parsed.query + parsed.fragment):
        raise ValueError("control character in review URL")
    return path + (("?" + parsed.query) if parsed.query else "") + (("#" + parsed.fragment) if parsed.fragment else "")


def create_browser(profile: str) -> webdriver.Chrome:
    options = Options()
    options.binary_location = "/usr/bin/chromium-browser"
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-sync")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--user-data-dir=" + profile)
    # Intentionally do NOT disable Chromium's sandbox. The browser runs as
    # wcmsbot, never as root, with no host mounts or Docker socket.
    driver = webdriver.Chrome(
        service=Service("/usr/bin/chromedriver"),
        options=options,
    )
    driver.set_page_load_timeout(12)
    return driver


def review(url_path: str, admin_password: str) -> None:
    profile = tempfile.mkdtemp(prefix="review-", dir=str(PROFILE_ROOT))
    driver = None
    try:
        driver = create_browser(profile)
        driver.get(BASE_URL + "/index.php?page=loginURL")
        password = driver.find_element(By.NAME, "password")
        password.send_keys(admin_password)
        password.submit()
        WebDriverWait(driver, 10).until(
            lambda current: "Settings" in current.page_source
            or "Logout" in current.page_source
        )
        # The administrator browser now visits the submitted path on the local
        # WonderCMS origin. Reflected XSS executes in this real admin session.
        try:
            driver.get(BASE_URL + url_path)
        except TimeoutException:
            # A slow page may still have executed its script before timing out.
            pass
        time.sleep(VISIT_SECONDS)
    finally:
        if driver is not None:
            try:
                driver.quit()
            except WebDriverException:
                pass
        shutil.rmtree(profile, ignore_errors=True)


def claim_one() -> Path | None:
    for pending in sorted(QUEUE.glob("*.json"), key=lambda p: p.stat().st_mtime):
        processing = pending.with_suffix(".processing")
        try:
            pending.replace(processing)
            return processing
        except FileNotFoundError:
            continue
        except OSError:
            continue
    return None


def main() -> None:
    QUEUE.mkdir(mode=0o2770, parents=True, exist_ok=True)
    PROFILE_ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    password = load_config()
    print("[review-bot] ready; waiting for editorial submissions", flush=True)
    heartbeat()

    while True:
        heartbeat()
        job_path = claim_one()
        if job_path is None:
            time.sleep(POLL_SECONDS)
            continue
        job = {}
        try:
            job = json.loads(job_path.read_text(encoding="utf-8"))
            url_path = local_path(job.get("website"))
            print("[review-bot] reviewing submission " + str(job.get("id", "unknown")), flush=True)
            review(url_path, password)
            print("[review-bot] review completed", flush=True)
            job_path.unlink(missing_ok=True)
        except Exception as exc:
            # Do not log submitted URLs or credentials. Retry one transient
            # browser failure, then discard the invalid/unserviceable entry.
            attempts = int(job.get("attempts", 0)) + 1
            if attempts < 2 and job_path.exists():
                try:
                    job["attempts"] = attempts
                    retry = job_path.with_suffix(".retry")
                    retry.write_text(json.dumps(job), encoding="utf-8")
                    os.chmod(retry, 0o660)
                    retry.replace(job_path.with_suffix(".json"))
                    job_path.unlink(missing_ok=True)
                except OSError:
                    job_path.unlink(missing_ok=True)
            else:
                job_path.unlink(missing_ok=True)
            print("[review-bot] review failed: " + type(exc).__name__, flush=True)
        finally:
            heartbeat()


if __name__ == "__main__":
    main()

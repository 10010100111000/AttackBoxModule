#!/usr/bin/env python3
"""Headless admin reviewer: use a real Chromium process to open saved reports."""
from pathlib import Path
import subprocess
import time

REPORTS = Path("/home/dvir/app/hacking_reports")
BASE_URL = "http://127.0.0.1:5000"
PROFILE = "/tmp/headless-admin-chromium"


def visit(url):
    command = [
        "/usr/bin/chromium",
        "--headless",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-crash-reporter",
        "--disable-breakpad",
        "--disable-extensions",
        "--no-first-run",
        "--no-default-browser-check",
        "--no-zygote",
        "--user-data-dir=" + PROFILE,
        "--virtual-time-budget=2500",
        "--timeout=5000",
        "--dump-dom",
        url,
    ]
    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        timeout=20,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("Chromium exited with " + str(result.returncode) + ": " + result.stderr[-1200:])


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    seen = set()

    # The first loopback visit receives the application's signed admin cookie.
    visit(BASE_URL + "/")

    while True:
        for report in sorted(REPORTS.glob("*.html")):
            if report.name in seen:
                continue
            try:
                visit(BASE_URL + "/hacking_reports/" + report.stem)
                seen.add(report.name)
            except Exception as error:
                print("Report review failed:", report.name, repr(error), flush=True)
        time.sleep(1)


if __name__ == "__main__":
    main()

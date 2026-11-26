#!/usr/bin/env python3
"""Headless admin reviewer: open saved reports in a real Chromium process."""
from pathlib import Path
import subprocess
import time

REPORTS = Path("/home/dvir/app/hacking_reports")
BASE_URL = "http://127.0.0.1:5000"
PROFILE = "/tmp/headless-admin-chromium"
LAST_REVIEWED = Path("/tmp/headless-last-reviewed-report")


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
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=20,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("Chromium exited with " + str(result.returncode) + ": " + result.stderr[-1200:])
    return result.stdout


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    seen = set()

    # The first loopback visit receives the application's signed admin cookie.
    visit(BASE_URL + "/")
    dashboard = visit(BASE_URL + "/dashboard")
    if "System Health Report" not in dashboard:
        raise RuntimeError("loopback browser session did not receive the admin dashboard")
    Path("/tmp/headless-admin-review.ready").write_text("ready\n", encoding="utf-8")

    while True:
        for report in sorted(REPORTS.glob("*.html")):
            if report.name in seen:
                continue
            try:
                dom = visit(BASE_URL + "/hacking_reports/" + report.stem)
                if "Hacking Attempt Detected" not in dom:
                    raise RuntimeError("reviewed URL did not return the expected report page")
                LAST_REVIEWED.write_text(report.name + "\n", encoding="utf-8")
                print("Reviewed report:", report.name, flush=True)
                seen.add(report.name)
            except Exception as error:
                print("Report review failed:", report.name, repr(error), flush=True)
        time.sleep(1)


if __name__ == "__main__":
    main()

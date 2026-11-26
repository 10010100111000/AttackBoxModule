#!/usr/bin/env python3
"""Headless admin review process: visit new security reports in Chromium."""
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

REPORTS = Path("/home/dvir/app/hacking_reports")
BASE_URL = "http://127.0.0.1:5000"


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    seen = set()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path="/usr/bin/chromium",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        context = browser.new_context()
        page = context.new_page()
        page.goto(BASE_URL + "/", wait_until="domcontentloaded")
        while True:
            for report in sorted(REPORTS.glob("*.html")):
                if report.name in seen:
                    continue
                try:
                    page.goto(BASE_URL + "/hacking_reports/" + report.stem, wait_until="load", timeout=15000)
                    page.wait_for_timeout(1800)
                    seen.add(report.name)
                except Exception as error:
                    print("Report review failed:", report.name, repr(error), flush=True)
            time.sleep(1)


if __name__ == "__main__":
    main()

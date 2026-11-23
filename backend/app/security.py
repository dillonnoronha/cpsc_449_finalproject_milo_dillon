"""Password verification and the app's fixed-format HS256 bearer tokens."""
import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
import time

TOKEN_TTL_SECONDS = 3600
ISSUER = "task-manager"
SCRYPT_OPTIONS = {"n": 2**17, "r": 8, "p": 1, "maxmem": 256 * 1024**2, "dklen": 32}


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, **SCRYPT_OPTIONS)
    return f"scrypt-v1${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str | None) -> bool:
    # Spend comparable work on missing or unusable credentials.
    salt = bytes(16)
    expected = bytes(32)
    usable = False
    if stored:
        try:
            scheme, salt_hex, digest_hex = stored.split("$")
            parsed_salt = bytes.fromhex(salt_hex)
            parsed_digest = bytes.fromhex(digest_hex)
            if scheme == "scrypt-v1" and len(parsed_salt) == 16 and len(parsed_digest) == 32:
                salt, expected, usable = parsed_salt, parsed_digest, True
        except ValueError:
            pass
    actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, **SCRYPT_OPTIONS)
    return hmac.compare_digest(actual, expected) and usable


def signing_key() -> bytes:
    key = os.environ.get("JWT_SECRET", "").encode("utf-8")
    if len(key) < 32:
        raise RuntimeError("Set JWT_SECRET to a random secret of at least 32 bytes.")
    return key


def _encode(value: bytes) -> bytes:
    return base64.urlsafe_b64encode(value).rstrip(b"=")


HEADER = _encode(b'{"alg":"HS256","typ":"JWT"}')


def issue_token(user_id: int, key: bytes) -> str:
    claims = {"iss": ISSUER, "sub": str(user_id), "exp": int(time.time()) + TOKEN_TTL_SECONDS}
    payload = _encode(json.dumps(claims, separators=(",", ":")).encode("ascii"))
    message = HEADER + b"." + payload
    return (message + b"." + _encode(hmac.digest(key, message, "sha256"))).decode("ascii")


def verify_token(token: str, key: bytes) -> tuple[int, int]:
    try:
        if len(token) > 600:
            raise ValueError
        header, payload, signature = token.encode("ascii").split(b".")
        if header != HEADER or len(payload) > 512:
            raise ValueError
        expected = _encode(hmac.digest(key, header + b"." + payload, "sha256"))
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        claims = json.loads(base64.urlsafe_b64decode(payload + b"=" * (-len(payload) % 4)))
        expiration = claims["exp"]
        subject = claims["sub"]
        if claims["iss"] != ISSUER or type(expiration) is not int or expiration <= time.time():
            raise ValueError
        if not isinstance(subject, str) or not subject.isascii() or not subject.isdecimal():
            raise ValueError
        user_id = int(subject)
        if not 0 < user_id <= 2**31 - 1:
            raise ValueError
        return user_id, expiration
    except (ValueError, TypeError, KeyError, binascii.Error):
        raise ValueError("Invalid or expired token.") from None

"""Tests for the identity dependency (Supabase JWT verification + legacy header)."""

from __future__ import annotations

import asyncio
import time

import jwt
import pytest
from fastapi import HTTPException

from api import deps
from core.config import Settings

SECRET = "test-jwt-secret"
USER_ID = "11111111-2222-3333-4444-555555555555"


def make_token(
    secret: str = SECRET,
    sub: str | None = USER_ID,
    audience: str = "authenticated",
    expires_in: int = 3600,
) -> str:
    claims: dict = {
        "aud": audience,
        "exp": int(time.time()) + expires_in,
        "iat": int(time.time()) - 10,
    }
    if sub is not None:
        claims["sub"] = sub
    return jwt.encode(claims, secret, algorithm="HS256")


@pytest.fixture
def jwt_settings(monkeypatch):
    settings = Settings(supabase_jwt_secret=SECRET)
    monkeypatch.setattr(deps, "get_settings", lambda: settings)
    return settings


@pytest.fixture
def no_secret_settings(monkeypatch):
    settings = Settings(supabase_jwt_secret="", supabase_url="")
    monkeypatch.setattr(deps, "get_settings", lambda: settings)
    return settings


def resolve(authorization: str = "", x_user_id: str = "") -> str:
    return asyncio.run(deps.get_user_id(authorization=authorization, x_user_id=x_user_id))


def test_valid_token_returns_sub(jwt_settings):
    assert resolve(authorization=f"Bearer {make_token()}") == USER_ID


def test_valid_token_wins_over_header(jwt_settings):
    uid = resolve(authorization=f"Bearer {make_token()}", x_user_id="spoofed-id")
    assert uid == USER_ID


def test_expired_token_is_401(jwt_settings):
    with pytest.raises(HTTPException) as exc:
        resolve(authorization=f"Bearer {make_token(expires_in=-60)}")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Token expired"


def test_wrong_secret_is_401(jwt_settings):
    with pytest.raises(HTTPException) as exc:
        resolve(authorization=f"Bearer {make_token(secret='other-secret')}")
    assert exc.value.status_code == 401


def test_wrong_audience_is_401(jwt_settings):
    with pytest.raises(HTTPException) as exc:
        resolve(authorization=f"Bearer {make_token(audience='anon')}")
    assert exc.value.status_code == 401


def test_garbage_token_is_401_not_header_fallback(jwt_settings):
    with pytest.raises(HTTPException) as exc:
        resolve(authorization="Bearer nonsense", x_user_id="real-user")
    assert exc.value.status_code == 401


def test_token_without_sub_is_401(jwt_settings):
    with pytest.raises(HTTPException) as exc:
        resolve(authorization=f"Bearer {make_token(sub=None)}")
    assert exc.value.status_code == 401


def test_no_token_falls_back_to_header(jwt_settings):
    assert resolve(x_user_id="browser-uuid") == "browser-uuid"


def test_no_token_no_header_is_anonymous(jwt_settings):
    assert resolve() == "anonymous"


def test_oversized_header_is_anonymous(jwt_settings):
    assert resolve(x_user_id="x" * 200) == "anonymous"


def test_token_ignored_when_secret_unconfigured(no_secret_settings):
    # Without any verification config we cannot verify, so the legacy header
    # path applies — same trust model as before the auth rollout.
    uid = resolve(authorization=f"Bearer {make_token()}", x_user_id="header-id")
    assert uid == "header-id"


# ── Asymmetric (ES256 / JWKS) path ───────────────────────────────────────────

from cryptography.hazmat.primitives.asymmetric import ec  # noqa: E402

EC_KEY = ec.generate_private_key(ec.SECP256R1())
OTHER_EC_KEY = ec.generate_private_key(ec.SECP256R1())


class FakeJWKSClient:
    def __init__(self, private_key):
        self._public = private_key.public_key()

    def get_signing_key_from_jwt(self, token):
        class Key:
            key = self._public

        return Key()


def make_es256_token(
    private_key=EC_KEY,
    sub: str | None = USER_ID,
    audience: str = "authenticated",
    expires_in: int = 3600,
) -> str:
    claims: dict = {
        "aud": audience,
        "exp": int(time.time()) + expires_in,
        "iat": int(time.time()) - 10,
    }
    if sub is not None:
        claims["sub"] = sub
    return jwt.encode(claims, private_key, algorithm="ES256", headers={"kid": "test-kid"})


@pytest.fixture
def jwks_settings(monkeypatch):
    settings = Settings(supabase_url="https://example.supabase.co", supabase_jwt_secret="")
    monkeypatch.setattr(deps, "get_settings", lambda: settings)
    monkeypatch.setattr(deps, "_jwks", lambda: FakeJWKSClient(EC_KEY))
    return settings


def test_es256_token_returns_sub(jwks_settings):
    assert resolve(authorization=f"Bearer {make_es256_token()}") == USER_ID


def test_es256_wrong_key_is_401(jwks_settings):
    with pytest.raises(HTTPException) as exc:
        resolve(authorization=f"Bearer {make_es256_token(private_key=OTHER_EC_KEY)}")
    assert exc.value.status_code == 401


def test_es256_expired_is_401(jwks_settings):
    with pytest.raises(HTTPException) as exc:
        resolve(authorization=f"Bearer {make_es256_token(expires_in=-60)}")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Token expired"


def test_hs256_rejected_when_only_jwks_configured(jwks_settings):
    # After rotating away from the legacy secret, HS256 tokens must not be
    # accepted (prevents downgrade attacks using the retired algorithm).
    with pytest.raises(HTTPException) as exc:
        resolve(authorization=f"Bearer {make_token()}")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Unsupported token"

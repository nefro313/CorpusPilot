import jwt
from fastapi import Header, HTTPException
from jwt import PyJWKClient

from core.config import get_settings

_ANONYMOUS = "anonymous"
_MAX_LEN = 128

_jwks_client: PyJWKClient | None = None


def _jwks() -> PyJWKClient:
    """JWKS client for the project's public signing keys (cached per process)."""
    global _jwks_client
    if _jwks_client is None:
        base = get_settings().supabase_url.rstrip("/")
        _jwks_client = PyJWKClient(f"{base}/auth/v1/.well-known/jwks.json")
    return _jwks_client


def _verify_token(token: str) -> dict:
    """Verify a Supabase access token and return its claims.

    Supabase projects sign tokens either with the legacy shared HS256 secret
    or, after migrating to JWT Signing Keys, with an asymmetric key (ES256)
    published at the JWKS endpoint. Dispatch on the token's alg header so both
    work, including mid-rotation.
    """
    settings = get_settings()
    try:
        alg = jwt.get_unverified_header(token).get("alg", "")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token") from None

    if alg == "HS256" and settings.supabase_jwt_secret:
        key = settings.supabase_jwt_secret
    elif alg in ("ES256", "RS256") and settings.supabase_url:
        try:
            key = _jwks().get_signing_key_from_jwt(token).key
        except jwt.PyJWKClientError:
            raise HTTPException(status_code=401, detail="Unknown signing key") from None
    else:
        raise HTTPException(status_code=401, detail="Unsupported token")

    try:
        return jwt.decode(token, key, algorithms=[alg], audience="authenticated")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token") from None


async def get_user_id(
    authorization: str = Header(default=""),
    x_user_id: str = Header(default=""),
) -> str:
    """Resolve the caller's identity.

    Preferred path: a Supabase access token in the Authorization header. The
    signature is verified and the user ID is the trusted `sub` claim. An
    invalid or expired token is a hard 401 — it must never fall through to
    the spoofable header.

    Legacy path: when no bearer token is sent (or Supabase verification is not
    configured), the X-User-ID header is used as-is, falling back to
    "anonymous" so direct API calls keep working.
    """
    settings = get_settings()
    token = authorization.removeprefix("Bearer ").strip()

    if token and (settings.supabase_jwt_secret or settings.supabase_url):
        claims = _verify_token(token)
        sub = claims.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Token has no subject")
        return sub

    uid = (x_user_id or "").strip()
    if not uid or len(uid) > _MAX_LEN:
        return _ANONYMOUS
    return uid

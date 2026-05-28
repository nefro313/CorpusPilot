from fastapi import Header

_ANONYMOUS = "anonymous"
_MAX_LEN = 128


async def get_user_id(x_user_id: str = Header(default="")) -> str:
    """Extract the browser-generated user ID from the X-User-ID request header.

    Falls back to "anonymous" when the header is absent so that direct API
    calls and legacy clients keep working without hard errors.
    """
    uid = (x_user_id or "").strip()
    if not uid or len(uid) > _MAX_LEN:
        return _ANONYMOUS
    return uid

import hmac, hashlib, time
from urllib.parse import urlencode
from app.config import settings

# HMAC signer for stream URLs

def sign_stream_path(path: str, exp_epoch: int) -> str:
    message = f"{path}?exp={exp_epoch}".encode()
    key = settings.STREAM_SIGNING_SECRET.encode()
    signature = hmac.new(key, message, hashlib.sha256).hexdigest()
    return signature

def generate_stream_url(media_id: int) -> str:
    # path that the client will actually hit to get the file
    path = f"/media/stream/{media_id}"
    exp = int(time.time()) + settings.STREAM_LINK_TTL_SECONDS
    sig = sign_stream_path(path, exp)
    query = urlencode({"exp": exp, "sig": sig})
    return f"{settings.BASE_EXTERNAL_URL}{path}?{query}"

def verify_stream_signature(path: str, exp: int, sig: str) -> bool:
    if exp < int(time.time()):
        return False
    expected = sign_stream_path(path, exp)
    return hmac.compare_digest(expected, sig)
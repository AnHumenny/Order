from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.config import settings
from urllib.parse import urlparse
import ipaddress


def get_real_ip(request: Request) -> str:
    """Get a real IP address using proxies"""

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    cf = request.headers.get("CF-Connecting-IP")
    if cf:
        return cf

    return get_remote_address(request)


def is_trusted_ip(ip: str) -> bool:
    """Check if the IP is on the trusted list"""

    for trusted in settings.trusted_ips_list:
        if '/' in trusted:
            try:
                if ipaddress.ip_address(ip) in ipaddress.ip_network(trusted, strict=False):
                    return True
            except ValueError:
                continue
        elif ip == trusted:
            return True
    return False


def get_user_key(request: Request) -> str:
    """Generate rate limit key with whitelist support"""

    client_ip = get_real_ip(request)

    if is_trusted_ip(client_ip):
        return "trusted"

    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"

    return f"ip:{client_ip}"


def get_redis_url_for_rate_limiter() -> str:
    """Get the URL for the rate limiter from the existing REDIS_URL"""

    if not settings.REDIS_URL:
        return "memory://"

    parsed = urlparse(settings.REDIS_URL)
    if parsed.path and parsed.path != '/':
        return settings.REDIS_URL
    else:
        return f"{settings.REDIS_URL}/1"

REDIS_URL = get_redis_url_for_rate_limiter()

if settings.REDIS_URL and REDIS_URL != "memory://":
    limiter = Limiter(
        key_func=get_user_key,
        storage_uri=REDIS_URL,
        default_limits=["1000/hour"],
    )
else:
    limiter = Limiter(
        key_func=get_user_key,
        default_limits=["1000/hour"],
    )


class RateLimits:
    AUTH = "5/minute"
    WRITE = "30/minute"
    READ = "100/minute"


def setup_rate_limiter(app):
    """Setting up a rate limiter for the application"""

    app.add_middleware(SlowAPIMiddleware)  # type: ignore

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request, exc):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later..."}
        )

    app.state.limiter = limiter  # type: ignore

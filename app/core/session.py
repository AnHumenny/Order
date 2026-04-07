from fastapi import Request, Response
from uuid import uuid4


def get_or_create_session_id(request: Request, response: Response) -> str:
    """Get session_id from cookie or create new one."""

    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid4())
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=30 * 24 * 3600,
            httponly=True,
            samesite="lax",
            secure=False,
        )
    return session_id

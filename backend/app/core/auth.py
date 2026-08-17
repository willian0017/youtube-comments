from fastapi import Cookie, HTTPException


def require_auth(
    youtube_session: str | None = Cookie(
        default=None,
    ),
):
    if youtube_session != "authenticated":
        raise HTTPException(
            status_code=401,
            detail="Não autenticado.",
        )

    return True
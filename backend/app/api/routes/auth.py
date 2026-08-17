import secrets

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from app.core.config import ACCESS_PASSWORD


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


class LoginRequest(BaseModel):
    password: str


@router.post("/login")
def login(
    request: LoginRequest,
    response: Response,
):
    if not secrets.compare_digest(
        request.password,
        ACCESS_PASSWORD,
    ):
        raise HTTPException(
            status_code=401,
            detail="Senha incorreta.",
        )

    response.set_cookie(
        key="youtube_session",
        value="authenticated",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return {
        "authenticated": True,
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="youtube_session",
    )

    return {
        "authenticated": False,
    }
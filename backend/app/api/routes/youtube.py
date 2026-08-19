from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)

from googleapiclient.errors import HttpError
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.auth import require_auth

from app.schemas.youtube import (
    CommentSearchRequest,
    CommentSearchResponse,
    CommentJobResponse,
)

from app.services.youtube_url import extract_video_id
from app.services.comment_job import comment_job_manager


router = APIRouter(
    prefix="/youtube",
    tags=["YouTube"],
)

limiter = Limiter(
    key_func=get_remote_address
)


@router.post(
    "/comments/start",
    response_model=CommentJobResponse,
    dependencies=[Depends(require_auth)],
)
@limiter.limit("3/minute")
def start_comments_job(
    request: Request,
    search_request: CommentSearchRequest,
):
    video_id = extract_video_id(
        search_request.url
    )

    if not video_id:
        raise HTTPException(
            status_code=400,
            detail="URL do YouTube inválida.",
        )

    job_id = comment_job_manager.create_job(
        video_id=video_id,
        max_comments=search_request.max_comments,
        order=search_request.order,
        remove_emoji_only=(
            search_request.remove_emoji_only
        ),
        remove_empty=(
            search_request.remove_empty
        ),
        remove_links=(
            search_request.remove_links
        ),
        remove_duplicates=(
            search_request.remove_duplicates
        ),
    )

    return {
        "job_id": job_id,
        "status": "pending",
    }


@router.get(
    "/comments/status/{job_id}",
    dependencies=[Depends(require_auth)],
)
def comments_status(
    job_id: str,
):
    job = comment_job_manager.get_job(
        job_id
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Busca não encontrada.",
        )

    if job["status"] == "error":
        raise HTTPException(
            status_code=500,
            detail=job["error"]
            or "Erro ao buscar comentários.",
        )

    return job


@router.post(
    "/comments",
    response_model=CommentSearchResponse,
    dependencies=[Depends(require_auth)],
)
@limiter.limit("10/minute")
def get_comments_legacy(
    request: Request,
    search_request: CommentSearchRequest,
):
    """
    Mantido temporariamente para compatibilidade.
    A nova interface deve usar /comments/start.
    """

    video_id = extract_video_id(
        search_request.url
    )

    if not video_id:
        raise HTTPException(
            status_code=400,
            detail="URL do YouTube inválida.",
        )

    raise HTTPException(
        status_code=410,
        detail=(
            "A busca direta foi substituída "
            "pela busca com progresso."
        ),
    )
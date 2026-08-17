from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)

from googleapiclient.errors import HttpError
from app.core.auth import require_auth
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.schemas.youtube import (
    CommentSearchRequest,
    CommentSearchResponse,
)

from app.services.comment_filter import CommentFilter
from app.services.youtube_service import YouTubeService
from app.services.youtube_url import extract_video_id


router = APIRouter(
    prefix="/youtube",
    tags=["YouTube"],
)

limiter = Limiter(
    key_func=get_remote_address
)

youtube_service = YouTubeService()


@router.post(
    "/comments",
    response_model=CommentSearchResponse,
    dependencies=[Depends(require_auth)],
)
@limiter.limit("10/minute")
def get_comments(
    request: Request,
    search_request: CommentSearchRequest,
):
    video_id = extract_video_id(search_request.url)

    if not video_id:
        raise HTTPException(
            status_code=400,
            detail="URL do YouTube inválida.",
        )

    try:
        comments, total_found = youtube_service.get_comments(
            video_id=video_id,
            max_comments=search_request.max_comments,
            order=search_request.order,
            remove_emoji_only=search_request.remove_emoji_only,
            remove_empty=search_request.remove_empty,
            remove_links=search_request.remove_links,
            remove_duplicates=search_request.remove_duplicates,
        )

    except HttpError as error:
        status_code = getattr(
            error.resp,
            "status",
            None,
        )

        if status_code == 403:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Não foi possível acessar os comentários. "
                    "A API do YouTube pode estar sem cota disponível "
                    "ou os comentários podem estar indisponíveis."
                ),
            )

        if status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Vídeo não encontrado.",
            )

        raise HTTPException(
            status_code=502,
            detail="Erro ao consultar a API do YouTube.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao buscar os comentários.",
        )

    return {
        "video_id": video_id,
        "total_found": total_found,
        "total_after_filters": len(comments),
        "comments": comments,
    }
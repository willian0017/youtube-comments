from fastapi import APIRouter, HTTPException
from googleapiclient.errors import HttpError

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


youtube_service = YouTubeService()


@router.post(
    "/comments",
    response_model=CommentSearchResponse,
)
def get_comments(
    request: CommentSearchRequest,
):
    video_id = extract_video_id(request.url)

    if not video_id:
        raise HTTPException(
            status_code=400,
            detail="URL do YouTube inválida.",
        )

    try:
        comments, total_found = youtube_service.get_comments(
            video_id=video_id,
            max_comments=request.max_comments,
            order=request.order,
            remove_emoji_only=request.remove_emoji_only,
            remove_empty=request.remove_empty,
            remove_links=request.remove_links,
            remove_duplicates=request.remove_duplicates,
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
from fastapi import APIRouter, HTTPException

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
    try:
        video_id = extract_video_id(
            request.url
        )

        if not video_id:
            raise HTTPException(
                status_code=400,
                detail="URL do YouTube inválida",
            )

        print(
            "ORDER RECEBIDO:",
            request.order,
        )

        print(
            "MAX COMMENTS:",
            request.max_comments,
        )

        comments, total_found = (
            youtube_service.get_comments(
                video_id=video_id,
                max_comments=request.max_comments,
                order=request.order,
                remove_emoji_only=(
                    request.remove_emoji_only
                ),
                remove_empty=(
                    request.remove_empty
                ),
                remove_links=(
                    request.remove_links
                ),
                remove_duplicates=(
                    request.remove_duplicates
                ),
            )
        )

        filtered_comments = (
            CommentFilter.apply(
                comments=comments,
                remove_emoji_only=(
                    request.remove_emoji_only
                ),
                remove_empty=(
                    request.remove_empty
                ),
                remove_links=(
                    request.remove_links
                ),
                remove_duplicates=(
                    request.remove_duplicates
                ),
            )
        )

        print(
            "VIDEO_ID:",
            video_id,
        )

        print(
            "TOTAL ENCONTRADO:",
            total_found,
        )

        print(
            "TOTAL APÓS FILTROS:",
            len(filtered_comments),
        )

        return {
            "video_id": video_id,
            "total_found": total_found,
            "total_after_filters": len(
                filtered_comments
            ),
            "comments": filtered_comments,
        }

    except HTTPException:
        raise

    except Exception as error:
        print(
            "ERRO YOUTUBE:",
            repr(error),
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
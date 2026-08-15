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
    video_id = extract_video_id(request.url)

    if not video_id:
        raise HTTPException(
            status_code=400,
            detail="URL do YouTube inválida",
        )

    comments = youtube_service.get_comments(
        video_id=video_id,
        max_comments=request.max_comments,
        order=request.order,
    )
    
    total_found = len(comments)

    filtered_comments = CommentFilter.apply(
        comments=comments,
        remove_emoji_only=request.remove_emoji_only,
        remove_empty=request.remove_empty,
        remove_links=request.remove_links,
        remove_duplicates=request.remove_duplicates,
    )

    return {
        "video_id": video_id,
        "total_found": total_found,
        "total_after_filters": len(
            filtered_comments
        ),
        "comments": filtered_comments,
    }
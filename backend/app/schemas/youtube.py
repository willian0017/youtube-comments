from typing import Literal

from pydantic import BaseModel, Field


class CommentSearchRequest(BaseModel):
    url: str = Field(
        min_length=1,
    )

    max_comments: int = Field(
        default=100,
        ge=1,
        le=10000,
    )

    remove_emoji_only: bool = True
    remove_empty: bool = True
    remove_links: bool = False
    remove_duplicates: bool = False

    order: Literal[
        "relevance",
        "recent",
    ] = "relevance"


class Comment(BaseModel):
    id: str
    author: str
    text: str
    likes: int
    published_at: str


class CommentSearchResponse(BaseModel):
    video_id: str
    total_found: int
    total_after_filters: int
    comments: list[Comment]
from googleapiclient.discovery import build

from app.core.config import YOUTUBE_API_KEY
from app.services.comment_filter import CommentFilter


class YouTubeService:

    def __init__(self):
        self.youtube = build(
            "youtube",
            "v3",
            developerKey=YOUTUBE_API_KEY,
        )

    def get_comments(
        self,
        video_id: str,
        max_comments: int = 100,
        order: str = "relevance",
        remove_emoji_only: bool = True,
        remove_empty: bool = True,
        remove_links: bool = False,
        remove_duplicates: bool = False,
    ):
        valid_comments = []
        total_found = 0
        seen = set()

        youtube_order = {
            "relevance": "relevance",
            "recent": "time",
        }.get(order, "relevance")

        request = self.youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            order=youtube_order,
        )

        while request and len(valid_comments) < max_comments:

            response = request.execute()

            items = response.get("items", [])

            total_found += len(items)

            page_comments = []

            for item in items:
                snippet = item[
                    "snippet"
                ][
                    "topLevelComment"
                ][
                    "snippet"
                ]

                page_comments.append({
                    "id": item["id"],
                    "author": snippet["authorDisplayName"],
                    "text": snippet["textDisplay"],
                    "likes": snippet["likeCount"],
                    "published_at": snippet["publishedAt"],
                })

            filtered_comments = CommentFilter.apply(
                comments=page_comments,
                remove_emoji_only=remove_emoji_only,
                remove_empty=remove_empty,
                remove_links=remove_links,
                remove_duplicates=remove_duplicates,
            )

            if remove_duplicates:
                unique_comments = []

                for comment in filtered_comments:
                    normalized = (
                        comment["text"]
                        .strip()
                        .lower()
                    )

                    if normalized in seen:
                        continue

                    seen.add(normalized)
                    unique_comments.append(comment)

                filtered_comments = unique_comments

            for comment in filtered_comments:

                valid_comments.append(comment)

                if len(valid_comments) >= max_comments:
                    break

            next_page_token = response.get(
                "nextPageToken"
            )

            if not next_page_token:
                break

            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token,
                order=youtube_order,
            )

        return valid_comments, total_found
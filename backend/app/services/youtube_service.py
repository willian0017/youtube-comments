from googleapiclient.discovery import build

from app.core.config import YOUTUBE_API_KEY


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
    ):
        comments = []

        request = self.youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            order=order,
        )

        while request and len(comments) < max_comments:
            response = request.execute()

            for item in response.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]

                comments.append({
                    "id": item["id"],
                    "author": snippet["authorDisplayName"],
                    "text": snippet["textDisplay"],
                    "likes": snippet["likeCount"],
                    "published_at": snippet["publishedAt"],
                })

                if len(comments) >= max_comments:
                    break

            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token,
                order="relevance",
            )

        return comments
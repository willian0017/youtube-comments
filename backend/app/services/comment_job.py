import threading
import uuid

from app.services.youtube_service import YouTubeService


class CommentJobManager:

    def __init__(self):
        self.jobs = {}
        self.lock = threading.Lock()
        self.youtube_service = YouTubeService()

    def create_job(
        self,
        video_id: str,
        max_comments: int,
        order: str,
        remove_emoji_only: bool,
        remove_empty: bool,
        remove_links: bool,
        remove_duplicates: bool,
    ) -> str:

        job_id = str(uuid.uuid4())

        with self.lock:
            self.jobs[job_id] = {
                "status": "pending",
                "video_id": video_id,
                "target": max_comments,
                "processed": 0,
                "total_found": 0,
                "comments": [],
                "error": None,
            }

        thread = threading.Thread(
            target=self._run_job,
            args=(
                job_id,
                video_id,
                max_comments,
                order,
                remove_emoji_only,
                remove_empty,
                remove_links,
                remove_duplicates,
            ),
            daemon=True,
        )

        thread.start()

        return job_id

    def _run_job(
        self,
        job_id: str,
        video_id: str,
        max_comments: int,
        order: str,
        remove_emoji_only: bool,
        remove_empty: bool,
        remove_links: bool,
        remove_duplicates: bool,
    ):
        self.jobs[job_id]["status"] = "running"

        try:
            comments, total_found = (
                self.youtube_service.get_comments(
                    video_id=video_id,
                    max_comments=max_comments,
                    order=order,
                    remove_emoji_only=remove_emoji_only,
                    remove_empty=remove_empty,
                    remove_links=remove_links,
                    remove_duplicates=remove_duplicates,
                    progress_callback=lambda processed: (
                        self._update_progress(
                            job_id,
                            processed,
                        )
                    ),
                )
            )

            with self.lock:
                self.jobs[job_id]["comments"] = comments
                self.jobs[job_id]["total_found"] = total_found
                self.jobs[job_id]["processed"] = len(comments)
                self.jobs[job_id]["status"] = "completed"

        except Exception as error:
            with self.lock:
                self.jobs[job_id]["status"] = "error"
                self.jobs[job_id]["error"] = str(error)

    def _update_progress(
        self,
        job_id: str,
        processed: int,
    ):
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id]["processed"] = processed

    def get_job(self, job_id: str):
        with self.lock:
            job = self.jobs.get(job_id)

            if not job:
                return None

            return {
                "status": job["status"],
                "video_id": job["video_id"],
                "target": job["target"],
                "processed": job["processed"],
                "total_found": job["total_found"],
                "total_after_filters": len(
                    job["comments"]
                ),
                "comments": (
                    job["comments"]
                    if job["status"] == "completed"
                    else []
                ),
                "error": job["error"],
            }


comment_job_manager = CommentJobManager()
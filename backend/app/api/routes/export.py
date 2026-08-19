from io import BytesIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openpyxl import Workbook

from app.core.auth import require_auth


router = APIRouter(
    prefix="/export",
    tags=["Export"],
)


@router.post(
    "/excel",
    dependencies=[Depends(require_auth)],
)
def export_excel(data: dict):
    comments = data.get("comments", [])
    video_id = data.get("video_id", "youtube")

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Comentários"

    worksheet.append([
        "ID",
        "Autor",
        "Comentário",
        "Curtidas",
        "Publicado em",
    ])

    for comment in comments:
        worksheet.append([
            comment.get("id", ""),
            comment.get("author", ""),
            comment.get("text", ""),
            comment.get("likes", 0),
            comment.get("published_at", ""),
        ])

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    filename = f"youtube-comments-{video_id}.xlsx"

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument"
            ".spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )
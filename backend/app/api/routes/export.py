from io import BytesIO

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from fastapi import APIRouter, Depends
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
    video_id = data.get("video_id")
    comments = data.get("comments", [])

    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Comentários"

    headers = [
        "Autor",
        "Comentário",
        "Curtidas",
        "Data",
        "Link",
    ]

    worksheet.append(headers)

    # Cabeçalho
    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="E5E7EB",
        )
        cell.alignment = Alignment(
            horizontal="center",
        )

    # Comentários
    for comment in comments:

        comment_id = comment.get("id", "")

        comment_url = ""

        if video_id and comment_id:
            comment_url = (
                f"https://www.youtube.com/watch"
                f"?v={video_id}"
                f"&lc={comment_id}"
            )

        worksheet.append([
            comment.get("author", ""),
            comment.get("text", ""),
            comment.get("likes", 0),
            comment.get("published_at", ""),
            comment_url,
        ])

    # Largura das colunas
    widths = {
        1: 25,
        2: 80,
        3: 12,
        4: 25,
        5: 60,
    }

    for column, width in widths.items():
        worksheet.column_dimensions[
            get_column_letter(column)
        ].width = width

    # Formatação
    for row in worksheet.iter_rows(min_row=2):

        row[1].alignment = Alignment(
            wrap_text=True,
            vertical="top",
        )

        if row[4].value:
            row[4].hyperlink = row[4].value
            row[4].style = "Hyperlink"

    worksheet.freeze_panes = "A2"

    # Arquivo em memória
    file = BytesIO()

    workbook.save(file)

    file.seek(0)

    return StreamingResponse(
        file,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                'attachment; filename="youtube-comments.xlsx"'
        },
    )
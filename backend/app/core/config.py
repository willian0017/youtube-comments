import os

from dotenv import load_dotenv

load_dotenv()


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

ACCESS_PASSWORD = os.getenv(
    "ACCESS_PASSWORD",
    "",
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "",
)

if not YOUTUBE_API_KEY:
    raise RuntimeError(
        "YOUTUBE_API_KEY não configurada"
    )
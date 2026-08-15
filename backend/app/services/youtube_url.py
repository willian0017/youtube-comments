from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> str | None:
    parsed = urlparse(url)

    if parsed.hostname in {"www.youtube.com", "youtube.com"}:
        query = parse_qs(parsed.query)

        return query.get("v", [None])[0]

    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/").split("/")[0]

    return None
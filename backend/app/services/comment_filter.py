import re


class CommentFilter:

    @staticmethod
    def is_empty(text: str) -> bool:
        return not text.strip()

    @staticmethod
    def is_emoji_only(text: str) -> bool:
        text = text.strip()

        if not text:
            return False

        cleaned = re.sub(
            r"[\s\W_]+",
            "",
            text,
            flags=re.UNICODE,
        )

        if not cleaned:
            return True

        return not bool(
            re.search(
                r"[a-zA-ZÀ-ÿ0-9]",
                cleaned,
            )
        )

    @staticmethod
    def contains_link(text: str) -> bool:
        return bool(
            re.search(
                r"(https?://|www\.)",
                text,
                re.IGNORECASE,
            )
        )

    @staticmethod
    def remove_duplicates(
        comments: list[dict],
    ) -> list[dict]:

        seen = set()
        result = []

        for comment in comments:
            normalized = (
                comment["text"]
                .strip()
                .lower()
            )

            if normalized in seen:
                continue

            seen.add(normalized)
            result.append(comment)

        return result

    @classmethod
    def apply(
        cls,
        comments: list[dict],
        remove_emoji_only: bool = True,
        remove_empty: bool = True,
        remove_links: bool = False,
        remove_duplicates: bool = False,
    ) -> list[dict]:

        result = []

        for comment in comments:
            text = comment["text"]

            if (
                remove_empty
                and cls.is_empty(text)
            ):
                continue

            if (
                remove_emoji_only
                and cls.is_emoji_only(text)
            ):
                continue

            if (
                remove_links
                and cls.contains_link(text)
            ):
                continue

            result.append(comment)

        if remove_duplicates:
            result = cls.remove_duplicates(result)

        return result
from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from tools._shared import err, fold_text


TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid"}
VALID_STRATEGIES = {"url_or_title", "url", "title"}


def _canonical_url(value: Any) -> str:
    url = str(value or "").strip()
    if not url:
        return ""

    parts = urlsplit(url)
    query = [
        (key, item)
        for key, item in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_PARAMS
    ]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), ""))


def _canonical_title(value: Any) -> str:
    return " ".join(fold_text(str(value or "")).split())


def deduplicate_results(
    items: list[dict[str, Any]] | None = None,
    strategy: str = "url_or_title",
) -> dict[str, Any]:
    """Keep the first research item for each canonical URL or title."""
    try:
        if items is None:
            items = []
        if not isinstance(items, list):
            raise TypeError("items must be a list of objects")
        if strategy not in VALID_STRATEGIES:
            raise ValueError(f"strategy must be one of: {', '.join(sorted(VALID_STRATEGIES))}")

        unique: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        seen_titles: set[str] = set()

        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise TypeError(f"items[{index}] must be an object")

            canonical_url = _canonical_url(item.get("url"))
            canonical_title = _canonical_title(item.get("title"))
            duplicate_url = bool(canonical_url and canonical_url in seen_urls)
            duplicate_title = bool(canonical_title and canonical_title in seen_titles)

            if strategy == "url":
                is_duplicate = duplicate_url
            elif strategy == "title":
                is_duplicate = duplicate_title
            else:
                is_duplicate = duplicate_url or duplicate_title

            if is_duplicate:
                continue

            unique.append(item)
            if canonical_url:
                seen_urls.add(canonical_url)
            if canonical_title:
                seen_titles.add(canonical_title)

        return {
            "tool": "deduplicate_results",
            "strategy": strategy,
            "items": unique,
            "original_count": len(items),
            "unique_count": len(unique),
            "removed_count": len(items) - len(unique),
        }
    except Exception as exc:
        return err("deduplicate_results", exc)

"""Job search module — DuckDuckGo search + page content extraction."""

import json
import logging
from typing import Any

import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
}


def search_jobs(
    query: str,
    location: str,
    num_results: int = 10,
) -> list[dict[str, str]]:
    """Search for job listings using DuckDuckGo.

    Runs targeted queries to maximise coverage across job boards.
    Returns list of dicts with keys: title, url, snippet.
    """
    capped = min(num_results, 25)

    queries = [
        f"{query} jobs {location} hiring 2026",
        f"{query} stelle {location} site:stepstone.de OR site:indeed.de OR site:linkedin.com",
    ]

    seen_urls: set[str] = set()
    results: list[dict[str, str]] = []

    with DDGS() as ddgs:
        for search_query in queries:
            if len(results) >= capped:
                break
            try:
                for r in ddgs.text(search_query, max_results=capped):
                    url = r.get("href", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        results.append({
                            "title": r.get("title", ""),
                            "url": url,
                            "snippet": r.get("body", ""),
                        })
            except Exception as e:
                logger.warning("Search query failed (%s): %s", search_query, e)

    if not results:
        return [{"error": "Search returned no results. The search engine may be temporarily unavailable. Please try again or search manually on LinkedIn, StepStone, or Indeed."}]

    return results[:capped]


def get_page_content(url: str, max_chars: int = 6000) -> str:
    """Fetch a URL and return cleaned text content."""
    try:
        resp = httpx.get(
            url,
            headers=_HEADERS,
            follow_redirects=True,
            timeout=20,
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error("HTTP error fetching %s: %s", url, e)
        return f"Error fetching page: {e}"
    except Exception as e:
        logger.error("Unexpected error fetching %s: %s", url, e)
        return f"Error fetching page: {e}"

    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(
        ["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]
    ):
        tag.decompose()

    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(attrs={"role": "main"})
        or soup.find(class_=lambda c: c and "job" in str(c).lower())
        or soup.body
        or soup
    )

    text = main.get_text(separator="\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    content = "\n".join(lines)

    if len(content) > max_chars:
        content = content[:max_chars] + "\n...[truncated]"

    return content


def execute_search(tool_input: dict[str, Any]) -> str:
    """Entry point called by the bot's tool dispatcher."""
    query = tool_input.get("query", "")
    location = tool_input.get("location", "")
    num = tool_input.get("num_results", 10)

    results = search_jobs(query, location, num)
    return json.dumps(results, ensure_ascii=False, indent=2)


def execute_get_details(tool_input: dict[str, Any]) -> str:
    """Entry point called by the bot's tool dispatcher."""
    url = tool_input.get("url", "")
    if not url:
        return "Error: No URL provided."
    return get_page_content(url)

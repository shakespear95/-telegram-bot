"""Job search module — web search + page content extraction.

Uses DuckDuckGo HTML search via httpx (no extra dependencies)
and BeautifulSoup to extract job posting details from URLs.
"""

import json
import logging
import re
from typing import Any
from urllib.parse import quote_plus, unquote

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
}


def _ddg_search(query: str, max_results: int = 10) -> list[dict[str, str]]:
    """Search DuckDuckGo HTML version and extract results."""
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    results: list[dict[str, str]] = []

    try:
        resp = httpx.get(url, headers=_HEADERS, follow_redirects=True, timeout=20)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error("DuckDuckGo search failed: %s", e)
        return results

    soup = BeautifulSoup(resp.text, "html.parser")

    for result_div in soup.select(".result"):
        if len(results) >= max_results:
            break

        link_tag = result_div.select_one(".result__a")
        snippet_tag = result_div.select_one(".result__snippet")

        if not link_tag:
            continue

        raw_href = link_tag.get("href", "")
        # DuckDuckGo wraps URLs — extract the actual URL
        actual_url = _extract_ddg_url(raw_href)
        if not actual_url:
            continue

        title = link_tag.get_text(strip=True)
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

        results.append({
            "title": title,
            "url": actual_url,
            "snippet": snippet,
        })

    return results


def _extract_ddg_url(href: str) -> str:
    """Extract the real URL from a DuckDuckGo redirect link."""
    if not href:
        return ""
    # Direct URL
    if href.startswith("http") and "duckduckgo.com" not in href:
        return href
    # DDG redirect format: //duckduckgo.com/l/?uddg=ENCODED_URL&...
    match = re.search(r"uddg=([^&]+)", href)
    if match:
        return unquote(match.group(1))
    return ""


def search_jobs(
    query: str,
    location: str,
    num_results: int = 10,
) -> list[dict[str, str]]:
    """Search for job listings using multiple DuckDuckGo queries.

    Runs targeted queries to maximise coverage across
    major job boards and general results.

    Returns list of dicts with keys: title, url, snippet.
    """
    capped = min(num_results, 25)

    queries = [
        f"{query} jobs {location} hiring 2025 2026",
        f"{query} stelle {location}",  # German keyword for local results
        f"{query} {location} linkedin.com/jobs OR stepstone.de OR indeed.com",
    ]

    seen_urls: set[str] = set()
    results: list[dict[str, str]] = []

    for search_query in queries:
        if len(results) >= capped:
            break
        try:
            raw = _ddg_search(search_query, max_results=capped)
            for r in raw:
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    results.append(r)
        except Exception as e:
            logger.warning("Search query failed (%s): %s", search_query, e)

    if not results:
        return [{"error": "No results found. Try broadening your search terms."}]

    return results[:capped]


def get_page_content(url: str, max_chars: int = 6000) -> str:
    """Fetch a URL and return cleaned text content.

    Strips navigation, scripts, and other boilerplate to isolate
    the main content — ideal for extracting job posting details.
    """
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

    # Remove non-content elements
    for tag in soup(
        ["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]
    ):
        tag.decompose()

    # Try to find the main content area first
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

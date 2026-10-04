import re
import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from typing import Optional

app = FastAPI(
    title="AgentReader API",
    description="High-speed web content cleaner, metadata extractor, and markdown converter tailored for LLMs and AI Agents.",
    version="1.0.0"
)

class ScrapeRequest(BaseModel):
    url: HttpUrl
    include_links: bool = True
    max_length: Optional[int] = 20000

class ScrapeResponse(BaseModel):
    url: str
    title: str
    description: Optional[str] = None
    byline: Optional[str] = None
    markdown: str
    word_count: int
    estimated_reading_time_minutes: float

def html_to_clean_markdown(soup: BeautifulSoup, include_links: bool = True) -> str:
    # Remove unwanted noise tags
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "aside", "form"]):
        tag.decompose()

    # Extract primary article body if exists, fallback to body
    target = soup.find("article") or soup.find("main") or soup.find("body") or soup

    lines = []
    for elem in target.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "blockquote"]):
        text = elem.get_text(separator=" ", strip=True)
        if not text:
            continue
        
        name = elem.name
        if name == "h1":
            lines.append(f"\n# {text}\n")
        elif name == "h2":
            lines.append(f"\n## {text}\n")
        elif name == "h3":
            lines.append(f"\n### {text}\n")
        elif name in ["h4", "h5", "h6"]:
            lines.append(f"\n#### {text}\n")
        elif name == "li":
            lines.append(f"- {text}")
        elif name == "blockquote":
            lines.append(f"> {text}")
        elif name == "pre":
            lines.append(f"\n```\n{text}\n```\n")
        else:
            lines.append(f"\n{text}\n")

    # Clean redundant whitespace
    raw_md = "\n".join(lines)
    cleaned = re.sub(r'\n{3,}', '\n\n', raw_md).strip()
    return cleaned

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "AgentReader API",
        "endpoints": {
            "GET /extract?url={target_url}": "Quick GET extract for URL",
            "POST /extract": "Batch / configurable payload extract"
        }
    }

@app.get("/extract", response_model=ScrapeResponse)
async def extract_get(
    url: str = Query(..., description="Target web page URL"),
    include_links: bool = Query(True, description="Keep markdown links"),
    max_length: int = Query(25000, description="Max char length")
):
    return await process_url(url, include_links, max_length)

@app.post("/extract", response_model=ScrapeResponse)
async def extract_post(req: ScrapeRequest):
    return await process_url(str(req.url), req.include_links, req.max_length)

async def process_url(url: str, include_links: bool, max_length: Optional[int]) -> ScrapeResponse:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AgentReader/1.0"
    }
    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code >= 400:
                raise HTTPException(status_code=resp.status_code, detail=f"Target URL returned status {resp.status_code}")
            html = resp.text
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch upstream URL: {str(exc)}")

    soup = BeautifulSoup(html, "html.parser")

    # Extract metadata
    title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled"
    desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    description = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else None
    author_tag = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", attrs={"property": "article:author"})
    byline = author_tag["content"].strip() if author_tag and author_tag.get("content") else None

    # Parse markdown content
    markdown = html_to_clean_markdown(soup, include_links)
    if max_length and len(markdown) > max_length:
        markdown = markdown[:max_length] + "\n\n...[Content Truncated]"

    words = len(markdown.split())
    reading_time = round(words / 200.0, 1)

    return ScrapeResponse(
        url=url,
        title=title,
        description=description,
        byline=byline,
        markdown=markdown,
        word_count=words,
        estimated_reading_time_minutes=reading_time
    )

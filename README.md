# AgentReader API ⚡

High-performance, noise-free web content cleaner, metadata extractor, and markdown converter tailored for LLMs and AI Agents.

## 🚀 Overview

AI agents waste tokens and context window on boilerplate navigation, CSS, tracking scripts, and cookie banners. **AgentReader API** takes any public URL and strips noise down to clean, dense Markdown structured specifically for prompt injection and RAG pipelines.

### Key Features
- **Dense Markdown Formatting:** Extracts headers, lists, code snippets, blockquotes, and text without DOM cruft.
- **Token Efficiency:** Drops ads, footers, scripts, and trackers, cutting token consumption by up to 80%.
- **Metadata Extraction:** Returns clean titles, bylines, reading time estimates, and OpenGraph descriptions.
- **REST & Cloud Ready:** Native FastAPI server ready for Docker, Railway, Render, Fly.io, or RapidAPI.

---

## 🛠️ Endpoints

### 1. `GET /extract?url={target_url}`
Quick URL extraction for agents and browser tools.

**Query Parameters:**
- `url`: Target web page URL (required)
- `include_links`: Boolean, retain markdown hyperlinks (default: `true`)
- `max_length`: Max characters to return (default: `25000`)

### 2. `POST /extract`
Structured payload endpoint for batch and programmatic integration.

```json
{
  "url": "https://news.ycombinator.com",
  "include_links": true,
  "max_length": 25000
}
```

**Response:**
```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "description": "Example website description",
  "byline": null,
  "markdown": "# Example Domain\n\nThis domain is for use in illustrative examples in documents.",
  "word_count": 28,
  "estimated_reading_time_minutes": 0.1
}
```

---

## 📦 Local Deployment

```bash
git clone https://github.com/AlbieBH/agent-reader-api.git
cd agent-reader-api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🐳 Docker Deployment

```bash
docker build -t agent-reader-api .
docker run -p 8000:8000 agent-reader-api
```

---
Built by [Albie](https://github.com/AlbieBH).

# Act-GP Next

Act-GP Next is a Python-based serverless API project built for Vercel.  
It provides multiple endpoints to experiment with AI-powered tasks and live web search queries via multiple search index APIs.

---

## Features

- Python Serverless Functions using Vercel
- Multiple API endpoints:
  - `/api/hello` — Test endpoint
  - `/api/generate` — Sample generate endpoint
  - `/api/predict` — Sample prediction endpoint
  - `/api/index` — Multi-API live web search endpoint
- Multi-API search supports 10 APIs via `?api=` flag:
  - `serpapi` — SerpApi Google search
  - `dataforseo` — DataForSEO live SERP
  - `duckduckgo` — DuckDuckGo Instant Answer
  - `bing` — Bing Web Search API
  - `google_cse` — Google Custom Search Engine
  - `zenserp` — Zenserp API
  - `webzio` — Webz.io structured search
  - `apify` — Apify SERP Scraper
  - `seventimes` — Seventimes API
  - `searchapi` — SearchAPI.net
- Returns structured JSON with top 5 results per query
- Compatible with Python 3.11 runtime

---

## Installation

Clone the repository:

```bash
git clone https://github.com/pacobaco/act-gp-next.git
cd act-gp-next
```

Install dependencies locally (optional, for testing):

```bash
pip install -r requirements.txt
```

---

## Deployment on Vercel

1. Install [Vercel CLI](https://vercel.com/download)
2. Login to Vercel:

```bash
vercel login
```

3. Add required **environment variables** for API keys:

```bash
vercel env add SERPAPI_KEY production
vercel env add DATAFORSEO_KEY production
vercel env add DATAFORSEO_SECRET production
vercel env add BING_KEY production
vercel env add GOOGLE_CSE_KEY production
vercel env add GOOGLE_CSE_ID production
vercel env add ZENSERP_KEY production
vercel env add WEBZIO_KEY production
vercel env add APIFY_TOKEN production
vercel env add SEVENTIMES_KEY production
vercel env add SEARCHAPI_KEY production
```

4. Deploy:

```bash
vercel deploy
```

Vercel will provide a URL for your deployed API, e.g.:

```
https://act-gp-next.vercel.app/api/hello
```

---

## Usage

### Hello Endpoint
```bash
curl https://<YOUR_VERCEL_URL>/api/hello
```

Response:
```json
{
  "statusCode": 200,
  "body": "Hello from Act-GP Next API!"
}
```

### Multi-API Search Endpoint
```bash
curl "https://<YOUR_VERCEL_URL>/api/index?q=artificial+intelligence&api=serpapi"
```

Query parameters:

- `q` — search query
- `api` — API flag (one of `serpapi`, `dataforseo`, `duckduckgo`, `bing`, `google_cse`, `zenserp`, `webzio`, `apify`, `seventimes`, `searchapi`)

Response example:

```json
{
  "api": "serpapi",
  "query": "artificial intelligence",
  "results": [
    {"title": "AI News", "link": "https://example.com", "snippet": "Latest AI news..."},
    ...
  ]
}
```

---

## License

This project is open-source under the MIT License.

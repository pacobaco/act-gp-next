import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------------------------
# Environment Variables
# -------------------------
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
DATAFORSEO_KEY = os.environ.get("DATAFORSEO_KEY")
DATAFORSEO_SECRET = os.environ.get("DATAFORSEO_SECRET")
BING_KEY = os.environ.get("BING_KEY")
GOOGLE_CSE_KEY = os.environ.get("GOOGLE_CSE_KEY")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID")
ZENSERP_KEY = os.environ.get("ZENSERP_KEY")
WEBZIO_KEY = os.environ.get("WEBZIO_KEY")
APIFY_TOKEN = os.environ.get("APIFY_TOKEN")
SEVENTIMES_KEY = os.environ.get("SEVENTIMES_KEY")
SEARCHAPI_KEY = os.environ.get("SEARCHAPI_KEY")
GROK_API_KEY = os.environ.get("GROK_API_KEY")

SUPPORTED_APIS = {
    "serpapi", "dataforseo", "duckduckgo", "bing", "google_cse",
    "zenserp", "webzio", "apify", "seventimes", "searchapi"
}

def handler(request):
    query = request.args.get("q")
    apis_str = request.args.get("apis")
    api_flag = request.args.get("api", "serpapi")  # backward compat
    num_results = min(int(request.args.get("num_results", 5)), 15)
    language = request.args.get("language", "en")
    country = request.args.get("country", "us")
    safe_search = request.args.get("safe_search", "true").lower() in ("true", "1", "yes")
    summarize = request.args.get("summarize", "false").lower() in ("true", "1", "yes")

    if not query:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing query parameter 'q'"}, ensure_ascii=False)}

    if apis_str:
        apis = [a.strip().lower() for a in apis_str.split(",") if a.strip().lower() in SUPPORTED_APIS]
    else:
        api_flag = api_flag.lower()
        apis = [api_flag] if api_flag in SUPPORTED_APIS else ["serpapi"]

    if not apis:
        apis = ["serpapi"]

    # Parallel calls
    results_by_provider = {}
    with ThreadPoolExecutor(max_workers=len(apis)) as executor:
        future_to_api = {
            executor.submit(call_provider, api, query, num_results, language, country, safe_search): api
            for api in apis
        }
        for future in as_completed(future_to_api):
            api = future_to_api[future]
            try:
                results_by_provider[api] = future.result().get("results", [])
            except Exception as e:
                results_by_provider[api] = {"error": str(e)}

    # Normalize and flatten
    all_results = []
    global_rank = 1
    for provider, res in results_by_provider.items():
        if isinstance(res, dict) and "error" in res:
            continue
        for item in res[:num_results]:
            normalized = {
                "provider": provider,
                "rank": global_rank,
                "title": item.get("title") or item.get("name") or item.get("Heading") or "",
                "link": item.get("link") or item.get("url") or item.get("FirstURL") or item.get("AbstractURL") or "",
                "snippet": item.get("snippet") or item.get("text") or item.get("AbstractText") or item.get("description") or ""
            }
            all_results.append(normalized)
            global_rank += 1

    total_requested = num_results * len(apis)
    response_body = {
        "query": query,
        "apis_used": list(results_by_provider.keys()),
        "num_results_requested": num_results,
        "results": all_results[:total_requested]
    }

    # Optional Grok AI summary
    if summarize and GROK_API_KEY and all_results:
        try:
            summary = generate_summary(query, all_results[:10], language)
            response_body["summary"] = summary
        except Exception as e:
            response_body["summary"] = f"Summary generation failed: {str(e)}"

    return {
        "statusCode": 200,
        "body": json.dumps(response_body, ensure_ascii=False)
    }

def call_provider(api, query, num_results, language, country, safe_search):
    if api == "serpapi":
        return serpapi_search(query, num_results, language, country, safe_search)
    elif api == "dataforseo":
        return dataforseo_search(query, num_results, language, country)
    elif api == "duckduckgo":
        return duckduckgo_search(query, num_results)
    elif api == "bing":
        return bing_search(query, num_results, language)
    elif api == "google_cse":
        return google_cse_search(query, num_results)
    elif api == "zenserp":
        return zenserp_search(query, num_results, language, country)
    elif api == "webzio":
        return webzio_search(query, num_results)
    elif api == "apify":
        return apify_search(query, num_results)
    elif api == "seventimes":
        return seventimes_search(query, num_results)
    elif api == "searchapi":
        return searchapi_search(query, num_results)
    return {"results": []}

# ------------------------- Provider Implementations -------------------------

def serpapi_search(query, num_results, language, country, safe_search):
    if not SERPAPI_KEY:
        raise ValueError("SERPAPI_KEY not set")
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": num_results,
        "hl": language,
        "gl": country,
        "safe": "active" if safe_search else "off"
    }
    resp = requests.get("https://serpapi.com/search", params=params, timeout=12)
    resp.raise_for_status()
    data = resp.json()
    results = [
        {"title": r.get("title"), "link": r.get("link"), "snippet": r.get("snippet")}
        for r in data.get("organic_results", [])[:num_results]
    ]
    return {"results": results}

def dataforseo_search(query, num_results, language, country):
    if not DATAFORSEO_KEY or not DATAFORSEO_SECRET:
        raise ValueError("DATAFORSEO_KEY or SECRET not set")
    payload = [{
        "keyword": query,
        "location_name": "United States" if country.upper() == "US" else country.upper(),
        "language_name": "English" if language == "en" else language,
        "device": "desktop",
        "os": "windows",
        "depth": num_results
    }]
    resp = requests.post(
        "https://api.dataforseo.com/v3/serp/google/organic/live/regular",
        auth=(DATAFORSEO_KEY, DATAFORSEO_SECRET),
        json=payload,
        timeout=15
    )
    resp.raise_for_status()
    data = resp.json()
    items = data.get("tasks", [{}])[0].get("result", [{}])[0].get("items", [])[:num_results]
    results = [
        {"title": i.get("title"), "link": i.get("url"), "snippet": i.get("snippet")}
        for i in items if i.get("type") == "organic"
    ]
    return {"results": results}

def duckduckgo_search(query, num_results):
    resp = requests.get(
        "https://api.duckduckgo.com/",
        params={"q": query, "format": "json", "no_redirect": 1, "skip_disambig": 1, "kl": "wt-wt"},
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    results = []
    if data.get("AbstractURL"):
        results.append({
            "title": data.get("Heading", query),
            "link": data.get("AbstractURL"),
            "snippet": data.get("AbstractText", "")
        })
    for topic in data.get("RelatedTopics", [])[:num_results - len(results)]:
        if topic.get("FirstURL"):
            results.append({
                "title": topic.get("Text", ""),
                "link": topic.get("FirstURL"),
                "snippet": ""
            })
    return {"results": results[:num_results]}

def bing_search(query, num_results, language):
    if not BING_KEY:
        raise ValueError("BING_KEY not set")
    mkt = f"{language}-{country.upper()}" if country else f"{language}-US"
    resp = requests.get(
        "https://api.bing.microsoft.com/v7.0/search",
        headers={"Ocp-Apim-Subscription-Key": BING_KEY},
        params={"q": query, "count": num_results, "mkt": mkt, "safeSearch": "Strict" if safe_search else "Off"},
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    results = [
        {"title": r.get("name"), "link": r.get("url"), "snippet": r.get("snippet")}
        for r in data.get("webPages", {}).get("value", [])[:num_results]
    ]
    return {"results": results}

def google_cse_search(query, num_results):
    if not GOOGLE_CSE_KEY or not GOOGLE_CSE_ID:
        raise ValueError("GOOGLE_CSE_KEY or ID not set")
    resp = requests.get(
        "https://www.googleapis.com/customsearch/v1",
        params={"q": query, "key": GOOGLE_CSE_KEY, "cx": GOOGLE_CSE_ID, "num": num_results},
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    results = [
        {"title": r.get("title"), "link": r.get("link"), "snippet": r.get("snippet")}
        for r in data.get("items", [])[:num_results]
    ]
    return {"results": results}

def zenserp_search(query, num_results, language, country):
    if not ZENSERP_KEY:
        raise ValueError("ZENSERP_KEY not set")
    params = {
        "q": query,
        "apikey": ZENSERP_KEY,
        "num": num_results,
        "hl": language,
        "gl": country
    }
    resp = requests.get("https://app.zenserp.com/api/v2/search", params=params, timeout=12)
    resp.raise_for_status()
    data = resp.json()
    results = [
        {"title": r.get("title"), "link": r.get("url"), "snippet": r.get("snippet")}
        for r in data.get("organic", [])[:num_results]
    ]
    return {"results": results}

def webzio_search(query, num_results):
    if not WEBZIO_KEY:
        raise ValueError("WEBZIO_KEY not set")
    resp = requests.get(
        "https://api.webz.io/filtered-web-content",
        params={"token": WEBZIO_KEY, "q": query, "size": num_results},
        timeout=12
    )
    resp.raise_for_status()
    data = resp.json()
    results = [
        {"title": r.get("title"), "link": r.get("url"), "snippet": r.get("text")}
        for r in data.get("posts", [])[:num_results]
    ]
    return {"results": results}

def apify_search(query, num_results):
    if not APIFY_TOKEN:
        raise ValueError("APIFY_TOKEN not set")
    # Uses a pre-configured Google Search task (adjust task name if needed)
    resp = requests.get(
        "https://api.apify.com/v2/actor-tasks/google-search/run-sync-get-dataset",
        params={"token": APIFY_TOKEN, "q": query, "maxItems": num_results},
        timeout=30  # Apify can be slower
    )
    resp.raise_for_status()
    data = resp.json()
    results = [
        {"title": r.get("title"), "link": r.get("url"), "snippet": r.get("description", "")}
        for r in data[:num_results]
    ]
    return {"results": results}

def seventimes_search(query, num_results):
    if not SEVENTIMES_KEY:
        raise ValueError("SEVENTIMES_KEY not set")
    resp = requests.get(
        "https://api.seventimes.com/search",
        headers={"Authorization": f"Bearer {SEVENTIMES_KEY}"},
        params={"q": query, "limit": num_results},
        timeout=12
    )
    resp.raise_for_status()
    data = resp.json()
    results = [
        {"title": r.get("title"), "link": r.get("link"), "snippet": r.get("snippet", "")}
        for r in data.get("results", [])[:num_results]
    ]
    return {"results": results}

def searchapi_search(query, num_results):
    if not SEARCHAPI_KEY:
        raise ValueError("SEARCHAPI_KEY not set")
    resp = requests.get(
        "https://api.searchapi.io/search",
        params={"q": query, "api_key": SEARCHAPI_KEY, "num": num_results},
        timeout=12
    )
    resp.raise_for_status()
    data = resp.json()
    results = [
        {"title": r.get("title"), "link": r.get("url"), "snippet": r.get("snippet", "")}
        for r in data.get("organic_results", [])[:num_results]
    ]
    return {"results": results}

def generate_summary(query, results, language):
    if not GROK_API_KEY:
        raise ValueError("GROK_API_KEY not set")
    snippets = "\n".join([f"{r['title']}: {r['snippet'][:300]}" for r in results if r.get("snippet")])
    prompt = (
        f"Summarize the most important findings from these top search results about '{query}' "
        f"in 4-6 concise bullet points. Respond in {language.upper()} language:\n\n{snippets}"
    )
    resp = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "grok-beta",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 400
        },
        timeout=15
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
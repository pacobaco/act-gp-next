import os
import json
import requests

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


def handler(request):
    # Get query and API flag
    query = request.args.get("q") if hasattr(request, "args") else None
    api_flag = request.args.get("api") if hasattr(request, "args") else "serpapi"

    if not query:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing query parameter 'q'"})}

    # Dispatch to API functions
    try:
        if api_flag.lower() == "serpapi":
            return serpapi_search(query)
        elif api_flag.lower() == "dataforseo":
            return dataforseo_search(query)
        elif api_flag.lower() == "duckduckgo":
            return duckduckgo_search(query)
        elif api_flag.lower() == "bing":
            return bing_search(query)
        elif api_flag.lower() == "google_cse":
            return google_cse_search(query)
        elif api_flag.lower() == "zenserp":
            return zenserp_search(query)
        elif api_flag.lower() == "webzio":
            return webzio_search(query)
        elif api_flag.lower() == "apify":
            return apify_search(query)
        elif api_flag.lower() == "seventimes":
            return seventimes_search(query)
        elif api_flag.lower() == "searchapi":
            return searchapi_search(query)
        else:
            return {"statusCode": 400, "body": json.dumps({"error": f"Unknown API flag '{api_flag}'"})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# -------------------------
# Individual API Functions
# -------------------------
def serpapi_search(query):
    if not SERPAPI_KEY:
        return {"statusCode": 500, "body": json.dumps({"error": "SERPAPI_KEY not set"})}
    resp = requests.get(
        "https://serpapi.com/search",
        params={"q": query, "api_key": SERPAPI_KEY, "engine": "google"}
    )
    data = resp.json()
    results = [{"title": r.get("title"), "link": r.get("link"), "snippet": r.get("snippet")} 
               for r in data.get("organic_results", [])[:5]]
    return {"statusCode": 200, "body": json.dumps({"api": "serpapi", "query": query, "results": results})}


def dataforseo_search(query):
    if not DATAFORSEO_KEY or not DATAFORSEO_SECRET:
        return {"statusCode": 500, "body": json.dumps({"error": "DATAFORSEO_KEY or SECRET not set"})}
    resp = requests.get(
        "https://api.dataforseo.com/v3/serp/google/organic/live/regular",
        auth=(DATAFORSEO_KEY, DATAFORSEO_SECRET),
        params={"q": query, "location_name": "United States", "language_name": "English"}
    )
    data = resp.json()
    results = [{"title": r.get("title"), "link": r.get("url")} 
               for r in data.get("tasks", [{}])[0].get("result", [])[:5]]
    return {"statusCode": 200, "body": json.dumps({"api": "dataforseo", "query": query, "results": results})}


def duckduckgo_search(query):
    resp = requests.get(
        "https://api.duckduckgo.com/",
        params={"q": query, "format": "json", "no_redirect": 1, "skip_disambig": 1}
    )
    data = resp.json()
    results = []
    if data.get("AbstractURL"):
        results.append({"title": data.get("Heading"), "link": data.get("AbstractURL"), "snippet": data.get("AbstractText")})
    for topic in data.get("RelatedTopics", [])[:5]:
        if "Text" in topic and "FirstURL" in topic:
            results.append({"title": topic["Text"], "link": topic["FirstURL"], "snippet": ""})
    return {"statusCode": 200, "body": json.dumps({"api": "duckduckgo", "query": query, "results": results})}


def bing_search(query):
    if not BING_KEY:
        return {"statusCode": 500, "body": json.dumps({"error": "BING_KEY not set"})}
    resp = requests.get(
        "https://api.bing.microsoft.com/v7.0/search",
        headers={"Ocp-Apim-Subscription-Key": BING_KEY},
        params={"q": query}
    )
    data = resp.json()
    results = [{"title": r.get("name"), "link": r.get("url"), "snippet": r.get("snippet")} 
               for r in data.get("webPages", {}).get("value", [])[:5]]
    return {"statusCode": 200, "body": json.dumps({"api": "bing", "query": query, "results": results})}


def google_cse_search(query):
    if not GOOGLE_CSE_KEY or not GOOGLE_CSE_ID:
        return {"statusCode": 500, "body": json.dumps({"error": "GOOGLE_CSE_KEY or ID not set"})}
    resp = requests.get(
        "https://www.googleapis.com/customsearch/v1",
        params={"q": query, "key": GOOGLE_CSE_KEY, "cx": GOOGLE_CSE_ID}
    )
    data = resp.json()
    results = [{"title": r.get("title"), "link": r.get("link"), "snippet": r.get("snippet")} 
               for r in data.get("items", [])[:5]]
    return {"statusCode": 200, "body": json.dumps({"api": "google_cse", "query": query, "results": results})}


def zenserp_search(query):
    if not ZENSERP_KEY:
        return {"statusCode": 500, "body": json.dumps({"error": "ZEN_SERP_KEY not set"})}
    resp = requests.get(
        "https://app.zenserp.com/api/v2/search",
        params={"q": query, "apikey": ZENSERP_KEY}
    )
    data = resp.json()
    results = [{"title": r.get("title"), "link": r.get("url"), "snippet": r.get("snippet")} 
               for r in data.get("organic", [])[:5]]
    return {"statusCode": 200, "body": json.dumps({"api": "zenserp", "query": query, "results": results})}


def webzio_search(query):
    if not WEBZIO_KEY:
        return {"statusCode": 500, "body": json.dumps({"error": "WEBZIO_KEY not set"})}
    resp = requests.get(
        "https://api.webz.io/v1/search",
        headers={"Authorization": f"Bearer {WEBZIO_KEY}"},
        params={"q": query, "size": 5}
    )
    data = resp.json()
    results = [{"title": r.get("title"), "link": r.get("url"), "snippet": r.get("text")} 
               for r in data.get("articles", [])]
    return {"statusCode": 200, "body": json.dumps({"api": "webzio", "query": query, "results": results})}


def apify_search(query):
    if not APIFY_TOKEN:
        return {"statusCode": 500, "body": json.dumps({"error": "APIFY_TOKEN not set"})}
    resp = requests.get(
        "https://api.apify.com/v2/actor-tasks/google-search/run-sync-get-dataset",
        params={"token": APIFY_TOKEN, "q": query, "maxItems": 5}
    )
    data = resp.json()
    results = [{"title": r.get("title"), "link": r.get("url")} for r in data.get("items", [])]
    return {"statusCode": 200, "body": json.dumps({"api": "apify", "query": query, "results": results})}


def seventimes_search(query):
    if not SEVENTIMES_KEY:
        return {"statusCode": 500, "body": json.dumps({"error": "SEVENTIMES_KEY not set"})}
    resp = requests.get(
        "https://api.seventimes.com/search",
        headers={"Authorization": f"Bearer {SEVENTIMES_KEY}"},
        params={"q": query, "limit": 5}
    )
    data = resp.json()
    results = [{"title": r.get("title"), "link": r.get("link")} for r in data.get("results", [])]
    return {"statusCode": 200, "body": json.dumps({"api": "seventimes", "query": query, "results": results})}


def searchapi_search(query):
    if not SEARCHAPI_KEY:
        return {"statusCode": 500, "body": json.dumps({"error": "SEARCHAPI_KEY not set"})}
    resp = requests.get(
        "https://api.searchapi.net/search",
        headers={"Authorization": f"Bearer {SEARCHAPI_KEY}"},
        params={"q": query, "size": 5}
    )
    data = resp.json()
    results = [{"title": r.get("title"), "link": r.get("url")} for r in data.get("items", [])]
    return {"statusCode": 200, "body": json.dumps({"api": "searchapi", "query": query, "results": results})}
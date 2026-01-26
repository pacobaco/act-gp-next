import json
from flask import Flask, request, jsonify
from http.server import BaseHTTPRequestHandler  # For compatibility if needed
import requests  # For Brave API calls

app = Flask(__name__)

# Brave API Config (use env var for key)
import os
API_KEY = os.environ.get("BRAVE_API_KEY", "YOUR_BRAVE_API_KEY")  # Set this in Vercel env vars
BASE_URL = "https://api.search.brave.com/res/v1"

VERTICALS = {
    "web": "/web/search",
    "images": "/images/search",
    "news": "/news/search",
    "videos": "/videos/search"
}

def analyze_query(query: str) -> str:
    if "image" in query.lower() or "picture" in query.lower():
        return "images"
    elif "news" in query.lower() or "recent" in query.lower():
        return "news"
    elif "video" in query.lower():
        return "videos"
    return "web"

def search_vertical(query: str, vertical: str = "web", count: int = 10) -> list:
    endpoint = VERTICALS.get(vertical, "/web/search")
    headers = {"X-Subscription-Token": API_KEY}
    params = {"q": query, "count": count, "country": "us", "search_lang": "en"}
    response = requests.get(BASE_URL + endpoint, headers=headers, params=params)
    
    if response.status_code == 200:
        results_key = 'results' if vertical != 'web' else 'web.results'
        data = response.json()
        results = data.get(vertical, {}).get('results', []) if vertical == 'web' else data.get('results', [])
        return results
    return []

def plan_steps(query: str) -> list:
    if "compare" in query.lower():
        parts = query.split("compare")[1].split("and")
        return [f"Search for {part.strip()}" for part in parts] + ["Summarize comparison"]
    return [query, "Summarize results"]

def execute_search_step(step: str, vertical: str):
    if "Summarize" in step:
        # Simplified summary (could use Brave chat if integrated)
        return f"Summary of {step}: (Agentic logic here - expand with LLM if needed)"
    else:
        results = search_vertical(step, vertical, count=5)
        return "\n".join([f"{r['title']}: {r['description']}" for r in results])

@app.route('/search', methods=['GET', 'POST'])
def agentic_search():
    query = request.args.get('query') or request.json.get('query') if request.json else None
    if not query:
        return jsonify({"error": "Query parameter required"}), 400
    
    vertical = analyze_query(query)
    steps = plan_steps(query)
    context = ""
    for step in steps:
        result = execute_search_step(step, vertical)
        context += f"Step: {step}\nResult: {result}\n\n"
    
    return jsonify({"query": query, "results": context})

@app.route('/', methods=['GET'])
def home():
    return "Agentic Search Engine API is running!"

# For Vercel compatibility (optional if using app)
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Hello from Vercel!')

if __name__ == '__main__':
    app.run()

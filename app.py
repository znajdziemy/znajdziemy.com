from flask import Flask, request, jsonify, render_template
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SERPAPI_KEY = "c9c658199f6d702f0b0bc5986f16d5c5a0dd7a384a188cc045f88b2686f221e4"
ALLEGRO_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJhbGxlZ3JvOmFwaTpzYWxlOm9mZmVyczpyZWFkIl0sImFsbGVncm9fYXBpIjp0cnVlLCJpc3MiOiJodHRwczovL2FsbGVncm8ucGwiLCJleHAiOjE3NTM0NjAwOTUsImp0aSI6IjNkOWY2MWM4LWYxNzAtNGNlNy04YzQ3LWU0MTRhZmE4ZTA1ZCIsImNsaWVudF9pZCI6IjZmZTI3ZGQwOTNmMTQwZDc4ODBlZDA5ZDgzMGYwYmYyIn0.XiZbZx-xRsuKea2jEv5tBq5KJFGyxjE7fDugOIuP4weL8JUVu1-XDpoZwJXZ2Wn4tGNKjtWm3rYmTRBlnBXQutq_66pt01IE7SYf9hvi52xw0kKjsg8VN3WHGxHjFT5HuEl0A0KALHc_R6HEhH04jwQoXxsp9Uk45hp4-KVQ13NofaDCG5pbtuL8oGqFswLKLMVV8q6qyfoOctce8lqTwT_b6KdGn_-WfTLAwRKBbhilwgI6-g8YsOaKiKw2gjCvpZcGlHv2ndTh2ui5WcrtZ9Q_tzwJe5QkUInrMLWA2oxNW9fRQu5rJMbs0Nx2tPQb0sZh03yBxgycXDY579i6xA"


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/search")
def search():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Brak zapytania"}), 400

    results = []

    # SerpAPI
    serp = requests.get("https://serpapi.com/search.json", params={
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "gl": "pl",
        "hl": "pl"
    })
    if serp.ok:
        for item in serp.json().get("shopping_results", []):
            results.append({
                "title": item.get("title"),
                "price": item.get("price"),
                "link": item.get("link"),
                "source": "SerpAPI"
            })

    # Allegro
    allegro = requests.get("https://api.allegro.pl/offers/listing", params={
        "phrase": query,
        "limit": 5
    }, headers={
        "Authorization": f"Bearer {ALLEGRO_TOKEN}",
        "Accept": "application/vnd.allegro.public.v1+json"
    })
    if allegro.ok:
        for item in allegro.json().get("items", {}).get("regular", {}).get("items", []):
            results.append({
                "title": item.get("name"),
                "price": item.get("sellingMode", {}).get("price", {}).get("amount"),
                "link": item.get("product", {}).get("id", "#"),
                "source": "Allegro"
            })

    return jsonify({"results": results})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


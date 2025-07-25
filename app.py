from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import base64

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

CLIENT_ID = "6fe27dd093f140d7880ed09d830f0bf2"
CLIENT_SECRET = "e0YaBEO3yMAFlCjOlOCaF7W3lGHGmHRF"
SERPAPI_KEY = "c9c658199f6d702f0b0bc5986f16d5c5a0dd7a384a188cc045f88b2686f221e4"

# Automatyczne pobieranie tokena Allegro
def get_allegro_token():
    url = "https://allegro.pl/auth/oauth/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token", None)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/search')
def search():
    query = request.args.get("q")
    results = []
    
    try:
        token = get_allegro_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.allegro.public.v1+json"
        }
        params = {"phrase": query, "limit": 5}
        res = requests.get("https://api.allegro.pl/offers/listing", headers=headers, params=params)
        offers = res.json().get("items", {}).get("regular", [])
        for item in offers:
            results.append({
                "title": item.get("name"),
                "price": item.get("sellingMode", {}).get("price", {}).get("amount", "brak"),
                "link": item.get("permalink"),
                "source": "Allegro"
            })
    except Exception as e:
        print("Allegro error:", e)

    try:
        serpapi_res = requests.get("https://serpapi.com/search.json", params={
            "q": query,
            "engine": "google",
            "api_key": SERPAPI_KEY
        }).json()
        for item in serpapi_res.get("shopping_results", [])[:5]:
            results.append({
                "title": item.get("title"),
                "price": item.get("price"),
                "link": item.get("link"),
                "source": "Google"
            })
    except Exception as e:
        print("SerpAPI error:", e)

    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

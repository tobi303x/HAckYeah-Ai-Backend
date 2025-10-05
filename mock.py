from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import chromadb
from chromadb.api.models.Collection import Collection
from google import genai
from typing import Dict, Any
import os
import uuid
import requests

# ----------------- Load environment -----------------
load_dotenv()

# ----------------- Flask setup -----------------
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # allow Polish chars

# Security headers middleware
@app.after_request
def apply_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Rate limiter (prevent abuse)
limiter = Limiter(get_remote_address, app=app, default_limits=["60 per minute"])

# ----------------- Initialize clients -----------------
chroma_client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE")
)
gemini_client = genai.Client(api_key=os.getenv("GOOGLE_GENAI_KEY"))

COLLECTION_NAME = "Ogloszenia"
collection: Collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# ----------------- API Key Auth -----------------
API_KEY = os.getenv("API_KEY") or "super-secret-key"

def require_api_key():
    key = request.headers.get("x-api-key")
    if not key or key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

# ----------------- Allowed values -----------------
ALLOWED_TAGS = [
    "Rynek mieszkaniowy", "Zieleń i klimat", "Jakość powietrza", "Potrzeby kierowców",
    "Potrzeby rowerzystów", "Potrzeby pieszych", "Komunikacja miejska", "Edukcja",
    "Zdrowie", "Oferta społeczno-kulturalna miasta", "Zwierzęta", "Seniorzy i seniorki",
    "Transparentność działań urzędów", "Usługi komunalne (np. woda, śmieci)"
]
ALLOWED_WORKLOAD = [
    "Mini - Zaangażowanie do 1 godziny tygodniowo",
    "Lekkie - Zaangażowanie 1-4 godziny tygodniowo",
    "Umiarkowane - Zaangażowanie 4-8 godzin tygodniowo",
    "Pełne - Zaangażowanie ponad 8 godzin tygodniowo"
]
ALLOWED_FORM = [
    "Zostań aktywistą online", "Dbaj o potrzeby dzielnicy", "Weź udział w akcjach bezpośrednich",
    "Spotkaj się z mieszkańcami", "Zaangażuj się w obywatelską kontrolę",
    "Wesprzyj pogotowie obywatelskie"
]

# ----------------- Helpers -----------------
def parse_date(date_str: str):
    for fmt in ("%Y-%m-%d", "%d:%m:%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except Exception:
            continue
    return None

def matches_filter(value: str, query_value: str) -> bool:
    return query_value.lower() in str(value).lower()

def generate_embedding(text: str) -> list[float]:
    result = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values

def validate_payload(data: Dict[str, Any]) -> Dict[str, str]:
    required_fields = [
        "title", "description", "tags", "thumbnail",
        "lon", "lat", "start_date", "end_date", "workload", "form", "organizer"
    ]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return {"error": f"Missing fields: {', '.join(missing)}"}

    # Validate allowed lists
    for field, allowed in [
        ("tags", ALLOWED_TAGS),
        ("workload", ALLOWED_WORKLOAD),
        ("form", ALLOWED_FORM)
    ]:
        if not isinstance(data[field], list):
            return {"error": f"{field} must be a list."}
        invalid = [v for v in data[field] if v not in allowed]
        if invalid:
            return {"error": f"Invalid values in {field}: {', '.join(invalid)}"}

    return {}

def get_city_from_coords(lat: float, lon: float) -> str:
    """Use OpenStreetMap Nominatim to get city from coordinates."""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10}
    try:
        resp = requests.get(url, params=params, headers={"User-Agent": "FlaskApp"})
        resp.raise_for_status()
        data = resp.json()
        return data.get("address", {}).get("city") or data.get("address", {}).get("town") or "Unknown"
    except Exception:
        return "Unknown"

# ----------------- Endpoint: Add -----------------
@app.route("/add_opportunity", methods=["POST"])
@limiter.limit("10/minute")
def add_opportunity():
    auth = require_api_key()
    if auth: return auth

    data = request.json or {}
    validation = validate_payload(data)
    if validation:
        return jsonify(validation), 400

    record_id = str(uuid.uuid4())

    # Determine city from lat/lon
    city = get_city_from_coords(float(data["lat"]), float(data["lon"]))

    metadata = {
        "Nazwa": data["title"],
        "Tags": ", ".join(data["tags"]),
        "Thumbnail": data["thumbnail"],
        "Lokalizacja": city,
        "Data rozpoczęcia": data["start_date"],
        "Data zakończenia": data["end_date"],
        "Wymagania nakładu pracy": ", ".join(data["workload"]),
        "Preferowana forma działalności": ", ".join(data["form"]),
        "Nazwa organizatora": data["organizer"]
    }

    try:
        embedding = generate_embedding(data["description"])
        collection.add(
            documents=[data["description"]],
            metadatas=[metadata],
            ids=[record_id],
            embeddings=[embedding]
        )
        return jsonify({"status": "success", "record_id": record_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- Endpoint: Query -----------------
@app.route("/query", methods=["GET"])
@limiter.limit("30/minute")
def query_opportunities():
    auth = require_api_key()
    if auth: return auth

    text_query = request.args.get("text")
    filters = {
        "Nazwa": request.args.get("title"),
        "Lokalizacja": request.args.get("location"),
        "Tags": request.args.get("tags"),
        "Preferowana forma działalności": request.args.get("form"),
        "Wymagania nakładu pracy": request.args.get("workload"),
    }

    # Validate filters
    if filters["Wymagania nakładu pracy"] and filters["Wymagania nakładu pracy"] not in ALLOWED_WORKLOAD:
        return jsonify({"error": "Invalid workload", "allowed": ALLOWED_WORKLOAD}), 400
    if filters["Preferowana forma działalności"] and filters["Preferowana forma działalności"] not in ALLOWED_FORM:
        return jsonify({"error": "Invalid form", "allowed": ALLOWED_FORM}), 400
    if filters["Tags"] and filters["Tags"] not in ALLOWED_TAGS:
        return jsonify({"error": "Invalid tags", "allowed": ALLOWED_TAGS}), 400

    # Date filters
    start_date_from = parse_date(request.args.get("start_date_from", ""))
    start_date_to = parse_date(request.args.get("start_date_to", ""))
    end_date_from = parse_date(request.args.get("end_date_from", ""))
    end_date_to = parse_date(request.args.get("end_date_to", ""))

    try:
        # If semantic query
        if text_query:
            embedding = generate_embedding(text_query)
            results = collection.query(query_embeddings=[embedding], n_results=25)
            docs = [
                {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
                for i in range(len(results["ids"][0]))
            ]
        else:
            results = collection.get()
            docs = [
                {
                    "id": results["ids"][i],
                    "document": results["documents"][i],
                    "metadata": results["metadatas"][i],
                }
                for i in range(len(results["ids"]))
            ]

        matched = []
        for doc in docs:
            meta = doc["metadata"]
            ok = True
            for field, value in filters.items():
                if value and (field not in meta or not matches_filter(meta[field], value)):
                    ok = False
                    break
            if not ok:
                continue

            # Date range filters
            meta_start = parse_date(meta.get("Data rozpoczęcia", ""))
            meta_end = parse_date(meta.get("Data zakończenia", ""))
            if start_date_from and (not meta_start or meta_start < start_date_from):
                continue
            if start_date_to and (not meta_start or meta_start > start_date_to):
                continue
            if end_date_from and (not meta_end or meta_end < end_date_from):
                continue
            if end_date_to and (not meta_end or meta_end > end_date_to):
                continue

            matched.append(doc)

        return jsonify({
            "count": len(matched),
            "results": matched
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------- Run -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)

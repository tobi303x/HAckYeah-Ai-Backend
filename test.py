from flask import Flask, request, jsonify
from dotenv import load_dotenv
import chromadb
from chromadb.api.models.Collection import Collection
from google import genai
from datetime import datetime
import os

# ----------------- Load environment variables -----------------
load_dotenv()

# ----------------- Initialize clients -----------------
chroma_client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE")
)
gemini_client = genai.Client(api_key=os.getenv("GOOGLE_GENAI_KEY"))

COLLECTION_NAME = "Ogloszenia"
collection: Collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# ----------------- Flask app -----------------
app = Flask(__name__)

# ----------------- Allowed filter values -----------------
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

ALLOWED_TAGS = [
    "Rynek mieszkaniowy", "Zieleń i klimat", "Jakość powietrza", "Potrzeby kierowców",
    "Potrzeby rowerzystów", "Potrzeby pieszych", "Komunikacja miejska", "Edukcja",
    "Zdrowie", "Oferta społeczno-kulturalna miasta", "Zwierzęta", "Seniorzy i seniorki",
    "Transparentność działań urzędów", "Usługi komunalne (np. woda, śmieci)"
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

# ----------------- /query endpoint -----------------
@app.route("/query", methods=["GET"])
def query_opportunities():
    """
    Example:
    /query?location=Warszawa&tags=Zwierzęta&form=Zostań aktywistą online
           &workload=Mini - Zaangażowanie do 1 godziny tygodniowo
           &start_date_from=2025-09-01&start_date_to=2025-12-31
    """
    text_query = request.args.get("text")

    filters = {
        "Nazwa": request.args.get("title"),
        "Lokalizacja": request.args.get("location"),
        "Tags": request.args.get("tags"),
        "Preferowana forma działalności": request.args.get("form"),
        "Wymagania nakładu pracy": request.args.get("workload"),
    }

    # Validate allowed values
    if filters["Wymagania nakładu pracy"] and filters["Wymagania nakładu pracy"] not in ALLOWED_WORKLOAD:
        return jsonify({"error": "Nieprawidłowa wartość workload", "allowed": ALLOWED_WORKLOAD}), 400
    if filters["Preferowana forma działalności"] and filters["Preferowana forma działalności"] not in ALLOWED_FORM:
        return jsonify({"error": "Nieprawidłowa wartość form", "allowed": ALLOWED_FORM}), 400
    if filters["Tags"] and filters["Tags"] not in ALLOWED_TAGS:
        return jsonify({"error": "Nieprawidłowa wartość tags", "allowed": ALLOWED_TAGS}), 400

    # Parse date filters
    start_date_from = parse_date(request.args.get("start_date_from", ""))
    start_date_to = parse_date(request.args.get("start_date_to", ""))
    end_date_from = parse_date(request.args.get("end_date_from", ""))
    end_date_to = parse_date(request.args.get("end_date_to", ""))

    try:
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

            # Field filters
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
    app.run(host="0.0.0.0", port=5001, debug=True)

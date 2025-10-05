from flask import Flask, request, jsonify
from dotenv import load_dotenv
import chromadb
from chromadb.api.models.Collection import Collection
from google import genai
from typing import Dict, Any
import os
import uuid

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

# ----------------- Allowed values for multi-picklists -----------------
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

# ----------------- Validation helper -----------------
def validate_payload(data: Dict[str, Any]) -> Dict[str, str]:
    required_fields = [
        "title", "description", "tags", "thumbnail", "location",
        "start_date", "end_date", "workload", "form", "organizer"
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return {"error": f"Missing fields: {', '.join(missing)}"}

    # Validate multi-picklists
    for field, allowed in [("tags", ALLOWED_TAGS), ("workload", ALLOWED_WORKLOAD), ("form", ALLOWED_FORM)]:
        if not isinstance(data[field], list):
            return {"error": f"{field} must be a list."}
        invalid_values = [v for v in data[field] if v not in allowed]
        if invalid_values:
            return {"error": f"Invalid values in {field}: {', '.join(invalid_values)}"}
    
    return {}

# ----------------- Embedding helper -----------------
def generate_embedding(text: str) -> list[float]:
    result = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values

# ----------------- Add record to ChromaDB -----------------
def add_record_to_chroma(record_id: str, document: str, metadata: Dict[str, Any], embedding: list[float]):
    collection.add(
        documents=[document],
        metadatas=[metadata],
        ids=[record_id],
        embeddings=[embedding]
    )

# ----------------- API endpoint -----------------
@app.route("/add_opportunity", methods=["POST"])
def add_opportunity():
    data = request.json
    validation_error = validate_payload(data)
    if validation_error:
        return jsonify(validation_error), 400

    # Generate unique ID
    record_id = str(uuid.uuid4())

    # Prepare metadata
    metadata: Dict[str, Any] = {
        "Nazwa": data["title"],
        "Tags": ", ".join(data["tags"]),
        "Thumbnail": data["thumbnail"],
        "Lokalizacja": data["location"],
        "Data rozpoczęcia": data["start_date"],
        "Data zakończenia": data["end_date"],
        "Wymagania nakładu pracy": ", ".join(data["workload"]),
        "Preferowana forma działalności": ", ".join(data["form"]),
        "Nazwa organizatora": data["organizer"]
    }

    try:
        embedding = generate_embedding(data["description"])
        add_record_to_chroma(record_id, data["description"], metadata, embedding)
        return jsonify({"status": "success", "record_id": record_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ----------------- Run Flask -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

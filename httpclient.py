import chromadb
from chromadb.config import Settings
import sys

# --- 1. Client Setup ---
try:
    client = chromadb.HttpClient(
        host="13.48.129.238",
        port=8000,
        settings=Settings(
            chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
            chroma_client_auth_credentials="sk-chuj-ci-na-kurwe"
        )
    )

    # --- 2. Collections Listing ---
    print("--- Listing All Collections on Server ---")
    collection_names = client.list_collections()

    if not collection_names:
        print("No collections found.")
    else:
        # Loop through each collection name and fetch its details
        for name in collection_names:
            collection = client.get_collection(name)
            print(f"- Name: {collection.name} | ID: {collection.id}")
            
except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
    sys.exit(1)
# embed_team_scouting.py

import os
import json
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "team-scouting"
MODEL_NAME = "all-MiniLM-L6-v2"
JSON_PATH = "data/json/team_scouting_data.json"

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if it doesn't exist
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Connect to index
index = pc.Index(INDEX_NAME)

# Load embedding model
model = SentenceTransformer(MODEL_NAME)

# Load and embed JSON data
def embed_team_scouting():
    with open(JSON_PATH, "r") as f:
        data = json.load(f)

    for i, entry in enumerate(data):
        team = entry["team"]
        year = entry["year"]
        summary = entry["summary"]

        embedding = model.encode(summary).tolist()

        metadata = {
            "team": team,
            "year": str(year),
            "summary": summary,
            "source": "team_scouting"
        }

        uid = f"{team}_{year}_{i}"
        index.upsert([(uid, embedding, metadata)])

if __name__ == "__main__":
    embed_team_scouting()
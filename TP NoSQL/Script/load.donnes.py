import time
import requests
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import os
from datetime import datetime

# Charger les variables d'environnement (.env)
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# URL de l'API : ici 10 blagues aléatoires
API_URL = os.getenv("API_URL")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def fetch_jokes():
    """Récupère des blagues depuis l'API."""
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    jokes = resp.json()
    # L’API renvoie déjà une liste d’objets JSON [web:100]
    return jokes

def upsert_jokes(jokes):
    """Insère ou met à jour les blagues dans MongoDB."""
    ops = []
    now = datetime.utcnow().isoformat()

    for j in jokes:
        # Ajout d’un timestamp d’ingestion
        j["ingestion_timestamp"] = now

        # L’API a un champ 'id' unique par blague
        ops.append(
            UpdateOne(
                {"id": j["id"]},     # critère de recherche
                {"$set": j},         # données à mettre à jour
                upsert=True          # insert si pas trouvé
            )
        )

    if ops:
        result = collection.bulk_write(ops)  # écriture groupée [web:119][web:122]
        print(
            f"[{now}] upsert terminé : "
            f"{result.upserted_count} insérés, {result.modified_count} modifiés"
        )

def run_every_minute():
    """Boucle infinie qui interroge l'API toutes les 60 secondes."""
    while True:
        try:
            jokes = fetch_jokes()
            print(f"Récupéré {len(jokes)} blagues depuis l'API.")
            upsert_jokes(jokes)
        except Exception as e:
            print("Erreur lors de l'exécution du cycle :", e)

        # Attendre 60 secondes
        time.sleep(60)

if __name__ == "__main__":
    run_every_minute()

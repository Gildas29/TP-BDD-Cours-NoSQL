import time
import requests
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import os
from datetime import datetime, UTC

# Charger les variables d'environnement (.env)
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME_DB")
COLLECTION_NAME = os.getenv("COLLECTION_NAME_DB")

# URL de l'API : ici 10 blagues aléatoires
API_URL = os.getenv("API_URL_DB")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def fetch_characters():
    """Récupère les personnages depuis l'API Dragon Ball."""
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # Debug léger pour vérifier la structure
    # print(type(data), data[:2] if isinstance(data, list) else data)

    # D'après la doc, /api/characters renvoie une liste de personnages. [web:145][web:169]
    if isinstance(data, list):
        return data
    # Si jamais l'API renvoie un objet avec une clé 'items' ou 'data'
    if isinstance(data, dict):
        for key in ("items", "data", "results"):
            if key in data and isinstance(data[key], list):
                return data[key]

    raise ValueError(f"Format de réponse inattendu depuis l'API : {type(data)}")

def upsert_characters(characters):
    """Insère ou met à jour les personnages dans MongoDB."""
    ops = []
    now = datetime.now(UTC).isoformat()  # remplace utcnow() pour éviter le warning. [web:162][web:164]

    for c in characters:
        # On ne traite que les dicts
        if not isinstance(c, dict):
            print("Élément ignoré (pas un dict) :", c)
            continue

        char_id = c.get("id")
        if char_id is None:
            print("Personnage sans id, ignoré :", c.get("name"))
            continue

        # Ajout d’un timestamp d’ingestion
        c["ingestion_timestamp"] = now

        ops.append(
            UpdateOne(
                {"id": char_id},   # critère de recherche
                {"$set": c},       # données à mettre à jour
                upsert=True        # insert si pas trouvé
            )
        )

    if ops:
        result = collection.bulk_write(ops)
        print(
            f"[{now}] upsert terminé : "
            f"{result.upserted_count} insérés, {result.modified_count} modifiés"
        )
    else:
        print(f"[{now}] aucune opération à effectuer (liste vide ou éléments invalides).")

def run_every_minute():
    """Boucle infinie qui interroge l'API toutes les 60 secondes."""
    while True:
        try:
            characters = fetch_characters()
            print(f"Récupéré {len(characters)} personnages depuis l'API.")
            upsert_characters(characters)
        except Exception as e:
            print("Erreur lors de l'exécution du cycle :", e)

        # Attendre 60 secondes
        time.sleep(60)

if __name__ == "__main__":
    if not MONGO_URI:
        raise ValueError("MONGO_URI manquant dans le fichier .env")
    run_every_minute()
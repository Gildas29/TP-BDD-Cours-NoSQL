# collector/dragonball_collector.py
import time
import requests
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import os
from datetime import datetime, UTC  # Python 3.12+

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
API_URL = os.getenv("API_URL")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def fetch_characters():
    """Récupère les personnages depuis l'API Dragon Ball."""
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # D’après la doc, /api/characters renvoie une liste de personnages. [web:145][web:169]
    if isinstance(data, list):
        return data

    # Si jamais l'API renvoie un objet {"items": [...] } ou similaire.
    if isinstance(data, dict):
        for key in ("items", "data", "results"):
            if key in data and isinstance(data[key], list):
                return data[key]

    raise ValueError(f"Format de réponse inattendu depuis l'API : {type(data)}")


def clean_character(raw: dict) -> dict:
    """Nettoie et normalise un personnage brut de l'API."""
    if not isinstance(raw, dict):
        return None

    # Champs typiques de l'API Dragon Ball (à adapter si nécessaire). [web:169]
    name = str(raw.get("name", "")).strip()
    race = str(raw.get("affiliation", raw.get("race", ""))).strip()
    ki = raw.get("ki", 0)
    max_ki = raw.get("maxKi", 0)
    description = str(raw.get("description", "")).strip()
    gender = str(raw.get("gender", "")).strip()
    image = raw.get("image", "")

    # Normalisation des types numériques
    try:
        ki = float(ki) if ki is not None else 0.0
    except (ValueError, TypeError):
        ki = 0.0

    try:
        max_ki = float(max_ki) if max_ki is not None else 0.0
    except (ValueError, TypeError):
        max_ki = 0.0

    cleaned = {
        "name": name,
        "race": race,
        "gender": gender,
        "ki": ki,
        "max_ki": max_ki,
        "description": description,
        "image": image,
    }

    # Suppression des champs vides
    cleaned = {k: v for k, v in cleaned.items() if v not in ("", None)}

    return cleaned


def upsert_characters(characters):
    """Insère ou met à jour les personnages dans MongoDB (après nettoyage)."""
    ops = []
    now = datetime.now(UTC).isoformat()

    for raw in characters:
        if not isinstance(raw, dict):
            continue

        char_id = raw.get("id")
        if char_id is None:
            continue

        doc = clean_character(raw)
        if doc is None:
            continue

        # On garde l'id de l'API pour les upserts
        doc["api_id"] = char_id
        doc["ingestion_timestamp"] = now

        ops.append(
            UpdateOne(
                {"api_id": char_id},  # clé de recherche
                {"$set": doc},        # données nettoyées
                upsert=True,
            )
        )

    if ops:
        result = collection.bulk_write(ops)
        print(
            f"[{now}] upsert terminé : "
            f"{result.upserted_count} insérés, {result.modified_count} modifiés"
        )
    else:
        print(f"[{now}] aucune opération à effectuer.")


def run_every_minute():
    """Boucle infinie qui interroge l'API toutes les 60 secondes."""
    while True:
        try:
            characters = fetch_characters()
            print(f"Récupéré {len(characters)} personnages depuis l'API.")
            upsert_characters(characters)
        except Exception as e:
            print("Erreur lors de l'exécution du cycle :", e)

        time.sleep(60)


if __name__ == "__main__":
    if not MONGO_URI:
        raise ValueError("MONGO_URI manquant dans le fichier .env")
    run_every_minute()
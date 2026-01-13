from pymongo import MongoClient
from dotenv import load_dotenv
import os

def test_mongo_connection():
    # Charge les variables d'environnement depuis .env
    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")

    if not mongo_uri:
        print("❌ MONGO_URI manquant dans le fichier .env")
        return

    try:
        client = MongoClient(mongo_uri)
        # Ping pour vérifier la connexion
        client.admin.command("ping")
        print("✅ Connexion à MongoDB Atlas réussie !")

        if db_name:
            db = client[db_name]
            print(f"✅ Accès à la base : {db.name}")
        else:
            print("ℹ️ Aucun nom de base (MONGO_DB_NAME) spécifié, mais la connexion fonctionne.")

    except Exception as e:
        print("❌ Erreur de connexion à MongoDB :", e)

if __name__ == "__main__":
    test_mongo_connection()

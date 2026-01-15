from pymongo import MongoClient
from dotenv import load_dotenv
import os

def get_users():
    # Charger les variables d'environnement
    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")  # ta chaîne Atlas
    db_name = os.getenv("MONGO_DB_NAME")
    col_users = os.getenv("SAMPLE_MFLIX_USERS")
    if not mongo_uri:
        raise ValueError("MONGO_URI manquant dans le fichier .env")

    # Connexion au cluster
    client = MongoClient(mongo_uri)

    # Sélection de la base et de la collection
    db = client[db_name]
    users_collection = db[col_users]

    # Récupérer tous les documents
    users_cursor = users_collection.find({})  # équivalent SELECT * [web:100][web:101]

    # Convertir en liste (attention si beaucoup de données)
    users = list(users_cursor)

    # Afficher quelques utilisateurs pour vérifier
    for user in users[:10]:
        print(user)

    print(f"Nombre total d'utilisateurs : {len(users)}")

    return users

if __name__ == "__main__":
    get_users()

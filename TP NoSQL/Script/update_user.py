from pymongo import MongoClient
from dotenv import load_dotenv
import os

def update_user():
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

    # Ajoute un user dans la collection 'users'
    db.users.update_one(
        { "name": "Gildas" },
        {'$set' :
         {'password': 'test2'}
        } 
    )

if __name__ == "__main__":
    update_user()

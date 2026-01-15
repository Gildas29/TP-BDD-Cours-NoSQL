# db/mongo.py
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

_client = None


def get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client


def get_collection():
    client = get_client()
    db = client[DB_NAME]
    return db[COLLECTION_NAME]


def get_all_characters():
    col = get_collection()
    docs = list(col.find({}))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs


def get_character_by_id(doc_id: str):
    col = get_collection()
    return col.find_one({"_id": ObjectId(doc_id)})


def insert_character(data: dict):
    col = get_collection()
    res = col.insert_one(data)
    return str(res.inserted_id)


def update_character(doc_id: str, data: dict):
    col = get_collection()
    col.update_one({"_id": ObjectId(doc_id)}, {"$set": data})


def delete_character(doc_id: str):
    col = get_collection()
    col.delete_one({"_id": ObjectId(doc_id)})

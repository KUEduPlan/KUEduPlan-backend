from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def connect_client():
    mongo_url = os.getenv("MONGO_URL")
    client = MongoClient(mongo_url)
    return client


def connect_mongo(database_name: str):
    mongo_url = os.getenv("MONGO_URL")
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_url)
        db = client.get_database(database_name)
        print("Already connect with database")
        return db

    except Exception as e:
        print(e)
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
import os

load_dotenv()
mongo_url = os.getenv("MONGO_URL")

def connect_client():
    client = MongoClient(mongo_url, tlsCAFile=certifi.where())
    return client


def connect_mongo(database_name: str):
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_url, tlsCAFile=certifi.where())
        db = client.get_database(database_name)
        print("Already connect with database")
        return db

    except Exception as e:
        print(e)
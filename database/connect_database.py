from pymongo import MongoClient


def connect_client():
    client = MongoClient("mongodb://localhost:27017")
    return client


def connect_mongo(database_name: str):
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017")
        db = client.get_database(database_name)
        print("Already connect with database")
        return db

    except Exception as e:
        print(e)

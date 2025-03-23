from http import client
import stream_chat
from database.connect_database import connect_mongo
import os
import datetime

def server():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    server_client = stream_chat.StreamChat(
    api_key=f"{api_key }", api_secret=f"{api_secret}"
    )
    return server_client

def eduplan_tokens(student_code):
    server_client = server()
    expire_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
    tokens = server_client.create_token(student_code, exp=expire_time)
    return tokens, expire_time


def insert_student_tokens(student_code, tokens, expire_time):
    db = connect_mongo("Student")
    collection = db["StudentTokens"]
    data = {
        "StdID": student_code,
        "Tokens": tokens,
        "ExpireTime": expire_time
    }
    existing_data = collection.find_one({"StdID":student_code})
    if existing_data:
        collection.replace_one({"StdID":student_code}, data)
        return "Replace Tokens"
    else:
        collection.insert_one(data)
        return "Already insert tokens"

def revoke_tokens(student_code, tokens):
    db = connect_mongo("Student")
    collection = db["StudentTokens"]
    data = {
        "StdID": student_code,
        "Tokens": "",
        "ExpireTime": datetime.datetime.now()
    }
    existing_data = collection.find_one({"StdID":student_code})
    print(existing_data)
    if existing_data:
        collection.replace_one({"StdID":student_code}, data)

    return "Revoke user tokens"

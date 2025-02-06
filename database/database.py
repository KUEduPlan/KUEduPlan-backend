from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from eduplan.api.connect_api import *
from eduplan.database.curriculumn_database import *
from eduplan.database.student_database import *
from eduplan.database.connect_database import connect_client


app = FastAPI()
client = connect_client()

password = ""
username = ""
student_code = ""

def main():
    try:
        token = request_token(password, username)
        verify_token(token)

    except Exception as e:
        print(e)

    # insert_plan_list(student_code, client, token)
    insert_student_enrollment(student_code, token)


# Run the script
if __name__ == "__main__":
    main()

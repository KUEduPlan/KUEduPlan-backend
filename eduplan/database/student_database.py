from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from eduplan.api.connect_api import *
from eduplan.api.student_data import * 
from eduplan.database.connect_database import connect_mongo

def insert_or_replace_database(collection_name: str, student_code: str, data: dict):
    db = connect_mongo("Student")
    collection = db[collection_name]
    existing_data = collection.find_one({"student_code":student_code})
    
    if existing_data:
        # Replace existing data
        collection.replace_one({"student_code":student_code}, data)
    else:
        # Insert new data
        collection.insert_one(data)


def insert_student_status(student_code: str, token):
    collection_name = "StudentStatus"
    data = student_status(student_code, token)
    try:
        insert_or_replace_database(collection_name, student_code, data)

        return "Already insert student status"
    except Exception as e:
        return e
    
def insert_student_enrollment(student_code: str, token):
    collection_name = "StudentEnrollment"
    try:
        data = student_enrollment(student_code, token)
        inserted_data = {
            "student_code": student_code,
            "enrollment": data
        }
        if not data:
            raise ValueError("No data returned from student_enrollment function")
        insert_or_replace_database(collection_name, student_code, inserted_data)
        return "Already insert student enrollment"
    except Exception as e:
        print(f"Error in insert_student_enrollment: {e}")
        return e

def insert_student_grades(student_code: str, token):
    collection_name = "StudentGrades"
    try:
        data = student_grades(student_code, token)
        inserted_data = {
            "student_code": student_code,
            "grades": data
        }
        if not data:
            raise ValueError("No data returned from student_grades function")
        insert_or_replace_database(collection_name, student_code, inserted_data)
        return "Already insert student grades"
    except Exception as e:
        print(f"Error in insert_student_grades: {e}")
        return e

def insert_or_replace_open_plan_database(collection_name: str, plan_id:int, data: dict):
    db = connect_mongo("Plan")
    collection = db[collection_name]
    existing_data = collection.find_one({"Plan_ID":plan_id})
    
    if existing_data:
        # Replace existing data
        collection.replace_one({"Plan_ID":plan_id}, data)
    else:
        # Insert new data
        collection.insert_one(data)

def insert_open_plan_data(plan_id, data):
    collection_name = "OpenPlan"
    try:
        inserted_data = {
            "Plan_ID": plan_id,
            "Open_Plan": data
            }
        if not inserted_data:
            raise ValueError("No data returned from student_grades function")
        insert_or_replace_open_plan_database(collection_name, plan_id, inserted_data)
        return "Already updated open plan"
    except Exception as e:
        print(f"Error in insert_or_replace_open_plan_database: {e}")
        return e
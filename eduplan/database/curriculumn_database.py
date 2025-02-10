import sys
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from eduplan.api.connect_api import *
from eduplan.api.curriculum_data import *
from eduplan.database.connect_database import connect_mongo


def insert_or_replace_database_cur_id(collection_name: str, cur_id: str, data: dict):
    db = connect_mongo("Curriculumn")
    collection = db[collection_name]
    existing_data = collection.find_one({"cur_id":cur_id})
    
    if existing_data:
        # Replace existing data
        collection.replace_one({"cur_id":cur_id}, data)
    else:
        # Insert new data
        collection.insert_one(data)

def insert_or_replace_database_plan_id(collection_name: str, plan_id: str, data: dict):
    db = connect_mongo("Curriculumn")
    collection = db[collection_name]
    existing_data = collection.find_one({"plan_id":plan_id})
    
    if existing_data:
        # Replace existing data
        collection.replace_one({"plan_id":plan_id}, data)
    else:
        # Insert new data
        collection.insert_one(data)
        
def insert_plan_list(student_code: str, client, token):
    collection_name = "PlanList"
    try:
        student_collection = client.get_database("Student")["StudentStatus"]
        student_data = student_collection.find_one({"student_code": student_code})
        student_cur_id = student_data["cur_id"]

        data = plan_list(student_cur_id, token)
        inserted_data = {
            "cur_id": student_cur_id,
            "plan_list": data
        }

        if not data:
            raise ValueError("No data returned from student_grades function")
        insert_or_replace_database_cur_id(collection_name, student_cur_id, inserted_data)
        return "Already insert student grades"
    except Exception as e:
        print(f"Error in insert_student_grades: {e}")
        return e

def insert_structure(student_code: str, client, token):
    collection_name = "Structure"
    try:
        student_collection = client.get_database("Student")["StudentStatus"]
        student_data = student_collection.find_one({"student_code": student_code})
        student_plan_id = student_data["plan_id"]
        data = structure(student_plan_id, token)
        inserted_data = {
            "plan_id": student_plan_id,
            "plan_list": data
        }

        if not data:
            raise ValueError("No data returned from student_grades function")
        insert_or_replace_database_plan_id(collection_name, student_plan_id, inserted_data)
        return "Already insert student grades"
    except Exception as e:
        print(f"Error in insert_student_grades: {e}")
        return e  

def insert_plan_subject(student_code: str, client, token):
    collection_name = "PlanSubject"
    try:
        student_collection = client.get_database("Student")["StudentStatus"]
        student_data = student_collection.find_one({"student_code": student_code})
        student_plan_id = student_data["plan_id"]
        data = subjects(student_plan_id, token)
        inserted_data = {
            "plan_id": student_plan_id,
            "plan_subject": data
        }

        if not data:
            raise ValueError("No data returned from student_grades function")
        insert_or_replace_database_plan_id(collection_name, student_plan_id, inserted_data)
        return "Already insert student grades"
    except Exception as e:
        print(f"Error in insert_student_grades: {e}")
        return e  

def insert_preco_subject(student_code: str, client, token):
    collection_name = "PreCoSubject"
    try:
        student_collection = client.get_database("Student")["StudentStatus"]
        student_data = student_collection.find_one({"student_code": student_code})
        student_plan_id = student_data["plan_id"]
        data = preco_subjects(student_plan_id, token)
        inserted_data = {
            "plan_id": student_plan_id,
            "preco_subject": data
        }

        if not data:
            raise ValueError("No data returned from student_grades function")
        insert_or_replace_database_plan_id(collection_name, student_plan_id, inserted_data)
        return "Already insert student grades"
    except Exception as e:
        print(f"Error in insert_student_grades: {e}")
        return e  

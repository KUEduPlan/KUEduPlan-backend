from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from eduplan.database.connect_database import connect_mongo
import time
from database.student_database import insert_student_enrollment, insert_student_grades, insert_student_status, insert_open_plan_data
from database.connect_database import connect_client
from api.connect_api import request_token, verify_token_iwing
from database.curriculumn_database import insert_plan_list, insert_preco_subject, insert_structure, insert_plan_subject
import os
# Secret key for JWT encoding/decoding (Keep it safe!)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# Mock in-memory blacklist (for demo purposes, use Redis or DB in production)
blacklist = set()


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to authenticate user
def authenticate_user(username: str, password: str):
    # user = fake_users_db.get(username)
    db = connect_mongo("Authen")
    collection = db["UserData"]
    user = collection.find_one({"username":username})
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Verify and decode token function
def verify_token(token: str = Depends(oauth2_scheme)):
    blacklist = set()
    db = connect_mongo("Authen")
    collection = db["Blacklist"]
    for data in collection.find({}):
        blacklist.add(data['token'])
        
    if token in blacklist:
        raise HTTPException(status_code=401, detail="Token has been invalidated (logged out)")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")

def student_login(username, password):
    student_code = username.split("b")[1]
    client = connect_client()

    try:
        token = request_token(password, username)
        verify_token_iwing(token)
   
    except Exception as e:
        print(e)

    student_collection = client.get_database("Student")["StudentStatus"]
    student_data = student_collection.find_one({"student_code": student_code})

    if student_data == None:
        # Insert student
        insert_student_status(student_code, token)
        time.sleep(2)
        insert_student_enrollment(student_code, token)
        time.sleep(2)
        insert_student_grades(student_code, token)
        time.sleep(2)

        # Insert curriculumn
        insert_plan_list(student_code, client, token)
        time.sleep(2)
        insert_structure(student_code, client, token)
        time.sleep(2)
        insert_plan_subject(student_code, client, token)
        time.sleep(2)
        insert_preco_subject(student_code, client, token)
        return student_code
    else:
        return student_code
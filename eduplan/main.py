from math import e
from unittest import result
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
from pyswip import Prolog
from rule.assert_rule import *
from fastapi.middleware.cors import CORSMiddleware  # Import CORS Middleware
from database.connect_database import connect_client
from database.models import DropFailCourseRequest, Login, Tokens, OpenPlanCourse, OpenPlanChoice, OpenPlanDropFailCourseRequest
from based_distribution import *
from based_study_plan import *
from based_open_plan import *
from based_prolog_data import *
from based_advisor_data import *
import time
from database.student_database import *
from datetime import datetime, timedelta
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from authen import *

# TODO: Added login part and all function required login add token genelize
# TODO: Added button required current sem from student 

prolog = Prolog()
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, you can specify a list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Root endpoint for sanity check
@app.get("/")
def read_root():
    return {"message": "Welcome to the KU EduPlan API!"}

# TODO: Login / Logout part
# Login endpoint to generate token
@app.post("/eduplan/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create token with username and role
    try:
        if user["role"] == "student":
            student_code = student_login(form_data.username, form_data.password)
            access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
            return {"username": student_code, "access_token": access_token, "token_type": "bearer"}
        else:
            access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
            return {"username": user["username"], "access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(e)

@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")  # Extract the role from the payload
        
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        if role == "student":
            db = connect_mongo("Student")
            collection = db["StudentStatus"]
            student_code = username.split("b")[1]
            data = collection.find_one({"student_code": student_code})
        if role == "curriculum_admin":
            db = connect_mongo("CurriculumnAdmin")
            collection = db["AdminData"]
            data = collection.find_one({"advisor_code": username})
        if role == "advisor":
            db = connect_mongo("Advisor")
            collection = db["AdvisorData"]
            data = collection.find_one({"advisor_code": username}) 
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")

    return {"username": username, "role": role, "plan_id": data['plan_id']}

# Logout endpoint to invalidate token
@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    client = connect_client()
    db = client["Authen"]
    collection = db["Blacklist"]
    collection.insert_one({"token":token})  # Add the token to blacklist
    return {"message": "Logged out successfully"}


# TODO: Request PRECO course from advisor or data of plan id of advisor cannot use student data
## TODO: pre help5
@app.get("/distribution_course")
def get_distribution_course(user: dict = Depends(verify_token)):
    if user["role"] != "curriculum_admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    return distribution_course()

@app.post("/sub_dis_cid/{CID}")
def post_distribution_course(CID, request: OpenPlanChoice, user: dict = Depends(verify_token)):
    if user["role"] != "curriculum_admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    remove_all_data()
    assert_preco_course_plan_id(request.Plan_ID)
    assert_rules()
    pre_course = pre_Course()
    pre_course_ids = {course['PREID'] for course in pre_course}.union({course['CID'] for course in pre_course})
    for course in distribution_data:
        if course['CID'] == CID:
            if course['CID'] not in pre_course_ids:
                return distribution(CID, pre_course_ids)
            if course['CID'] in pre_course_ids:
                return pre_sub_distribution(CID, pre_course_ids, pre_course)

@app.post("/allow_sub_dis_cid/{CID}")          
def post_allow_distribution_course(CID, request: OpenPlanChoice, user: dict = Depends(verify_token)):
    if user["role"] != "curriculum_admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    remove_all_data()
    assert_preco_course_plan_id(request.Plan_ID)
    assert_rules()
    pre_course = pre_Course()
    pre_course_ids = {course['PREID'] for course in pre_course}.union({course['CID'] for course in pre_course})
    for course in distribution_data:
        if course['CID'] == CID:
            if course['CID'] not in pre_course_ids:
                data =  distribution(CID, pre_course_ids)
                for year, values in data.items():
                    values["Eligible"] +=  values["Ineligible"]
                    values["Ineligible"] = 0
                return data
            if course['CID'] in pre_course_ids:
                data = pre_sub_distribution(CID, pre_course_ids, pre_course)
                for year, values in data.items():
                    if "GOT_F_Passed_Pre" in  values.keys():
                        values["Ineligible"] -= values["GOT_F_Passed_Pre"]
                        values["Eligible"] += values["GOT_F_Passed_Pre"]
                    else:
                        values["Eligible"] +=  values["Ineligible"]
                        values["Ineligible"] = 0
                return data

### TODO: Open Plan for curriculumn admin
@app.post("/open_plan")
def post_open_plan(request: OpenPlanChoice, user: dict = Depends(verify_token)):
    if user["role"] != "curriculum_admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    remove_all_data()
    open_plan(request.Plan_ID)
    results = list(prolog.query(f"course(CID, CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))
    return results

# @app.post("/open_plan_course_choice")
# def get_required_course(request: OpenPlanChoice, user: dict = Depends(verify_token)):
#     if user["role"] != "curriculum_admin":
#         raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

#     ## Finished
#     print(request.Plan_ID)
#     remove_all_data()
#     assert_open_plan(request.Plan_ID)
#     pre_info_list = list(prolog.query(f"course(CID, CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))
#     pre_info_list = [{k: v for k, v in item.items() if k not in ["ALLOWYEAR", "OPENSEM"]} for item in pre_info_list]
#     return pre_info_list

@app.post("/added_course_open_plan")
def added_course(request: OpenPlanCourse, user: dict = Depends(verify_token)):
    if user["role"] != "curriculum_admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    remove_all_data()
    assert_required_course_open_plan(request.Plan_ID)
    prolog.assertz(f"course('{request.CID}', '{request.CNAME}', '{request.GID}', '{request.GNAME}', {request.ALLOWYEAR}, {request.OPENSEM})")
    pre_info_list = list(prolog.query(f"course(CID, CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))
    insert_open_plan_data(request.Plan_ID, pre_info_list)
    return pre_info_list

@app.post("/removed_course_open_plan")
def removed_course(request: OpenPlanCourse, user: dict = Depends(verify_token)):
    if user["role"] != "curriculum_admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    remove_all_data()
    assert_open_plan(request.Plan_ID)
    prolog.retract(f"course('{request.CID}', '{request.CNAME}', '{request.GID}', '{request.GNAME}', {request.ALLOWYEAR}, {request.OPENSEM})")
    pre_info_list = list(prolog.query(f"course(CID, CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))
    insert_open_plan_data(request.Plan_ID, pre_info_list)
    return pre_info_list

@app.post("/open_plan_lost_sub")
def post_open_plan_lost_sub(request: OpenPlanChoice, user: dict = Depends(verify_token)):
    if user["role"] != "curriculum_admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    client = connect_client()
    db_plan_sub = client["Curriculumn"]
    collection_plan_sub = db_plan_sub["PlanSubject"]
    plan_sub = collection_plan_sub.find_one({"plan_id": request.Plan_ID})
    plan_sub = plan_sub['plan_subject']
    db_open_plan = client["Plan"]
    collection_open_plan = db_open_plan["OpenPlan"]
    open_plan_sub = collection_open_plan.find_one({"Plan_ID": request.Plan_ID})
    open_plan_sub = open_plan_sub['Open_Plan']

    # Extracting subject codes from plan_sub
    plan_subject_codes = {sub['subject_code'].split('-')[0] for sub in plan_sub}

    # Extracting CIDs from open_plan
    open_plan_cids = {plan['CID'] for plan in open_plan_sub}

    # Finding subject codes not in open_plan CIDs
    missing_subjects = plan_subject_codes - open_plan_cids

    # Finding full data of subjects in plan_sub that are missing
    missing_subjects_data = [sub for sub in plan_sub if sub['subject_code'].split('-')[0] in missing_subjects]

    for sub in missing_subjects_data:
        sub['subject_code'] = sub['subject_code'].split('-')[0]
    return missing_subjects_data

@app.post("/reset_open_plan")
def post_open_plan(request: OpenPlanChoice, user: dict = Depends(verify_token)):
    client = connect_client()
    db_open_plan = client["Plan"]
    collection_open_plan = db_open_plan["OpenPlan"]
    # Delete all documents in the collection
    collection_open_plan.delete_many({})
    assert_required_course_open_plan(request.Plan_ID)
    return "Already reset open plan as default"

# TODO: Student and study plan endpoint
# Endpount to get the student data
@app.get("/student_data/{stdID}")
def get_student_data(stdID, user: dict = Depends(verify_token)):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    remove_all_data()
    assert_data(stdID)
    assert_rules()
    results = student_data(stdID)
    results[0]['StdID'] = stdID
    return results

@app.get("/pre_course/{stdID}")
def get_student_passed_course(stdID):
    remove_all_data()
    assert_data(stdID)
    assert_rules()
    pre_course = pre_Course()
    result = []

    for course in pre_course:
        pre_id = course["PREID"]
        
        # Query prerequisite course info
        pre_info_list = list(prolog.query(f"course('{pre_id}', CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))
        if pre_info_list:  # Ensure pre_info_list is not empty
            for pre_info in pre_info_list:  # Iterate through the list
                pre_info['ID'] = pre_id
        else:
            print(f"No prerequisite info found for {pre_id}")

        # Query current course info
        id = course["CID"]
        info_list = list(prolog.query(f"course('{id}', CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))

        if info_list:
            for info in info_list:
                info['ID'] = id

        # Append structured data
        for pre_info in pre_info_list:
            for info in info_list:
                result.append({
                    "PrerequisiteCourse": {
                        "ID": pre_info["ID"],
                        "Name": pre_info["CNAME"],
                        "AllowedYear": pre_info["ALLOWYEAR"],
                        "OpenSemester": pre_info["OPENSEM"]
                    },
                    "CurrentCourse": {
                        "ID": info["ID"],
                        "Name": info["CNAME"],
                        "AllowedYear": info["ALLOWYEAR"],
                        "OpenSemester": info["OPENSEM"]
                    }
                })
    return result

## TODO: Student used open plan
#assert_open_plan(request.Plan_ID)
@app.post("/open_plan/{stdID}")
def student_open_plan(stdID: str, request: OpenPlanChoice, user: dict = Depends(verify_token)):
    print(user["role"])
    if user["role"] == "curriculum_admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Student and Advisor only")

    #TODO: check current sem of student
    remove_all_data()
    open_plan(request.Plan_ID)
    open_plan_assert_data(stdID)
    assert_rules()
    course = list(prolog.query(f"course(CID, CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))
    results = open_study_plan(stdID, course)
    for course in results:
        course.setdefault('GID', '0')
    return results

@app.post("/open_plan/submit_drop_fail_course/")
def post_open_plan_drop_fail_course(request: OpenPlanDropFailCourseRequest, user: dict = Depends(verify_token)):
    if user["role"] == "curriculum_admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Curriculum admin only")

    # Clear data and assert courses
    remove_all_data()

    open_plan(request.Plan_ID)
    open_plan_assert_data(request.StdID)

    # # Process the courses based on their Type
    for course in request.Courses:
        if course.Type == "Dropped":
            prolog.retract(f"recivedGrade('{request.StdID}', '{course.CID}', '{course.CName}', _, _, {course.Sem})") 
            prolog.assertz(f"recivedGrade('{request.StdID}', '{course.CID}', '{course.CName}', 'W', {course.Year}, {course.Sem})")    
        elif course.Type == "Failed":
        #   print(f"Failed course: CID={course.CID}, Year={course.Year}, Sem={course.Sem}")
            prolog.retract(f"recivedGrade('{request.StdID}', '{course.CID}', '{course.CName}', _, _, {course.Sem})") 
            prolog.assertz(f"recivedGrade('{request.StdID}', '{course.CID}', '{course.CName}', 'F', {course.Year}, {course.Sem})")   
    # Reassert rules and generate a study plan
    assert_rules()
    course = list(prolog.query(f"course(CID, CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))
    results = open_study_plan(request.StdID, course)
    return results

# ToDo Adivisor
@app.post("/advisee_list_data/{advisor_code}")
def advisee_data(advisor_code, user: dict = Depends(verify_token)):
    if user["role"] != "advisor":
        raise HTTPException(status_code=403, detail="Access forbidden: Advisor only")
    remove_all_data()
    return query_advisee_data(advisor_code)

@app.post("/advisor_data/{advisor_code}")
def advisor_data(advisor_code, user: dict = Depends(verify_token)):
    if user["role"] != "advisor":
        raise HTTPException(status_code=403, detail="Access forbidden: Advisor only")
    
    db = connect_mongo("Advisor")
    collection = db["AdvisorData"]
    course_data = collection.find_one({"advisor_code": advisor_code}, {'_id': 0})
    return course_data

# ToDo Curriculumn

@app.post("/curriculum_admin_data/{curriculum_admin_code}")
def advisee_data(curriculum_admin_code, user: dict = Depends(verify_token)):
    if user["role"] != "curriculum_admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Curriculum admin only")
    
    db = connect_mongo("CurriculumnAdmin")
    collection = db["AdminData"]
    course_data = collection.find_one({"advisor_code": curriculum_admin_code}, {'_id': 0})
    return course_data
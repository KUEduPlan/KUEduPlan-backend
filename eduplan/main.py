from unittest import result
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
from pyswip import Prolog
from rule.assert_rule import *
from fastapi.middleware.cors import CORSMiddleware  # Import CORS Middleware
from api.connect_api import request_token, verify_token
from database.student_database import insert_student_enrollment, insert_student_grades, insert_student_status, insert_open_plan_data
from database.curriculumn_database import insert_plan_list, insert_preco_subject, insert_structure, insert_plan_subject
from database.connect_database import connect_client
from tokens import eduplan_tokens, insert_student_tokens, revoke_tokens
from database.models import DropFailCourseRequest, Login, Tokens, OpenPlanCourse, OpenPlanChoice, OpenPlanDropFailCourseRequest
from based_distribution import *
from based_study_plan import *
from based_open_plan import *
from based_prolog_data import *
from based_advisor_data import *
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

@app.post("/login")
def login(request: Login):
    username = request.Username
    password = request.Password
    student_code = username.split("b")[1]
    client = connect_client()

    try:
        token = request_token(password, username)
        verify_token(token)
        tokens, expire_time = eduplan_tokens(student_code)
        print(tokens)
        insert_student_tokens(student_code, tokens, expire_time)

    except Exception as e:
        print(e)

    student_collection = client.get_database("Student")["StudentStatus"]
    student_data = student_collection.find_one({"student_code": student_code})

    if student_data == None:
        # Insert student
        insert_student_status(student_code, token)
        insert_student_enrollment(student_code, token)
        insert_student_grades(student_code, token)

        # Insert curriculumn
        insert_plan_list(student_code, client, token)
        insert_structure(student_code, client, token)
        insert_plan_subject(student_code, client, token)
        insert_preco_subject(student_code, client, token)
        return student_code
    else:
        return student_code
    
@app.post("/logout")
def logout(request: Tokens):
    student_code = str(request.StdID)
    tokens = request.Tokens
    return revoke_tokens(student_code, tokens)

# TODO: Student and study plan endpoint
# Endpount to get the student data
@app.get("/student_data/{stdID}")
def get_student_data(stdID):
    remove_all_data()
    assert_data(stdID)
    assert_rules()
    results = student_data(stdID)
    results[0]['StdID'] = stdID
    return results

@app.get("/study_plan/{stdID}")
def get_student_passed_course(stdID):
    remove_all_data()
    assert_data(stdID)
    assert_rules()
    results = study_plan(stdID)
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

@app.post("/submit_drop_fail_course/{stdID}")
def post_drop_fail_course(stdID, request: DropFailCourseRequest):
    # Clear data and assert courses
    remove_all_data()
    assert_data(stdID)

    # # Process the courses based on their Type
    for course in request.Courses:
        if course.Type == "Dropped":
            prolog.retract(f"recivedGrade('{stdID}', '{course.CID}', '{course.CName}', _, _, {course.Sem})") 
            prolog.assertz(f"recivedGrade('{stdID}', '{course.CID}', '{course.CName}', 'W', {course.Year}, {course.Sem})")    
        elif course.Type == "Failed":
        #   print(f"Failed course: CID={course.CID}, Year={course.Year}, Sem={course.Sem}")
            prolog.retract(f"recivedGrade('{stdID}', '{course.CID}', '{course.CName}', _, _, {course.Sem})") 
            prolog.assertz(f"recivedGrade('{stdID}', '{course.CID}', '{course.CName}', 'F', {course.Year}, {course.Sem})")   
        print(list(prolog.query(f"recivedGrade('{stdID}', '{course.CID}', CName, GRADE, YEAR, SEM)")))
    # Reassert rules and generate a study plan
    assert_rules()
    results = study_plan(stdID)
    return results


# TODO: Request PRECO course from advisor or data of plan id of advisor cannot use student data
## TODO: pre help
@app.get("/distribution_course")
def get_distribution_course():
    return distribution_course()

@app.post("/sub_dis_cid/{CID}")
def post_distribution_course(CID):
    student_code = '6410546131'
    assert_data(student_code)
    assert_rules()
    pre_course = pre_Course()
    pre_course_ids = {course['PREID'] for course in pre_course}.union({course['CID'] for course in pre_course})
    for course in distribution_data:
        if course['CID'] == CID:
            if course['CID'] not in pre_course_ids:
                return distribution(CID, pre_course_ids)
            if course['CID'] in pre_course_ids:
                return pre_sub_distribution(CID, pre_course_ids, pre_course)
            


### TODO: Open Plan
@app.post("/open_plan")
def post_open_plan(request: OpenPlanChoice):
    remove_all_data()
    open_plan(request.Plan_ID)
    results = list(prolog.query(f"course(CID, CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))
    return results

@app.post("/open_plan_course_choice")
def get_required_course(request: OpenPlanChoice):
    ## Finished
    print(request.Plan_ID)
    remove_all_data()
    assert_open_plan(request.Plan_ID)
    pre_info_list = list(prolog.query(f"course(CID, CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))
    pre_info_list = [{k: v for k, v in item.items() if k not in ["ALLOWYEAR", "OPENSEM"]} for item in pre_info_list]
    return pre_info_list

@app.post("/added_course_open_plan")
def added_course(request: OpenPlanCourse):
    remove_all_data()
    assert_required_course_open_plan(request.Plan_ID)
    prolog.assertz(f"course('{request.CID}', '{request.CNAME}', '{request.GID}', '{request.GNAME}', {request.ALLOWYEAR}, {request.OPENSEM})")
    pre_info_list = list(prolog.query(f"course(CID, CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))
    insert_open_plan_data(request.Plan_ID, pre_info_list)
    return pre_info_list

@app.post("/removed_course_open_plan")
def removed_course(request: OpenPlanCourse):
    remove_all_data()
    assert_open_plan(request.Plan_ID)
    prolog.retract(f"course('{request.CID}', '{request.CNAME}', '{request.GID}', '{request.GNAME}', {request.ALLOWYEAR}, {request.OPENSEM})")
    pre_info_list = list(prolog.query(f"course(CID, CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))
    insert_open_plan_data(request.Plan_ID, pre_info_list)
    return pre_info_list


## TODO: Student used open plan
#assert_open_plan(request.Plan_ID)
@app.post("/open_plan/{stdID}")
def student_open_plan(stdID: str, request: OpenPlanChoice):
    #TODO: check current sem of student
    remove_all_data()
    open_plan(request.Plan_ID)
    open_plan_assert_data(stdID)
    assert_rules()
    course = list(prolog.query(f"course(CID, CNAME, GID, GNAME, ALLOWYEAR, OPENSEM)"))
    results = open_study_plan(stdID, course)
    return results

@app.post("/open_plan/submit_drop_fail_course/")
def post_open_plan_drop_fail_course(request: OpenPlanDropFailCourseRequest):

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

# TODO: Advisor part
@app.get("/advior_data/")
def get_advisor_data():
    return mock_advisor_data


# advisor_code = "McLaren12345"
# advisor_plan_id = 9363

@app.post("/advisee_list_data/{advisor_code}")
def advisee_data(advisor_code):
    remove_all_data()
    # open_plan(advisor_plan_id)
    # open_plan_assert_data(request.StdID)
    return query_advisee_data(advisor_code)

# advisee_data(advisor_code, advisor_plan_id)
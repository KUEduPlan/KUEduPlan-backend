from unittest import result
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
from pyswip import Prolog
from rule.assert_rule import *
from fastapi.middleware.cors import CORSMiddleware  # Import CORS Middleware
from api.connect_api import request_token, verify_token
from database.student_database import insert_student_enrollment, insert_student_grades, insert_student_status
from database.curriculumn_database import insert_plan_list, insert_preco_subject, insert_structure, insert_plan_subject
from database.connect_database import connect_client
from tokens import eduplan_tokens, insert_student_tokens, revoke_tokens
from database.models import DropFailCourseRequest, Login, Tokens

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

def assert_data(student_code):
    assert_student_data(student_code)
    assert_student_register(student_code)
    assert_student_grade_recived(student_code)
    assert_required_course(student_code)
    assert_preco_course(student_code)
    assert_student_recived_grade_current_sem(student_code)
    

# Root endpoint for sanity check
@app.get("/")
def read_root():
    return {"message": "Welcome to the KU EduPlan API!"}

# Fetch the initial study plan for the user, 
# including courses, prerequisites, and semester structure.

def remove_all_data():
    prolog.retractall('student(_, _, _, _, _, _, _, _, _, _, _, _)')
    prolog.retractall('register(_, _, _, _, _)')
    prolog.retractall('recivedGrade(_, _, _, _, _, _)')
    prolog.retractall('course(_, _, _, _, _, _)')
    prolog.retractall('directPrerequisiteOf(_, _)')
    prolog.retractall('corequisiteOf(_, _)')
    prolog.retractall('currentYear(_)')

    # Clear Rules
    prolog.retractall('passedCourse(_, _, _, _, _)')
    prolog.retractall('canRegister(_, _, _, _)')
    prolog.retractall('futureCourse(_, _, _, _, _)')
    prolog.retractall('prerequisiteOf(_, _)')


def study_plan(stdID):
    # Retrieve data with fallback to empty lists if None is returned
    course = required_course()
    passed = passed_courses(stdID)
    future_data = future_course(stdID) + future_fail_course(stdID)

    df = pd.DataFrame(future_data)
    df['YEAR'] = df['YEAR'] % 100
    df_unique = df.drop_duplicates()
    future = df_unique.to_dict(orient='records')

    # TODO: Fixed bugs that collision conditions
    remove_courses = set()

    # print("Future", future)

    for course in future:
        query_grade = list(prolog.query(f"recivedGrade('{stdID}', '{course['CID']}', CName, GRADE, YEAR, SEM)"))
        for i in range(len(query_grade)):
            query_grade[i]['CID'] = course['CID']
        # print("Query", query_grade)
        
        # Check if the course is already passed
        for grade_entry in query_grade:
            if grade_entry['GRADE'] not in ["Undefined", "F"]:  # Passed courses
                remove_courses.add(grade_entry['CID'])

    # Filter out passed courses
    future = [course for course in future if course['CID'] not in remove_courses]
    print(future)

    grades = recieved_grade(stdID)

    for course_passed in passed:
        for course_grade in grades:
            if course_passed['CID'] == course_grade['CID']:
                course_passed['GRADE'] = course_grade['GRADE']
    
    for course_future in future:
        course_future['GRADE'] = 'Undefinded'

    results =  passed + future

    courses = required_course()

    for course in courses:
        for result in results:
            if result['CID'] == course['CID']:
                result['CNAME'] = course['CNAME']
    return results

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

    # print(request)
    # grades = recieved_grade(stdID)
    # return grades

    # # Process the courses based on their Type
    for course in request.Courses:
        if course.Type == "Dropped":
            prolog.retract(f"recivedGrade('{stdID}', '{course.CID}', '{course.CName}', _, _, {course.Sem})") 
            prolog.assertz(f"recivedGrade('{stdID}', '{course.CID}', '{course.CName}', 'W', {course.Year}, {course.Sem})")    
        elif course.Type == "Failed":
        #   print(f"Failed course: CID={course.CID}, Year={course.Year}, Sem={course.Sem}")
            prolog.retract(f"recivedGrade('{stdID}', '{course.CID}', '{course.CName}', _, _, {course.Sem})") 
            prolog.assertz(f"recivedGrade('{stdID}', '{course.CID}', '{course.CName}', 'F', {course.Year}, {course.Sem})")   
    # Reassert rules and generate a study plan
    assert_rules()
    results = study_plan(stdID)
    return results


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
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
from function import *

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
def assert_required_course_open_plan(plan_id):
    db = connect_mongo("Curriculumn")
    collection = db["PlanSubject"]
    course_data = collection.find_one({"plan_id": plan_id})
    plan_subject = course_data['plan_subject']
    for i in range(len(plan_subject)):
        plan_subject[i]['subject_code'] = plan_subject[i]['subject_code'].split('-')[0]
    key_mapping = {
    "CID": "subject_code",
    "CNAME": "subject_name",
    "GID": "group_no",
    "GNAME": "group_name",
    "ALLOWYEAR": "class_year",
    "OPENSEM": "semester"
    }
    plan_subject = [
    {new_key: item[old_key] for new_key, old_key in key_mapping.items()}
    for item in plan_subject
    ]
    
    insert_open_plan_data(plan_id, plan_subject)
    for i in range(len(plan_subject)):
        prolog.assertz(
            f"course('{plan_subject[i]['CID']}', '{plan_subject[i]['CNAME']}', '{plan_subject[i]['GID']}', '{plan_subject[i]['GNAME']}', {plan_subject[i]['ALLOWYEAR']}, {plan_subject[i]['OPENSEM']})"
        )

def assert_open_plan(plan_id):
    db = connect_mongo("Plan")
    collection = db["OpenPlan"]
    course_data = collection.find_one({"Plan_ID": plan_id})
    plan_subject = course_data['Open_Plan']
    for i in range(len(plan_subject)):
        prolog.assertz(
            f"course('{plan_subject[i]['CID']}', '{plan_subject[i]['CNAME']}', '{plan_subject[i]['GID']}', '{plan_subject[i]['GNAME']}', {plan_subject[i]['ALLOWYEAR']}, {plan_subject[i]['OPENSEM']})"
        )

def open_plan(plan_id):
    db = connect_mongo("Plan")
    collection = db["OpenPlan"]
    course_data = collection.find_one({"Plan_ID": plan_id})
    if course_data:
        assert_open_plan(plan_id)
        print('1')
    else: 
        assert_required_course_open_plan(plan_id)
        print('2')

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
def open_study_plan(stdID, courses):
    # Retrieve data with fallback to empty lists if None is returned
    course = required_course()
    passed = passed_courses(stdID)
    future_data = future_course(stdID) + future_fail_course(stdID)
    df = pd.DataFrame(future_data)
    df['YEAR'] = df['YEAR'] % 100
    df_unique = df.drop_duplicates()
    future = df_unique.to_dict(orient='records')


    # Find max YEAR
    max_year = max(course['YEAR'] for course in passed)

    # Filter courses with max YEAR
    filtered_by_year = [course for course in passed if course['YEAR'] == max_year]

    # Find max SEM from the filtered courses
    max_sem = max(course['SEM'] for course in filtered_by_year)

    # Filter courses with max SEM
    max_y_s_p = [course for course in filtered_by_year if course['SEM'] == max_sem]

    if max_y_s_p[0]['SEM'] == 2:
        max_y_s_p[0]['SEM'] = 1
        max_y_s_p[0]['YEAR'] = max_y_s_p[0]['YEAR'] + 1
    if max_y_s_p[0]['SEM'] == 1:
        max_y_s_p[0]['SEM'] = 2
    current_year = max_y_s_p[0]['YEAR']
    current_sem = max_y_s_p[0]['SEM']

    remove_courses = set()
    for course in future:
        query_grade = list(prolog.query(f"recivedGrade('{stdID}', '{course['CID']}', CName, GRADE, YEAR, SEM)"))
        for i in range(len(query_grade)):
            query_grade[i]['CID'] = course['CID']
        # Check if the course is already passed
        for grade_entry in query_grade:
            if grade_entry['GRADE'] not in ["Undefined", "F"]:  # Passed courses
                remove_courses.add(grade_entry['CID'])

    # Filter out passed courses
    future = [course for course in future if course['CID'] not in remove_courses]
    # print(future)
    # TODO: Added test
    for course in future:
        course_year = course['YEAR']
        course_sem = course['REGISTERSEM']

        if course_year < current_year and course_sem == 2:
            # If previous year's sem 2, register in current semester
            course['YEAR'], course['REGISTERSEM'] = current_year, current_sem
        elif course_year < course['REGISTERSEM'] and course_sem == 1:
            # If previous year's sem 1, register in next year's sem 1
            course['YEAR'], course['REGISTERSEM'] = current_year + 1, 1
        else:
            # Otherwise, keep the original registration year and semester
            course['YEAR'], course['REGISTERSEM'] = course_year, course_sem

        print(f"Course {course['CID']} should be registered in Year {course['YEAR']}, Semester {course['REGISTERSEM']}")


    grades = recieved_grade(stdID)

    for course_passed in passed:
        for course_grade in grades:
            if course_passed['CID'] == course_grade['CID']:
                course_passed['GRADE'] = course_grade['GRADE']
    
    for course_future in future:
        course_future['GRADE'] = 'Undefinded'

    grades_f = list(prolog.query(f"recivedGrade('{stdID}', CID, CName, 'F', YEAR, SEM)"))
    grades_w = list(prolog.query(f"recivedGrade('{stdID}', CID, CName, 'W', YEAR, SEM)"))
    for i in range(len(grades_f)):
        grades_f[i]['GRADE'] = 'F'
    for i in range(len(grades_w)):
        grades_w[i]['GRADE'] = 'W'
    results =  passed + grades_f + grades_w + future

    for course in courses:
        for result in results:
            if result['CID'] == course['CID']:
                result['CNAME'] = course['CNAME']
    return results


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
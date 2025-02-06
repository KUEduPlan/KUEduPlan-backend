from unittest import result
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pyswip import Prolog
from rule.rule import *
from fastapi.middleware.cors import CORSMiddleware  # Import CORS Middleware

# TODO: Assert required course that student need to study in the future
# TODO: Calculate the min/max credit
# TODO: Created test
# TODO: Some of preco code doesn't in subject code ?
# TODO: Added login part and all function required login
# TODO: Added button required current sem fromstudent 

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


class CourseDetail(BaseModel):
    CID: str
    Year: int
    Sem: str
    Type: str

# Define the request body model
class DropFailCourseRequest(BaseModel):
    StdID: int
    Courses: List[CourseDetail]

def assert_data(student_code):
    assert_student_data(student_code)
    assert_student_register(student_code)
    assert_student_grade_recived(student_code)
    assert_required_course(student_code)
    assert_preco_course(student_code)

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
    prolog.retractall('passedCourse(_, _, _, _)')
    prolog.retractall('canRegister(_, _, _, _)')
    prolog.retractall('futureCourse(_, _, _, _)')


def study_plan(stdID):
    # Retrieve data with fallback to empty lists if None is returned
    passed = passed_courses(stdID)
    future = future_course(stdID)
    grades = recieved_grade(stdID)

    for course_passed in passed:
        for course_grade in grades:
            if course_passed['CID'] == course_grade['CID']:
                course_passed['GRADE'] = course_grade['GRADE']
    
    for course_future in future:
        course_future['GRADE'] = 'Undefinded'

    results =  passed + future

    courses = required_course()
    print(results)

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

    print(result)
    return result

    # return result

@app.post("/submit_drop_fail_course/{stdID}")
def post_drop_fail_course(stdID, request: DropFailCourseRequest):

    # Clear data and assert courses
    remove_all_data()
    assert_data(stdID)

    # Process the courses based on their Type
    for course in request.Courses:
        if course.Type == "Dropped":
            print(f"Drop course: CID={course.CID}, Year={course.Year}, Sem={course.Sem}")
            prolog.retract(f'recievedGrade({request.StdID}, "{course.CID}", _, {course.Year})')
            prolog.assertz(f'recievedGrade({request.StdID}, "{course.CID}", "W", {course.Year})')
        elif course.Type == "Failed":
            print(f"Failed course: CID={course.CID}, Year={course.Year}, Sem={course.Sem}")
            prolog.retract(f'recievedGrade({request.StdID}, "{course.CID}", _, {course.Year})')
            prolog.assertz(f'recievedGrade({request.StdID}, "{course.CID}", "F", {course.Year})')

    # Reassert rules and generate a study plan
    assert_rules()
    results = study_plan(request.StdID)
    print(results)
    return results




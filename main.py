from unittest import result
from mock_courses import *
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from pyswip import Prolog



# Initialize Prolog
prolog = Prolog()
app = FastAPI()

assert_courses()
assert_rules()

class CourseDetail(BaseModel):
    CID: str
    Year: int
    Sem: str

# Define the request body model
class DropFailCourseRequest(BaseModel):
    StdID: int
    Drop: List[CourseDetail]
    Fail: List[CourseDetail]

# Root endpoint for sanity check
@app.get("/")
def read_root():
    return {"message": "Welcome to the KU EduPlan API!"}

# Fetch the initial study plan for the user, 
# including courses, prerequisites, and semester structure.

def remove_all_data():
    # Clear Department data
    prolog.retractall('department(_, _)')
    prolog.retractall('major(_, _)')
    prolog.retractall('departmentOf(_, _)')

    # Clear RequiredCourseByMajor data
    prolog.retractall('requiredCourseByMajor(_, _)')

    # Clear Course data
    prolog.retractall('course(_, _, _, _)')

    # Clear Prerequisite data
    prolog.retractall('directPrerequisiteOf(_, _)')
    prolog.retractall('corequisiteOf(_, _)')
    prolog.retractall('prerequisiteOf(_, _)')

    # Clear Student data
    prolog.retractall('student(_, _, _, _, _, _, _, _)')

    # Clear Grades and Registration data
    prolog.retractall('recievedGrade(_, _, _, _)')
    prolog.retractall('register(_, _, _, _)')

    # Clear Current Year data
    prolog.retractall('currentYear(_)')

    # Clear Rules
    prolog.retractall('passedCourse(_, _, _, _)')
    prolog.retractall('canRegister(_, _, _, _)')
    prolog.retractall('futureCourse(_, _, _, _)')


def study_plan(stdID):
    # Retrieve data with fallback to empty lists if None is returned
    passed = passed_courses(stdID)
    future = future_course(stdID)
    # courses = passed + future
    grades = recieved_grade(stdID)
    print(future)

    for course_passed in passed:
        for course_grade in grades:
            if course_passed['CID'] == course_grade['CID']:
                course_passed['GRADE'] = course_grade['GRADE']
    
    for course_future in future:
        course_future['GRADE'] = 'Undefinded'

    results =  passed + future

    courses = course_data()
    print(courses)

    for course in courses:
        for result in results:
            if result['CID'] == course['CID']:
                result['CNAME'] = course['CNAME']
    return results

# Endpount to get the student data
@app.get("/student_data/{stdID}")
def get_student_data(stdID: int):
    remove_all_data()
    assert_courses()
    assert_rules()
    results = student_data(stdID)
    return results

@app.get("/study_plan/{stdID}")
def get_student_passed_course(stdID):
    remove_all_data()
    assert_courses()
    assert_rules()
    results = study_plan(stdID)
    return results

@app.get("/pre_course")
def get_student_passed_course():
    remove_all_data()
    assert_courses()
    assert_rules()
    pre_course = pre_Course()
    result = []
    for course in pre_course:
        pre_id = course["PREID"]
        pre_info = list(prolog.query(f'course("{pre_id}", CNAME, ALLOWYEAR, OPENSEM)'))[0]
        pre_info['ID'] = pre_id

        id = course["CID"]
        info = list(prolog.query(f'course("{id}", CNAME, ALLOWYEAR, OPENSEM)'))[0]
        info['ID'] = id

        # Append structured data
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

@app.post("/submit_drop_fail_course")
def post_drop_fail_course(request: DropFailCourseRequest):

    # Clear data and assert courses
    remove_all_data()
    assert_courses()

    # Process the 'Drop' courses
    if request.Drop != []:
        for course in request.Drop:
            print(f"Drop course: CID={course.CID}, Year={course.Year}, Sem={course.Sem}")
            prolog.retract(f'recievedGrade({request.StdID}, "{course.CID}", _, {course.Year})')
            ### Data wrong please fix ###
            prolog.assertz(f'recievedGrade({request.StdID}, "{course.CID}", "W", {course.Year})')
    if request.Fail != []:
        # Process the 'Fail' courses
        for course_fail in request.Fail:
            # Add your specific logic for Fail courses if necessary
            print(f"Failed course: CID={course_fail.CID}, Year={course_fail.Year}, Sem={course_fail.Sem}")
            prolog.retract(f'recievedGrade({request.StdID}, "{course_fail.CID}", _, {course_fail.Year})')
            prolog.assertz(f'recievedGrade({request.StdID}, "{course_fail.CID}", "F", {course_fail.Year})')
    assert_rules()
    results = study_plan(request.StdID)
    print(results)
    return results







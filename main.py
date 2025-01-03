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


# Root endpoint for sanity check
@app.get("/")
def read_root():
    return {"message": "Welcome to the KU EduPlan API!"}


# Fetch the initial study plan for the user, 
# including courses, prerequisites, and semester structure.


# Endpount to get the student data
@app.get("/student_data/{stdID}")
def get_student_data(stdID: int):
    results = student_data(stdID)
    return results

@app.get("/study_plan/{stdID}")
def get_student_passed_course(stdID):

    # **** ADDED COURSE NAME *** #
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

@app.get("/pre_course")
def get_student_passed_course():
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



# Can register course that student can register in the current sem
# Endpoint get

# Connect with mongoDB
# End post if F/W

  # KE F
  # recieved greade KEI F

# End post if recived grade subject = F 
# prolog.ass (revie






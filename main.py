from fastapi import FastAPI
from mock_courses import *

from pyswip import Prolog

# Initialize Prolog
prolog = Prolog()

app = FastAPI()

assert_courses()


# Root endpoint for sanity check
@app.get("/")
def read_root():
    return {"message": "Welcome to the KU EduPlan API!"}


# Endpount to get the student data
@app.get("/student_data/{stdID}")
def get_student_data(stdID: int):
    results = student_data(stdID)
    return results

@app.get("/student_passed_courses/{stdID}")
def get_student_passed_course(stdID):

    # **** ADDED COURSE NAME *** #
    # Retrieve data with fallback to empty lists if None is returned
    courses = passed_courses(stdID)
    grades = recieved_grade(stdID)

    # Find common data
    common_data = [
        {'CID': grade['CID'], 'GRADE': grade['GRADE'], 'YEAR': grade['YEAR']}
        for grade in grades
        if any(course['CID'] == grade['CID'] for course in courses)
    ]
    print(common_data)
    return common_data


@app.get("/student_future_courses/{stdID}")
def get_future_courses(stdID):
    results = future_course(stdID)
    return results


# Can register course that student can register in the current sem
# Endpoint get

# Connect with mongoDB
# End post if F/W

  # KE F
  # recieved greade KEI F

# End post if recived grade subject = F 
# prolog.ass (revie




# # Endpoint to fetch current courses
# @app.get("/current_courses/{year}/{semester}")
# def get_current_courses(year: int, semester: int):
#     """
#     Fetches current courses based on year and semester.

#     Args:
#         year (int): The academic year.
#         semester (int): The semester.

#     Returns:
#         dict: A list of current courses.
#     """
#     try:
#         # Query Prolog for current courses
#         results = find_courses_by_year_semester(year, semester)
#         return {f"Courses in Year {year}, Semester {semester}:": results}
#     except Exception as e:
#         return {"error": str(e)}


# # Endpoint to fetch passed courses
# @app.get("/passed_courses/{year}/{semester}")
# def get_passed_courses(year: int, semester: int):
#     """
#     Fetches passed courses based on year and semester.

#     Args:
#         year (int): The academic year.
#         semester (int): The semester.

#     Returns:
#         dict: A list of passed courses.
#     """
#     try:
#         # Query Prolog for current courses
#         results = passed_courses(year, semester)
#         return {"Passed courses:": results}
#     except Exception as e:
#         return {"error": str(e)}


# # Endpoint to fetch future courses
# @app.get("/future_courses/{year}/{semester}")
# def get_future_courses(year: int, semester: int):
#     """
#     Fetches future courses to register for based on year and semester.

#     Args:
#         year (int): The academic year.
#         semester (int): The semester.

#     Returns:
#         dict: A list of future courses.
#     """
#     try:
#         # Query Prolog for current courses
#         results = future_courses_to_register(year, semester)
#         return {"Future courses to register:": results}
#     except Exception as e:
#         return {"error": str(e)}

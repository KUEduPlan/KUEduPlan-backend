from fastapi import FastAPI
from courses import find_courses_by_year_semester, passed_courses, future_courses_to_register, assert_courses

from pyswip import Prolog

# Initialize Prolog
prolog = Prolog()

app = FastAPI()

assert_courses()


# Root endpoint for sanity check
@app.get("/")
def read_root():
    return {"message": "Welcome to the KU EduPlan API!"}


# Endpoint to fetch current courses
@app.get("/current_courses/{year}/{semester}")
def get_current_courses(year: int, semester: int):
    """
    Fetches current courses based on year and semester.

    Args:
        year (int): The academic year.
        semester (int): The semester.

    Returns:
        dict: A list of current courses.
    """
    try:
        # Query Prolog for current courses
        results = find_courses_by_year_semester(year, semester)
        return {f"Courses in Year {year}, Semester {semester}:": results}
    except Exception as e:
        return {"error": str(e)}


# Endpoint to fetch passed courses
@app.get("/passed_courses/{year}/{semester}")
def get_passed_courses(year: int, semester: int):
    """
    Fetches passed courses based on year and semester.

    Args:
        year (int): The academic year.
        semester (int): The semester.

    Returns:
        dict: A list of passed courses.
    """
    try:
        # Query Prolog for current courses
        results = passed_courses(year, semester)
        return {"Passed courses:": results}
    except Exception as e:
        return {"error": str(e)}


# Endpoint to fetch future courses
@app.get("/future_courses/{year}/{semester}")
def get_future_courses(year: int, semester: int):
    """
    Fetches future courses to register for based on year and semester.

    Args:
        year (int): The academic year.
        semester (int): The semester.

    Returns:
        dict: A list of future courses.
    """
    try:
        # Query Prolog for current courses
        results = future_courses_to_register(year, semester)
        return {"Future courses to register:": results}
    except Exception as e:
        return {"error": str(e)}

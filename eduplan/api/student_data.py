import requests
from dotenv import load_dotenv
import os
import sys

load_dotenv()

def student_status(student_code, token):
    url = os.getenv("URL_STUDENT_STATUS")
    data = {
        "student_code": student_code
    }
    
    headers = {
        "Authorization": f'Bearer {token}'
    }

    try:
        # Sending POST request
        response = requests.post(url,headers=headers, json=data)

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Print the response data
        print("Response status code:", response.status_code)

        res = response.json()

    except requests.exceptions.RequestException as e:
        # Handle exceptions
        return ("An error occurred:", e)
    return res


def student_enrollment(student_code, token):
    url = os.getenv("URL_STUDENT_ENROLL")
    data = {
        "student_code": student_code
    }
    
    headers = {
        "Authorization": f'Bearer {token}'
    }

    try:
        # Sending POST request
        response = requests.post(url,headers=headers, json=data)

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Print the response data
        print("Response status code:", response.status_code)

        res = response.json()

    except requests.exceptions.RequestException as e:
        # Handle exceptions
        return ("An error occurred:", e)
    return res

def student_grades(student_code, token):
    url = os.getenv("URL_STUDENT_GRADE")
    data = {
        "student_code": student_code
    }
    
    headers = {
        "Authorization": f'Bearer {token}'
    }

    try:
        # Sending POST request
        response = requests.post(url,headers=headers, json=data)

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Print the response data
        print("Response status code:", response.status_code)

        res = response.json()

    except requests.exceptions.RequestException as e:
        # Handle exceptions
        return ("An error occurred:", e)
    return res


#Unused
def enrollment_semester(student_code, academic_year, semester, token):
    # Display the specify data 
    url = os.getenv("URL_ENROLL_SEM")
    data = {
        "student_code": student_code,
        "academic_year": academic_year, #64, 65
        "semester": semester
    }
    
    headers = {
        "Authorization": f'Bearer {token}'
    }

    try:
        # Sending POST request
        response = requests.post(url,headers=headers, json=data)

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Print the response data
        print("Response status code:", response.status_code)

        res = response.json()

    except requests.exceptions.RequestException as e:
        # Handle exceptions
        return ("An error occurred:", e)
    return res
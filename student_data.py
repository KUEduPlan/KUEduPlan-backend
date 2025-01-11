import requests

from connect_api import request_token, verify_token

def student_status(student_code, token):
    url = "https://webhost.oea.ku.ac.th/kuedu/api/std/status"
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
    url = "https://webhost.oea.ku.ac.th/kuedu/api/std/enrollment"
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
    url = "https://webhost.oea.ku.ac.th/kuedu/api/std/grades"
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


def enrollment_semester(student_code, academic_year, semester, token):
    # Display the specify data 
    url = "https://webhost.oea.ku.ac.th/kuedu/api/std/enrollment/semester"
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


# token = request_token(password, username)
# verify_token(token)


# print(enrollment_semester(student_code, 2564, 1, token))

# print(student_status(student_code, token).keys())
# print("=====")
# print(student_enrollment(student_code, token))

# print("========")
# print(student_grades(student_code, token))

# print("=======")
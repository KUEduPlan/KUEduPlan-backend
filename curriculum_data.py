import requests

from connect_api import request_token, verify_token
from student_data import *

def program_list(campus_id, faculty_id, edulevel, token):
    # display all of program need to specify campus fuc and edulevel
    url = "https://webhost.oea.ku.ac.th/kuedu/api/cur/program/list"
    data = {
    "campus_id": campus_id,
    "faculty_id": faculty_id,
    "edulevel": edulevel
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

def curricurum_program_list(program_id, token):
    url = "https://webhost.oea.ku.ac.th/kuedu/api/cur/program/curriculum/list"
    data = {
    "program_id": program_id
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

def plan_list(cur_id, token):
    url = "https://webhost.oea.ku.ac.th/kuedu/api/cur/plan/list"
    data = {
    "cur_id": cur_id
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

def structure(plan_id, token):
    # กลุ่มสาระที่ต้องเรียนใน plan นั้น min max credit
    url = "https://webhost.oea.ku.ac.th/kuedu/api/cur/structure"
    data = {
    "plan_id": plan_id
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

def subjects(plan_id, token):
    # กลุ่มสาระที่ต้องเรียนใน plan นั้น min max credit
    url = "https://webhost.oea.ku.ac.th/kuedu/api/cur/plan/subjects"
    data = {
    "plan_id": plan_id
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


def preco_subjects(plan_id, token):
    # กลุ่มสาระที่ต้องเรียนใน plan นั้น min max credit
    url = "https://webhost.oea.ku.ac.th/kuedu/api/cur/preco/subjects"
    data = {
    "plan_id": plan_id
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
# program_id = student_status(student_code, token)['program_id']

# print(curricurum_program_list(program_id, token))

# 'program_id': 1012, 'program_name': 'หลักสูตรวิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมซอฟต์แวร์และความรู้ (หลักสูตรนานาชาติ)
password = "pass"
username = "stdID"
student_code = "stdID"
token = request_token(password, username)
verify_token(token)

campus_id = student_status(student_code, token)['campus_code']
faculty_id = student_status(student_code, token)['faculty_code']
cur_id = student_status(student_code, token)['cur_id']
edulevel = "bachelor"
program_id = 1012
plan_id = student_status(student_code, token)['plan_id']

# print(program_list(campus_id, faculty_id, edulevel, token))

# print(student_status(student_code, token))
# print(curricurum_program_list(program_id, token))
# print(plan_list(cur_id, token))
# print(structure(plan_id, token))
# print(subjects(plan_id, token))
print(preco_subjects(plan_id, token))
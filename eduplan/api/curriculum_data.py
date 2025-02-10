import requests
from dotenv import load_dotenv
import os

load_dotenv()

def program_list(campus_id, faculty_id, edulevel, token):
    # display all of program need to specify campus fuc and edulevel
    url = os.getenv("URL_PROGRAM_LIST")
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

#Unused
def curricurum_program_list(program_id, token):
    url = os.getenv("URL_CURRI_PROGRAM_LIST")
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
    url = os.getenv("URL_PLAN_LIST")
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
    url = os.getenv("URL_STRUCTURE")
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
    url = os.getenv("URL_SUBJECTS")
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
    url = os.getenv("URL_PRECO_SUBJECTS")
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

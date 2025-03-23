import requests
from dotenv import load_dotenv
import os

load_dotenv()

def request_token(password, username):
    # Replace with your API endpoint
    url = os.getenv("URL_REQUEST_TOKEN")

    # Replace with your actual request body
    data = {
    "password": password,
    "username": username
    }

    try:
        # Sending POST request
        response = requests.post(url, json=data)

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Print the response data
        print("Response status code:", response.status_code)

        token = response.json()

    except requests.exceptions.RequestException as e:
        # Handle exceptions
        return ("An error occurred:", e)
    return token['access']


def verify_token_iwing(token):
    url = os.getenv("URL_VERIFY_TOKEN")
    data = {
    "token": token,
    }
    try:
        # Sending POST request
        response = requests.post(url, json=data)

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Print the response data
        print("Response status code:", response.status_code)

        res = response.json()

    except requests.exceptions.RequestException as e:
        # Handle exceptions
        return ("An error occurred:", e)
    return res

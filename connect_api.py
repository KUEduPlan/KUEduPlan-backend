import requests

def request_token(password, username):
    # Replace with your API endpoint
    url = "https://webhost.oea.ku.ac.th/kuedu/api/token/pair"

    # # Replace with your actual headers if needed
    # headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": "Bearer YOUR_ACCESS_TOKEN"  # Optional if your API requires authentication
    # }

    # Replace with your actual request body
    data = {
    "password": password,
    "username": "username"
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


def verify_token(token):
    url = "https://webhost.oea.ku.ac.th/kuedu/api/token/verify"
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

import os
import requests
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv('backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url', default="http://localhost:5050/"
)


def get_request(endpoint, **kwargs):
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params += f"{key}={value}&"

    request_url = backend_url + endpoint + ("?" + params if params else "")

    print(f"Attempting to GET data from: {request_url}")  # Debug print
    try:
        response = requests.get(request_url)
        response.raise_for_status()  # Raise HTTP errors
        print(f"Response received: {response.json()}")  # Debug print
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during GET request: {e}")  # Debug print
        return None


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "analyze/" + text
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Network exception occurred: {err}")
        return None


def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    try:
        response = requests.post(request_url, json=data_dict)
        print(response.json())
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Network exception occurred: {err}")
        return None

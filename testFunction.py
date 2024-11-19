from flask import Flask, request, jsonify
from Constants import User_Name, password, Base_URL
import requests

app = Flask(__name__)


if __name__ == '__main__':
    print()
    headers = {'Content-Type': 'application/json'}
    payload = {
        "username": User_Name,
        "password": password
    }
    login_url = Base_URL + 'login'
    response = requests.post(login_url, json=payload, headers=headers)
    print("response")
    print(response)
    # Get the response from the external API
    external_api_response = response.json()
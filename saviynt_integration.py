import requests
import Constants
import json
from datetime import datetime

default_headers = {'Content-Type': 'application/json'}

def greeting():
    # Get current date and time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")

    # Determine the greeting based on the time of day
    hour = now.hour
    if 5 <= hour < 12:
        greeting = "Good Morning"
    elif 12 <= hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    return "Hi " + greeting + ", Welcome to NTT Data, How can I assist you today?\n"

def get_user(username, payload=None):
    access_token = get_auth_code()
    default_headers['Authorization'] = f'Bearer {access_token}'
    default_payload = {
        "filtercriteria": {"username": username},
        "showsecurityanswers": "1"
    }
    if payload == None:
        payload = default_payload
    login_url = Constants.Base_URL + 'getUser'
    print("API Request: **************** \n ")
    print(payload)
    response = make_post_request(login_url, payload, default_headers)
    print("Status Code for getEndpoint API: " + str(response.status_code))
    response_json = response.json()
    print(response_json)
    if response_json.get('msg') == "Successful":
        response_text = "Successfully validated user: \n" + username + " "
    else:
        response_text = "Ohh OOO!!! Invalid user or user not found. \n"
    return response_text


def request_to_add_entitlement(username, endpoint, entitlement_value, entitlement_type='Roles', payload=None):
    print("**In Request Access API**")
    access_token = get_auth_code()
    default_headers['Authorization'] = f'Bearer {access_token}'
    default_payload = {
        "requesttype": "ADD",
        "username": username,
        "endpoint": endpoint,
        "securitysystem": endpoint,
        "accountname": "dheerajc",
        "comments": "add comment",
        "requestor": "dheerajc",
        "createaccountifnotexists": "true",
        "entitlement": [
            {"entitlementtype": entitlement_type, "entitlementvalue": entitlement_value, "startdate": "12-12-2024",
             "enddate": "12-05-2025", "businessjustification": "test business justification"}
        ],
        "checksod": "false"
    }
    if payload is None:
        payload = default_payload

    login_url = Constants.Base_URL + 'v5/createrequest'
    response = make_post_request(login_url, payload, default_headers)
    print("Status Code for Create Request API: " + login_url + " : " + str(response.status_code))
    response_json = response.json()
    print("Payload: ")
    print(payload)
    print(response_json)
    if response_json.get("errorCode") == '0':
        response_text = "Request to add entitlement is success, your request ID is: " + response_json.get("RequestId") + " \n Please request access again if you would like to make another request."
    else:
        response_text = response_json.get("message")
    return response_text


def get_entitlement_values_for_endpoints(application, payload=None):
    access_token = get_auth_code()
    default_headers['Authorization'] = f'Bearer {access_token}'
    default_payload = {
        "endpoint": application,
        "entitlementType": "Roles",
        "entownerwithrank": "false"
    }
    if payload is None:
        payload = default_payload

    login_url = Constants.Base_URL + 'getEntitlementValuesForEndpoint'
    response = make_post_request(login_url, payload, default_headers)
    print("Status Code for getEndpoint API: " + str(response.status_code))
    response_json = response.json()
    print(response_json)
    if response_json.get('msg') == "Successful":
        entitlement_value = [item.get("entitlement_value") for item in response_json.get("Entitlementdetails", [])]
        response_text = "Please select an entitlement value from the below list to request access: "
        for n in entitlement_value:
            if n is not None:
                response_text = response_text + "  " + '"{}"'.format(n) + "\n"
    else:
        response_text = "Application not available for request, Please try other application"
    return response_text


def get_endpoints(payload=None, sec_systems=None):
    access_token = get_auth_code()
    default_headers['Authorization'] = f'Bearer {access_token}'

    default_payload = {
        "filterCriteria": {
            "customproperty1": "1",
            "displayName": "Access Manager"
        }
    }

    if payload is None:
        payload = default_payload

    login_url = Constants.Base_URL + 'getEndpoints'
    response = make_post_request(login_url, payload, default_headers)
    print("Status Code for getEndpoint API: " + str(response.status_code))
    response_json = response.json()
    security_systems = [item.get('securitySystem') for item in response_json if 'securitySystem' in item]
    response_text = ", Please select an application from the below list to request access: "
    for n in security_systems:
        if n is not None:
            response_text = response_text + "  " + '"{}"'.format(n) + "\n"
    return response_text


def get_auth_code():
    payload = {
        "username": Constants.User_Name,
        "password": Constants.password
    }
    login_url = Constants.Base_URL + 'login'
    response = make_post_request(login_url, payload, default_headers)
    response_json = response.json()
    print(response_json)
    print("Status Code for Login API: " + str(response.status_code))
    auth_code = response_json.get("access_token")
    return auth_code


def make_post_request(url, payload, headers):
    response = requests.post(url, json=payload, headers=headers)
    return response

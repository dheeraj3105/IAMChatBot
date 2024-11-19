import requests
import json

# Load configuration from config.json
with open("config.json", "r") as f:
    config = json.load(f)

BASE_URL = config["Base_URL"]
USERNAME = config["User_Name"]
PASSWORD = config["password"]

default_headers = {'Content-Type': 'application/json'}

def get_auth_code():
    """Fetch the access token using credentials."""
    payload = {"username": USERNAME, "password": PASSWORD}
    response = make_post_request(f'{BASE_URL}login', payload)
    if response.ok:
        auth_code = response.json().get("access_token")
        return auth_code
    raise Exception("Failed to retrieve auth token")

def make_post_request(url, payload, headers=None):
    """Reusable function for making POST requests."""
    headers = headers or default_headers
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error during POST request: {e}")
        return None
    return response

def get_headers():
    """Generate authorization headers."""
    access_token = get_auth_code()
    return {**default_headers, 'Authorization': f'Bearer {access_token}'}

def get_user(username="vinay", show_security_answers="1"):
    """Fetch user details dynamically."""
    payload = {
        "filtercriteria": {"username": username},
        "showsecurityanswers": show_security_answers
    }
    response = make_post_request(f'{BASE_URL}getUser', payload, get_headers())
    return parse_response(response, "User Validated", "Username Invalid or User Not found")

def request_to_add_entitlement(username, entitlement_type, entitlement_value, start_date, end_date):
    """Create a request to add entitlement."""
    payload = {
        "requesttype": "ADD",
        "username": username,
        "endpoint": "Sentinel",
        "securitysystem": "Sentinel",
        "accountname": username,
        "comments": "Add comment",
        "requestor": username,
        "createaccountifnotexists": "true",
        "entitlement": [
            {"entitlementtype": entitlement_type,
             "entitlementvalue": entitlement_value,
             "startdate": start_date,
             "enddate": end_date,
             "businessjustification": "Test justification"}
        ],
        "checksod": "false"
    }
    response = make_post_request(f'{BASE_URL}v5/createrequest', payload, get_headers())
    return parse_response(response, "Request created", "Failed to create request", key="RequestId")

def get_entitlement_values_for_endpoints(endpoint="Sentinel", entitlement_type="Roles"):
    """Fetch entitlement values for a specific endpoint."""
    payload = {
        "endpoint": endpoint,
        "entitlementType": entitlement_type,
        "entownerwithrank": "false"
    }
    response = make_post_request(f'{BASE_URL}getEntitlementValuesForEndpoint', payload, get_headers())
    if response:
        values = [item.get("entitlement_value") for item in response.json().get("Entitlementdetails", [])]
        return format_list("Select an entitlement value: ", values)
    return "No entitlement values found."

def get_endpoints(custom_property="1", display_name="Access Manager"):
    """Fetch available endpoints dynamically."""
    payload = {
        "filterCriteria": {
            "customproperty1": custom_property,
            "displayName": display_name
        }
    }
    response = make_post_request(f'{BASE_URL}getEndpoints', payload, get_headers())
    if response:
        systems = [item.get('securitySystem') for item in response.json() if 'securitySystem' in item]
        return format_list("Select an application: ", systems)
    return "No endpoints found."

def parse_response(response, success_message, failure_message, key=None):
    """Parse API response and return appropriate messages."""
    if response:
        response_json = response.json()
        print(response_json)
        if response_json.get('msg') == "Successful":
            return success_message if not key else f"{success_message}, ID: {response_json.get(key)}"
    return failure_message

def format_list(prompt, items):
    """Format a list of items into a readable string."""
    return prompt + "  ".join(f'"{item}"' for item in items if item)
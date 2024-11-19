from flask import Flask, request, jsonify
import requests
import saviynt_integration

app = Flask(__name__)


# This is the route for Dialogflow webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    # Get the request JSON from Dialogflow
    req = request.get_json(silent=True, force=True)

    # Process the request (you can add your logic here)
    intent = req.get('queryResult').get('intent').get('displayName')

    # Example logic: respond based on the intent
    if intent == "YourIntentName":
        # Make an external API call (as an example)
        external_api_url = "https://api.example.com/endpoint"
        headers = {'Content-Type': 'application/json'}
        payload = {
            'param1': 'value1',
            'param2': 'value2'
        }

        # Send a POST request to an external API
        response = requests.post(external_api_url, json=payload, headers=headers)

        # Get the response from the external API
        external_api_response = response.json()

        # Build response for Dialogflow
        fulfillment_text = "The API returned: " + external_api_response.get('result', 'No result')

        return jsonify({
            "fulfillmentText": fulfillment_text,
            "source": "webhook"
        })

    # Default fallback response if intent doesn't match
    return jsonify({
        "fulfillmentText": "Sorry, I don't understand your request.",
        "source": "webhook"
    })


@app.route('/create_user', methods=['POST'])
def create_user():
    # Get the JSON data from the request body
    req = request.get_json()

    parameters = req.get('queryResult').get('parameters')
    first_name = parameters.get('firstName', '')
    last_name = parameters.get('lastName', '')
    email = parameters.get('email', '')
    username = parameters.get('username', '')
    application_name = parameters.get('application', '')

    display_name = req['queryResult']['intent']['displayName']
    print(display_name)
    flag = False
    response_text = "Something wrong with API Integration, Please contact IT support for assistance"
    if display_name == "Entitlement Value":
        response_text = saviynt_integration.get_entitlement_values_for_endpoints(application_name)
        if "Application not available" in response_text:
            flag = True
    elif display_name == "Get Entitlement Roles":
        response_text = saviynt_integration.get_entitlement_values_for_endpoints()
        if "Application not available" in response_text:
            flag = True
    elif display_name == "Create Request":
        parameters = req["queryResult"]["outputContexts"][1]["parameters"]
        first_name = parameters.get('firstName', '')
        last_name = parameters.get('lastName', '')
        email = parameters.get('email', '')
        # username = parameters.get('username', '')
        application_name = parameters.get('application', '')
        response_text = saviynt_integration.request_to_add_entitlement(username, application_name,
                                                                       parameters.get('entitlementvalue', ''))
    elif display_name == "Request_Access_Intent":
        user_authentication = saviynt_integration.get_user(username)
        if "Successfully" in user_authentication:
            response_text = user_authentication + saviynt_integration.get_endpoints()
        else:
            response_text = "User Not Found, please try again"
            flag = True
    elif display_name == "Welcome_Intent":
        response_text = saviynt_integration.greeting()
        flag = "welcome"
    print(response_text)
    if flag == False:
        return {"fulfillmentMessages": [{"text": {"text": [response_text]}}]}
    elif flag == "welcome":
        return {
            "fulfillmentMessages": [
                {
                    "quickReplies": {
                        "title": response_text + " Please choose an option from below for assistance:",
                        "quickReplies": ["Request Access", "Option 2"]
                    }
                }
            ]
        }
    else:
        print({"fulfillmentMessages": [{"text": {"text": [response_text]}}], "outputContexts": [{"name": "projects/iam-chatbot-438200/agent/sessions/c020046d-dc64-0379-3ff1-02a0c381c89b/contexts/FallbackIntent",
                                                                                                 "lifespanCount": 5}] })
        # return {"fulfillmentMessages": [{"text": {"text": [response_text]}}],
        #        "followupEventInput": {
        #     "name": "TARGET_INTENT_EVENT"
        # } }
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [response_text]
                    }
                }
            ],
            "followupEventInput": {
                "name": "TARGET_INTENT_EVENT"
            },
            "outputContexts": [
                {
                    "name": "projects/iam-chatbot-438200/agent/sessions/c020046d-dc64-0379-3ff1-02a0c381c89b/contexts/Request_Access_Intent-followup",
                    "lifespanCount": 0
                }
        ]
        }


if __name__ == '__main__':
    app.run(port=5000, debug=True)

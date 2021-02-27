import json
import logging
import os

import azure.functions as func
import msal
import requests

from dotenv import load_dotenv

load_dotenv()


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    client_id = 'c434aa12-501f-4267-957f-cca6d16f0edd'
    authority = \
        'https://login.microsoftonline.com/bpmcclunegmail.onmicrosoft.com'
    client_credential = os.environ['CLIENT_CREDENTIAL']
    scopes = ['https://graph.microsoft.com/.default']

    msal_app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_credential,
    )
    token_resp = msal_app.acquire_token_for_client(scopes)

    try:
        access_token = token_resp['access_token']
    except KeyError:
        return func.HttpResponse(
            json.dumps({'error': 'Unable to acquire access token'}),
            mimetype='application/json',
            status_code=401,
        )

    userid = req.params.get('userid')
    if not userid:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            userid = req_body.get('userid')

    if not userid:
        return func.HttpResponse(
            json.dumps({'error': 'No userid specifid'}),
            mimetype='application/json',
            status_code=400,
        )

    headers = {'Authorization': f'Bearer {access_token}'}
    api_resp = requests.get(
        f'https://graph.microsoft.com/v1.0/users/{userid}/memberOf',
        headers=headers,
    )
    resp_json = api_resp.json()

    groups = [(d['@odata.type'], d['displayName']) for d in resp_json['value']]
    return func.HttpResponse(
        json.dumps(groups),
        mimetype='application/json',
        status_code=200,
    )

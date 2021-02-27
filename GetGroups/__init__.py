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
    logging.info('Request headers: %s', req.headers)

    client_id = '382b58c4-60a3-4a2c-bd43-05692e40c15d'
    authority = \
        'https://login.microsoftonline.com/clunacy.onmicrosoft.com'
    client_credential = os.environ['CLIENT_CREDENTIAL']
    scopes = ['https://graph.microsoft.com/.default']

    try:
        msal_app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_credential,
        )
    except Exception:
        return func.HttpResponse(
            json.dumps({'error': 'Unable to initialize MSAL client'}),
            mimetype='application/json',
            status_code=503,
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

    userid = req.route_params.get('userid')
    if not userid:
        return func.HttpResponse(
            json.dumps({'error': 'No userid specifid'}),
            mimetype='application/json',
            status_code=400,
        )

    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        api_resp = requests.get(
            f'https://graph.microsoft.com/v1.0/users/{userid}/memberOf',
            headers=headers,
        )
        resp_json = api_resp.json()
        logging.info('Python HTTP received response from Graph: %s', resp_json)

        # groups = [
        #     (d['@odata.type'], d['displayName']) for d in resp_json['value']
        # ]
        return func.HttpResponse(
            # json.dumps(groups),
            resp_json,
            mimetype='application/json',
            status_code=200,
        )
    except (requests.HTTPError, requests.RequestException) as exc:
        return func.HttpResponse(
            json.dumps({'error': f'Exception caught: {exc}'}),
            mimetype='application/json',
            status_code=503,
        )

from datetime import time

from flask import Blueprint, Response, request

import os
import requests

BGG_API_KEY = os.getenv('BGG_API_KEY')


# ---------------------
#   BGG MANAGEMENT
# ---------------------

bgg_bp = Blueprint('bgg', __name__)

def bgg_get(url, params = None):
    """
    Fetch data from the BoardGameGeek API.

    Args:
        url (str): 
            The API endpoint URL.
        params (dict, optional):
            Query parameters for the API request.

    Returns:
        Response: The API response.

    """

    headers = {}
    if BGG_API_KEY:
        headers["Authorization"] = f"Bearer {BGG_API_KEY}"
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    while resp.status_code == 202:
        time.sleep(2)
        resp = requests.get(url, headers=headers, params=params, timeout=15)
    return resp

@bgg_bp.route('/bgg/search', methods=['GET'])
def bgg_search():
    """Search boardgames from the BoardGameGeek API.

    Request: GET
        query (str):
            The search query.

    Returns:
        Response: The API response.

    """

    # Get the original query string from the parameters
    query = request.args.get('query', '')
    resp = bgg_get('https://boardgamegeek.com/xmlapi2/search', params={'query': query})
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("Content-Type"))

@bgg_bp.route('/bgg/thing', methods=['GET'])
def bgg_thing():
    """Fetch details for a specific boardgame from the BoardGameGeek API.

    Request: GET
        id (str):
            The ID of the boardgame to fetch.

    Returns:
        Response: The API response.

    """

    # Get the object ID
    object_id = request.args.get('id', '')
    resp = bgg_get(f'https://boardgamegeek.com/xmlapi2/thing', params={'id': object_id})
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("Content-Type"))

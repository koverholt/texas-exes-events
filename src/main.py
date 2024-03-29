import json
import os
import pytz
import sys
from datetime import datetime, timedelta
from square.client import Client

try:
    SQUARE_ACCESS_TOKEN = os.environ["SQUARE_ACCESS_TOKEN"]
    SQUARE_LOCATION_ID = os.environ["SQUARE_LOCATION_ID"]
except KeyError:
    print("SQUARE_ACCESS_TOKEN and/or SQUARE_LOCATION_ID are not defined. Exiting.")
    sys.exit()

def apply(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    TIMEZONE = "US/Central"
    fetch_date = datetime.now(pytz.timezone(TIMEZONE))
    fetch_date = fetch_date.strftime("%B %-d, %Y at %-I:%M %p")

    client = Client(
        access_token=SQUARE_ACCESS_TOKEN,
        environment="production",
        max_retries=10,
        backoff_factor=1,
    )

    orders_api = client.orders

    current_date = str(datetime.now().astimezone().isoformat())
    past_date = str((datetime.now().astimezone() - timedelta(days=60)).isoformat())

    body = {}
    body["location_ids"] = [SQUARE_LOCATION_ID]
    body["query"] = {}
    body["query"]["filter"] = {}
    body["query"]["filter"]["state_filter"] = {}
    body["query"]["filter"]["state_filter"]["states"] = ["OPEN"]
    body["query"]["filter"]["date_time_filter"] = {}
    body["query"]["filter"]["date_time_filter"]["created_at"] = {}
    body["query"]["filter"]["date_time_filter"]["created_at"]["start_at"] = past_date
    body["query"]["filter"]["date_time_filter"]["created_at"]["end_at"] = current_date
    body["query"]["sort"] = {}
    body["query"]["sort"]["sort_field"] = "CREATED_AT"
    body["query"]["sort"]["sort_order"] = "DESC"
    body["limit"] = 100
    body["return_entries"] = True

    result = orders_api.search_orders(body)
    res_search = json.loads(result.text)
    if not res_search:
        res_search["order_entries"] = ""

    orders = []
    for item in res_search["order_entries"]:
        try:
            orders.append(item["order_id"])
        except:
            pass

    body = {}
    body["order_ids"] = orders

    result = orders_api.batch_retrieve_orders(body)
    res_retrieve = json.loads(result.text)
    if not res_retrieve:
        res_retrieve["orders"] = ""

    event_counts = {}
    for item in res_retrieve["orders"]:
        for count in range(len(item["line_items"])):
            try:
                event_name = item["line_items"][count]["name"]
                event_quantity = item["line_items"][count]["quantity"]
                event_counts[event_name] = event_counts.get(event_name, 0) + int(event_quantity)
            except:
                pass

    result = {"event_counts": event_counts, "fetch_date": fetch_date}
    return (result, 200, headers)

import Algorithmia
import json
import os
import pytz
import sys
from datetime import datetime, timedelta
from square.client import Client

client = Algorithmia.client()
secrets = json.loads(client.file("data://koverholt/TexasExesEvents/secrets.json").getString())

try:
    SQUARE_ACCESS_TOKEN = secrets["square-access-token"]
    SQUARE_LOCATION_ID = secrets["square-location-id"]
except KeyError:
    print("The secrets SQUARE_TOKEN and/or SQUARE_LOCATION_ID are not defined. Exiting.")
    sys.exit()

print(SQUARE_ACCESS_TOKEN)
print(SQUARE_LOCATION_ID)

def apply(input):
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

    current_date = str(datetime.now().isoformat())
    past_date = str((datetime.now() - timedelta(60)).isoformat())

    body = {}
    body["location_ids"] = [SQUARE_LOCATION_ID]
    body["query"] = {}
    body["query"]["filter"] = {}
    body["query"]["filter"]["state_filter"] = {}
    body["query"]["filter"]["state_filter"]["states"] = ["COMPLETED"]
    body["query"]["filter"]["date_time_filter"] = {}
    body["query"]["filter"]["date_time_filter"]["closed_at"] = {}
    body["query"]["filter"]["date_time_filter"]["closed_at"]["start_at"] = past_date
    body["query"]["filter"]["date_time_filter"]["closed_at"]["end_at"] = current_date
    body["query"]["sort"] = {}
    body["query"]["sort"]["sort_field"] = "CLOSED_AT"
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

    result = orders_api.batch_retrieve_orders(SQUARE_LOCATION_ID, body)
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

    resp = {"event_counts": event_counts, "fetch_date": fetch_date}
    return resp


if __name__ == "__main__":
    apply(input)

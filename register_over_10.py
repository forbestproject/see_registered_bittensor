
import os
import requests
from datetime import datetime, timedelta, timezone
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["TAOSTATS_API_KEY"]

URL = "https://api.taostats.io/v1/subnets/neuron-registration-events"

# Today's UTC time window
now = datetime.now(timezone.utc)
start = now.replace(hour=0, minute=0, second=0, microsecond=0)
end = start + timedelta(days=1)

params = {
    "timestamp_start": int(start.timestamp()),
    "timestamp_end": int(end.timestamp()) - 1,
    "limit": 200,
    "page": 1
}

headers = {"Authorization": API_KEY}

counts = Counter()

while True:
    response = requests.get(
        URL,
        headers=headers,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    result = response.json()

    for registration in result["data"]:
        counts[registration["netuid"]] += 1

    next_page = result["pagination"]["next_page"]
    if next_page is None:
        break

    params["page"] = next_page

# Filter: more than 10 registrations
qualified = [
    (netuid, count)
    for netuid, count in counts.items()
    if count > 10
]

qualified.sort(key=lambda x: x[1], reverse=True)

print(f"Date: {start.date()} (UTC)")
print("Subnets with more than 10 registrations:")
print("-" * 40)

for netuid, count in qualified:
    print(f"SN{netuid}: {count} registrations")

print(f"\nTotal qualifying subnets: {len(qualified)}")

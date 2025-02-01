import httpx
import os 
import json

try:
    API_KEY = "Bearer " + os.environ["API_KEY"]
except KeyError:
    raise Exception(
        "Please enter API Key for Yelp"
    )

url = "https://api.yelp.com/v3/businesses/search?location=Chicago&term=park&sort_by=best_match&limit=20"

headers = {
    "accept": "application/json"
}
headers["authorization"] = API_KEY

response = httpx.get(url, headers=headers)
data = response.json()

print(data)

# Save 
with open("yelp.json", "w") as f:
    json.dump(data, f, indent=1)

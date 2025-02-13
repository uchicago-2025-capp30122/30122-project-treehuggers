import httpx
import os 
import json
import time 

try:
    API_KEY = f"Bearer {os.environ["API_KEY"]}" 
except KeyError:
    raise Exception(
        "Please enter API Key for Yelp"
    )

headers = {"accept": "application/json"}
headers["authorization"] = API_KEY

all_businesses = []

for offset in range(0, 10001, 50):
    url = "https://api.yelp.com/v3/businesses/search?location=Chicago&categories=parkss&sort_by=best_match&offset=" + str(offset)
    response = httpx.get(url, headers=headers)
    
    print("Offset", offset,":",response.status_code)
    if response.status_code == 200:
        data = response.json()
        all_businesses.extend(data["businesses"])  
    else:
        print(response.status_code)
        break
    
    time.sleep(1)

all_data_dict = {"businesses": all_businesses}

# Save 
with open("data/yelp.json", "w") as f:
    json.dump(all_data_dict, f, indent=1)
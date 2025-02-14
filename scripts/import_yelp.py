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

url = "https://api.yelp.com/v3/businesses/search?"
headers = {"accept": "application/json",
           "authorization": API_KEY,
           "location": "Chicago",
           "categories": "parks",
           "sort_by": "best_match"
           }
all_businesses = []
for offset in range(0, 10001, 50):
    headers["offset": str(offset)]

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
import os 
#API_KEY = os.getenv('API_KEY')
import googlemaps

gmaps = googlemaps.Client(key=API_KEY)
import time
def get_parks():
    places = []
    next_page_token = None
    
    while len(places) < 50:
        if next_page_token:
            response = gmaps.places(
                query="park",
                location=(4.7110, -74.0721),
                radius=10000, 
                type="park", 
                page_token = next_page_token
            )
        else: 
            response = gmaps.places(
                query="park",
                location=(4.7110, -74.0721),
                radius=10000,
                type="bakery"
            )
        places.extend(response.get("results", []))
        
        next_page_token = response.get("next_page_token")
        if not next_page_token or len(places) >=50:
            break
        time.sleep(2)
    return places

def get_reviews(place_id):
    detalles = gmaps.place(place_id=place_id, fields=["name", "geometry/location", "rating", "reviews"])
    return detalles.get("result", {})

# Traemos las panaderias

parks = get_parks()

panaderias_df = []
for panaderia in parks: 
    details = get_reviews(panaderia["place_id"])
    name = details.get("name", "N/A")
    lat = details.get("geometry", {}).get("location", {}).get("lat", None)
    lng = details.get("geometry", {}).get("location", {}).get("lng", None)
    rating = details.get("rating", "N/A")
    reviews = details.get("reviews", [])
    
    review_texts = [review["text"] for review in reviews[:3]] if reviews else []
    
    panaderias_df.append({
        "Name": name,
        "Latitude": lat,
        "Longitude": lng,
        "Rating": rating,
        "Reviews": "; ".join(review_texts)
    })




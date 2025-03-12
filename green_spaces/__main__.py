import reviews.yelp 
import reviews.google 
import reviews.combine_reviews 
import parks.create_parks_geojson 
import parks.clean_park_polygons 
import index.index
import tract_level_analysis.grid_chicago
import tract_level_analysis.census
import tract_level_analysis.tracts_data
import viz.kepler_visual

def main():
    # Parks
    parks.create_parks_geojson.fetch_and_save_park_data()
    parks.clean_park_polygons.main()

    # Reviews
    reviews.yelp.main()
    reviews.google.main()
    reviews.combine_reviews.main()
    
    # Index
    index.index.main()

    # Census Tracts
    tract_level_analysis.grid_chicago.main()
    tract_level_analysis.census.main()
    tract_level_analysis.tracts_data.main()
    
    #Kepler Object
    viz.kepler_visual.main()

if __name__ == "__main__":
    main()

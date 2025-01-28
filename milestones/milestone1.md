# Tree Huggers

## Members

- Begum Akkas <bakkas@uchicago.edu>
- Evan Fantozzi <evanfantozzi@uchicago.edu>
- Grace Kleunder <graceek@uchicago.edu>
- Andres Camacho Baquero <afcamachob@uchicago.edu>

## Abstract
Our group is interested in investigating the availability of high-quality public
parks and other green space near affordable housing in Chicago. The city’s Department
of Housing maintains a list of affordable housing rental units, available online
and updated regularly. OpenStreetMap contains information on locations of green spaces,
and other websites such as Google and AllTrails allow users to provide ratings on green spaces.


We will reconcile the city’s Department of Housing data with spatial and user
review data on green space. For the data analysis component of this project,
we will be developing an index that quantifies the accessibility to high-quality
green spaces for the various public housing developments. This index will be
based upon the proximity of green spaces to public housing developments as well
as the quality of these green spaces, determined by ratings/reviews that we scrape
from AllTrails and/or Google.


## Preliminary Data Sources

## Data Source #1: Affordable Rental Housing Developments
- https://data.cityofchicago.org/Community-Economic-Development/Affordable-Rental-Housing-Developments-Map/k3g7-7kgc
- webpage
- N/A


## Data Source #2: Open Street Map API
- https://www.openstreetmap.org/about/api/
- API
- Potential challenges:
    - Not all green spaces are public. We will need to ensure we are categorizing 
    the green spaces correctly.

## Data Source #3: Here MAPS API
- https://www.here.com/platform/map-data 
- API
- Potential challenges:
    - Not sure if it's free
    - Unclear if it has reviews or some measure of quality of public green spaces


### Data Source #1: {Name}

- A URL to the data source.
- Is the data coming from a webpage, bulk data, or an API?
- Are there any challenges or uncertainity about the data at this point?

## Preliminary Project Plan

1. Initial Idea & preliminary plan: Conceptualize the idea of access to affordable housing that can also foster social interactions to impact human development through neighborhood interactions
2. Refinment and prototype: Create a simple mock-up prototype to envision the final product and the desired functionality
3. Data pipeline and integration: Implementation of a data pipeline, with at least 2 datasets APIs integrated, retrieved,  and cleaned to use them.
4. Data analysis: Analysis of the merged datasets, socioeconomic factors, and regression analysis to show relationships and insights
5. Dash configuration, Map settings (Kepler): Design of the desired filters and interactions (callbacks) for the aplication, the modules in kepler or mapbox to show the visualization, and the panels according to the prototype
6. Preliminary version for comments: A funcional version of the product, incorporating the comments raised in the meetings with James, and the project requirements.
7. Final output with demo and video: Preparation for project fair and final commits. Creation of audiovisual tools for enhancing storytelling around the project to add to the ReadMe file.

## Questions

1. Do you know if it's possible to use Google Places API? Is it free?
   - We may need some Google API to receive reviews of parks/public spaces
2. Does the CS department fund/have resources to run our program on a server?



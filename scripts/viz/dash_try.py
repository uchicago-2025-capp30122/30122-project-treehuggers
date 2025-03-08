import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
import json
import numpy as np
from pathlib import Path
from shapely import Point

# Color palette - Colorblind-friendly palette inspired by Viridis
COLORS = {
    'primary': '#440154',     # Deep purple
    'secondary': '#3b528b',   # Blue
    'tertiary': '#21918c',    # Teal
    'accent': '#5ec962',      # Green
    'highlight': '#fde725',   # Yellow
    'background': '#f8f9fa',  # Light gray
    'text': '#212529'         # Dark gray
}

def load_geojson_data(file_path):
    """Load GeoJSON files."""
    try:
        gdf = gpd.read_file(file_path)
        for col in gdf.columns:
            # Check if the column contains complex or unsupported types
            if gdf[col].dtype == 'object':
                # Try to convert to string
                gdf[col] = gdf[col].fillna('').astype(str)
        return gdf
    except Exception as e:
        print(f"Error loading GeoJSON file {file_path}: {e}")
        return None

def process_reviews(file_path):
    """Process reviews JSON file and convert to GeoDataFrame."""
    try:
        geometries = []
        data = []
        
        with open(file_path) as f:
            reviews_data = json.load(f)
            for review in reviews_data:
                geometries.append(Point(review['longitude'], review['latitude']))
                data.append(review)
        
        return gpd.GeoDataFrame(data, geometry=geometries)
    except Exception as e:
        print(f"Error processing reviews file {file_path}: {e}")
        return None

def create_dashboard(parks_gdf, housing_gdf, reviews_gdf, tracts_gdf):
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Clean up tracts data for visualization
    tracts_data = tracts_gdf.copy()
    # Replace negative values with NaN in income data
    tracts_data.loc[tracts_data['Median Household Income'] < 0, 'Median Household Income'] = np.nan
    
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Chicago Census Tracts and Parks Analysis", 
                            style={'color': COLORS['primary'], 'textAlign': 'center', 'marginTop': '20px'}),
                  width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("Map Layers:", style={'marginBottom': '10px'}),
                    dcc.Checklist(
                        id='layer-selector',
                        options=[
                            {'label': ' Census Tracts (Income)', 'value': 'tracts'},
                            {'label': ' Parks', 'value': 'parks'},
                            {'label': ' Housing', 'value': 'housing'},
                            {'label': ' Reviews', 'value': 'reviews'}
                        ],
                        value=['tracts', 'parks'],
                        inline=True,
                        labelStyle={'marginRight': '15px', 'fontSize': '15px'}
                    ),
                ], style={'marginBottom': '15px'}),
                dcc.Graph(id='main-map', style={'height': '70vh', 'border': f'1px solid {COLORS["secondary"]}', 'borderRadius': '5px'})
            ], width=8, className="mb-4"),
            
            # Right column with statistics
            dbc.Col([
                # Income histogram
                dbc.Card([
                    dbc.CardHeader("Income Distribution", 
                                  style={'backgroundColor': COLORS['secondary'], 'color': 'white', 'fontWeight': 'bold'}),
                    dbc.CardBody([
                        dcc.Graph(id='income-histogram')
                    ])
                ], className="mb-4", style={'border': f'1px solid {COLORS["secondary"]}'}),
                
                # Income vs Black Population scatter plot
                dbc.Card([
                    dbc.CardHeader("Income vs Black Population %", 
                                  style={'backgroundColor': COLORS['secondary'], 'color': 'white', 'fontWeight': 'bold'}),
                    dbc.CardBody([
                        dcc.Graph(id='income-race-scatter')
                    ])
                ], style={'border': f'1px solid {COLORS["secondary"]}'}),
            ], width=4)
        ])
    ], fluid=True, style={'backgroundColor': COLORS['background'], 'minHeight': '100vh'})
    
    @app.callback(
        [Output('main-map', 'figure'),
         Output('income-histogram', 'figure'),
         Output('income-race-scatter', 'figure')],
        [Input('layer-selector', 'value')]
    )
    def update_dashboard(selected_layers):
        # Create base map
        fig_map = go.Figure()
        
        # Add selected layers to the map
        if 'tracts' in selected_layers:
            # Add census tracts colored by income
            tract_fig = px.choropleth_maplibre(  # Updated from choropleth_mapbox
                tracts_data,
                geojson=tracts_data.__geo_interface__,
                locations=tracts_data.index,
                color='Median Household Income',
                color_continuous_scale='Viridis',
                opacity=0.7,
                labels={'Median Household Income': 'Median Income ($)'},
                hover_data={
                    'NAME': True,
                    'Median Household Income': True,
                    'Black Population Percentage': ':.1f'
                },
                maplibre_style="carto-positron",  # Updated from mapbox_style
                center={"lat": 41.8781, "lon": -87.6298},
                zoom=9,
            )
            fig_map = tract_fig
            
            # Update colorbar
            fig_map.update_layout(
                coloraxis_colorbar=dict(
                    title="Median<br>Income ($)",
                    thicknessmode="pixels", thickness=15,
                    lenmode="pixels", len=300,
                    yanchor="top", y=1,
                    ticks="outside"
                )
            )
        else:
            # Create empty map if tracts not selected
            fig_map = px.choropleth_maplibre(  # Updated from choropleth_mapbox
                maplibre_style="carto-positron",  # Updated from mapbox_style
                center={"lat": 41.8781, "lon": -87.6298},
                zoom=9,
            )
        
        if 'parks' in selected_layers and parks_gdf is not None:
            # Add parks as polygons
            fig_map.add_trace(
                go.Choroplethmaplibre(  # Updated from Choroplethmapbox
                    geojson=parks_gdf.__geo_interface__,
                    locations=parks_gdf.index.tolist(),
                    z=[1] * len(parks_gdf),  # Constant value for coloring
                    colorscale=[[0, COLORS['accent']], [1, COLORS['accent']]],
                    showscale=False,
                    marker_opacity=0.6,
                    marker_line_width=1,
                    name='Parks',
                    hovertemplate='<b>Park</b>: %{customdata[0]}<extra></extra>',
                    customdata=[[name] for name in parks_gdf.get('park_name', parks_gdf.index)]
                )
            )
        
        if 'housing' in selected_layers and housing_gdf is not None:
            # Add housing as points
            fig_map.add_trace(
                go.Scattermaplibre(  # Updated from Scattermapbox
                    lat=housing_gdf.geometry.y,
                    lon=housing_gdf.geometry.x,
                    mode='markers',
                    marker=dict(size=8, color=COLORS['highlight'], opacity=0.8),
                    text=housing_gdf.get('name', housing_gdf.index),
                    name='Housing'
                )
            )
        
        if 'reviews' in selected_layers and reviews_gdf is not None:
            # Add reviews as points
            fig_map.add_trace(
                go.Scattermaplibre(  # Updated from Scattermapbox
                    lat=reviews_gdf.geometry.y,
                    lon=reviews_gdf.geometry.x,
                    mode='markers',
                    marker=dict(size=6, color=COLORS['primary'], opacity=0.7),
                    text=[f"Rating: {r['rating']}<br>{r['text'][:50]}..." for r in reviews_gdf.to_dict('records')],
                    name='Reviews'
                )
            )
        
        # Update map layout
        fig_map.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            maplibre_style="carto-positron",  # Updated from mapbox_style
            maplibre=dict(  # Updated from mapbox
                center={"lat": 41.8781, "lon": -87.6298},
                zoom=9
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Create income histogram
        valid_income = tracts_data[tracts_data['Median Household Income'].notna()]
        fig_histogram = px.histogram(
            valid_income,
            x='Median Household Income',
            nbins=30,
            color_discrete_sequence=[COLORS['tertiary']],
            marginal='box',
            title='Distribution of Median Household Income'
        )
        fig_histogram.update_layout(
            xaxis_title='Median Household Income ($)',
            yaxis_title='Number of Census Tracts',
            template='plotly_white'
        )
        
        # Create income vs. black population scatter plot
        fig_scatter = px.scatter(
            valid_income,
            x='Median Household Income',
            y='Black Population Percentage',
            color='Black Population Percentage',
            color_continuous_scale='Viridis',
            size='Black Population Percentage',
            size_max=15,
            opacity=0.7,
            hover_data={
                'NAME': True,
                'Median Household Income': True,
                'Black Population Percentage': ':.1f'
            },
            title='Relationship Between Income and Black Population Percentage'
        )
        
        # Add trend line
        fig_scatter.update_traces(marker=dict(line=dict(width=0.5, color='white')))
        fig_scatter.update_layout(
            xaxis_title='Median Household Income ($)',
            yaxis_title='Black Population Percentage (%)',
            template='plotly_white',
            coloraxis_colorbar_title="Black<br>Population %"
        )
        
        # Add trend line
        valid_data = valid_income[['Median Household Income', 'Black Population Percentage']].dropna()
        if len(valid_data) > 1:
            fig_scatter.add_trace(
                go.Scatter(
                    x=valid_data['Median Household Income'].sort_values(),
                    y=valid_data['Black Population Percentage'].iloc[
                        valid_data['Median Household Income'].argsort()].rolling(window=20).mean(),
                    mode='lines',
                    line=dict(color=COLORS['highlight'], width=2, dash='dash'),
                    name='Rolling Average'
                )
            )
        
        return fig_map, fig_histogram, fig_scatter
    
    return app

def main():
    data_parent = Path(__file__).parent.parent
    path_parks = data_parent / "data/cleaned_park_polygons.geojson"
    path_housing = data_parent / "data/housing.geojson"
    path_reviews = data_parent / "data/combined_reviews_clean.json"
    path_tracts = data_parent / "blocks_and_tracks/data/processed/merged/merged_tract_data.geojson"

    parks_gdf = load_geojson_data(path_parks)
    housing_gdf = load_geojson_data(path_housing)
    reviews_gdf = process_reviews(path_reviews)
    tracts_gdf = load_geojson_data(path_tracts)
    
    # Print metadata about the loaded tracts
    if tracts_gdf is not None:
        print(f"Loaded {len(tracts_gdf)} census tracts")
        print(f"Columns available: {tracts_gdf.columns.tolist()}")

    app = create_dashboard(parks_gdf, housing_gdf, reviews_gdf, tracts_gdf)
    app.run_server(debug=True)

if __name__ == "__main__":
    main()
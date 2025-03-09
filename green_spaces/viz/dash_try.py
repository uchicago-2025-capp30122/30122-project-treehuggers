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

def create_dashboard(tracts_gdf, kepler_path=None):
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Clean up tracts data for visualization
    tracts_data = tracts_gdf.copy() if tracts_gdf is not None else None
    if tracts_data is not None:
        # Replace negative values with NaN in income data
        tracts_data.loc[tracts_data['Median Household Income'] < 0, 'Median Household Income'] = np.nan
    
    # Create dashboard content (existing dashboard content)
    dashboard_content = create_dashboard_content(tracts_data)
    
    # Create project summary content (Tab 1)
    project_summary_content = create_project_summary()
    
    # Create Kepler map content (Tab 3)
    kepler_map_content = create_kepler_map()
    
    # Main app layout with tabs
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Chicago Parks and Demographics Analysis", 
                          style={'color': COLORS['primary'], 'textAlign': 'center', 'marginTop': '20px'}),
                  width=12)
        ]),
        
        dbc.Tabs([
            dbc.Tab(project_summary_content, label="Project Overview", tab_id="tab-overview",
                  label_style={"color": COLORS['secondary']}, active_label_style={"color": COLORS['primary']}),
            dbc.Tab(dashboard_content, label="Interactive Dashboard", tab_id="tab-dashboard",
                  label_style={"color": COLORS['secondary']}, active_label_style={"color": COLORS['primary']}),
            dbc.Tab(kepler_map_content, label="Detailed Kepler Map", tab_id="tab-kepler-map",
                  label_style={"color": COLORS['secondary']}, active_label_style={"color": COLORS['primary']}),
        ], id="tabs", active_tab="tab-overview"),
        
    ], fluid=True, style={'backgroundColor': COLORS['background'], 'minHeight': '100vh'})
    
    # Register callbacks
    register_callbacks(app, tracts_data, kepler_path)
    
    return app

def create_project_summary():
    """Creates the project summary/landing page content."""
    
    # Try to load markdown if exists, otherwise use HTML
    summary_path = Path(__file__).parent / "project_summary.md"
    
    if summary_path.exists():
        # Load from markdown file
        with open(summary_path, 'r') as f:
            markdown_content = f.read()
            
        return dbc.Card(
            dbc.CardBody([
                dcc.Markdown(markdown_content, style={'padding': '20px'})
            ]),
            className="mt-4 mb-4",
            style={'border': f'1px solid {COLORS["secondary"]}'}
        )
    else:
        # Default HTML content
        return dbc.Card(
            dbc.CardBody([
                html.H2("Chicago Parks and Demographics Analysis", className="card-title"),
                html.H4("Project Overview", className="card-subtitle mt-3 mb-4", style={'color': COLORS['secondary']}),
                html.P([
                    "This project explores the relationship between parks, housing, and demographic data in Chicago. ",
                    "We analyze how park access and quality correlate with income levels and racial demographics across census tracts."
                ], className="card-text"),
                html.H4("Key Questions", className="mt-4 mb-3", style={'color': COLORS['secondary']}),
                html.Ul([
                    html.Li("How does park access vary across different neighborhoods in Chicago?"),
                    html.Li("Is there a relationship between income levels and proximity to quality parks?"),
                    html.Li("How do demographic factors correlate with park distribution?"),
                ], style={'marginBottom': '20px'}),
                html.H4("Data Sources", className="mt-4 mb-3", style={'color': COLORS['secondary']}),
                html.Ul([
                    html.Li("Chicago Park District data"),
                    html.Li("Census tract demographic information"),
                    html.Li("Housing location data"),
                ]),
                html.Div([
                    html.P("To explore the data, navigate to the Interactive Dashboard and Detailed Map tabs above."),
                ], className="mt-4 alert alert-info")
            ]),
            className="mt-4 mb-4",
            style={'border': f'1px solid {COLORS["secondary"]}'}
        )

def create_kepler_map():
    """Creates the Kepler.gl map tab content."""
    
    return html.Div([
        html.H4("Detailed Kepler.gl Map", className="mb-4", style={'color': COLORS['secondary']}),
        html.P([
            "The Kepler.gl map provides a more detailed, interactive view of our data. ",
            "You can explore park locations, demographics, and other data layers with advanced filtering capabilities."
        ], className="mb-4"),
        
        # Option 1: Use an iframe to embed a hosted Kepler map
        #html.Iframe(
        #    src="about:blank",
        #    style={'width': '100%', 'height': '700px', 'border': f'1px solid {COLORS["secondary"]}'},
        #    id="kepler-iframe"
        #),
        
        # Option 2: If you want to add your Kepler HTML file content directly
        html.Div(id='kepler-container',
                             style={
                'width': '100%', 
                'height': '700px',
                'position': 'relative',
                'overflow': 'hidden',
                'border': f'1px solid {COLORS["secondary"]}',
                'background': '#f8f9fa',  # Light background to see if the map is loading
                'marginBottom': '20px'
            }),
        
        html.Div([
            html.P("Note: The Kepler map allows you to toggle different data layers, adjust opacity, and filter data based on various attributes."),
            html.P("Use the controls in the left panel to customize your view.")
        ], className="mt-3 alert alert-info")
    ])

def create_dashboard_content(tracts_data):
    """Creates the dashboard content (previously the main content)."""
    
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.H4("Map Layers:", style={'marginBottom': '10px'}),
                dcc.Dropdown(
                    id='variable-selector',
                    options=[
                        {'label': 'Median Household Income', 'value': 'Median Household Income'},
                        {'label': 'Black Population Percentage', 'value': 'Black Population Percentage'},
                        {'label': 'Park Rating Index', 'value': 'rating_index'},
                    ],
                    value='rating_index',
                    clearable=False,
                    style={'width': '100%'}
                ),
            ], style={'marginBottom': '15px'}),
            dcc.Graph(id='main-map', style={'height': '70vh', 'border': f'1px solid {COLORS["secondary"]}', 'borderRadius': '5px'})
        ], width=7, className="mb-4"),
        
        # Right column with statistics
        dbc.Col([
            # Variable histogram
            dbc.Card([
                dbc.CardHeader("Variable Distribution", 
                              style={'backgroundColor': COLORS['secondary'], 'color': 'white', 'fontWeight': 'bold'}),
                dbc.CardBody([
                    dcc.Graph(id='variable-histogram')
                ])
            ], className="mb-4", style={'border': f'1px solid {COLORS["secondary"]}'}),
            
            # Park Index vs Selected Variable scatter plot
            dbc.Card([
                dbc.CardHeader("Relationship with Park Rating Index", 
                              style={'backgroundColor': COLORS['secondary'], 'color': 'white', 'fontWeight': 'bold'}),
                dbc.CardBody([
                    dcc.Graph(id='variable-scatter')
                ])
            ], style={'border': f'1px solid {COLORS["secondary"]}'}),
        ], width=5)
    ])

def register_callbacks(app, tracts_data, kepler_path=None):
    """Register all callbacks for the app."""
    
    @app.callback(
        [Output('main-map', 'figure'),
         Output('variable-histogram', 'figure'),
         Output('variable-scatter', 'figure')],
        [Input('variable-selector', 'value')]
    )
    def update_dashboard(selected_variable):
        if tracts_data is None or selected_variable not in tracts_data.columns:
            # Create empty figures if data not available
            empty_fig = go.Figure()
            empty_fig.update_layout(title="No data available")
            return empty_fig, empty_fig, empty_fig
            
        # Create map colored by selected variable
        fig_map = px.choropleth_map(
            tracts_data,
            geojson=tracts_data.__geo_interface__,
            locations=tracts_data.index,
            color=selected_variable,
            color_continuous_scale='Viridis',
            opacity=0.8,
            labels={
                'Median Household Income': 'Median Income ($)',
                'Black Population Percentage': 'Black Population (%)',
                'rating_index': 'Park Rating Index'
            },
            hover_data={
                'TRACTCE': True,
                'Median Household Income': True,
                'Black Population Percentage': True,
                'rating_index': ':.2f',
            },
            center={"lat": 41.8781, "lon": -87.6298},
            zoom=10,
        )
        
        # Update colorbar title based on selected variable
        title_mapping = {
            'Median Household Income': 'Median<br>Income ($)',
            'Black Population Percentage': 'Black<br>Population (%)',
            'rating_index': 'Park<br>Rating Index'
        }
        
        fig_map.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar=dict(
                title=title_mapping.get(selected_variable, selected_variable),
                thicknessmode="pixels", thickness=15,
                lenmode="pixels", len=300,
                yanchor="top", y=1,
                ticks="outside"
            )
        )
        
        # Create histogram for selected variable
        valid_data = tracts_data[tracts_data[selected_variable].notna()]
        if len(valid_data) > 0:
            fig_histogram = px.histogram(
                valid_data,
                x=selected_variable,
                nbins=30,
                color_discrete_sequence=[COLORS['tertiary']],
                marginal='box',
                title=f'Distribution of {selected_variable}'
            )
            fig_histogram.update_layout(
                xaxis_title=selected_variable,
                yaxis_title='Number of Census Tracts',
                template='plotly_white'
            )
        else:
            fig_histogram = go.Figure()
            fig_histogram.update_layout(title=f"No data available for {selected_variable}")
        
        # Create scatter plot: Park Rating Index vs Selected Variable
        # (Only if selected variable is not the rating index itself)
        if selected_variable != 'rating_index' and 'rating_index' in tracts_data.columns:
            scatter_data = tracts_data[[selected_variable, 'rating_index', 'TRACTCE']].dropna()
            
            if len(scatter_data) > 0:
                fig_scatter = px.scatter(
                    scatter_data,
                    x=selected_variable,
                    y='rating_index',
                    color=selected_variable,
                    color_continuous_scale='Viridis',
                    opacity=0.7,
                    hover_data={
                        'TRACTCE': True,
                        selected_variable: True,
                        'rating_index': ':.2f'
                    },
                    title=f'Park Rating Index vs {selected_variable}'
                )
                
                fig_scatter.update_traces(marker=dict(size=10, line=dict(width=0.5, color='white')))
                fig_scatter.update_layout(
                    xaxis_title=selected_variable,
                    yaxis_title='Park Rating Index',
                    template='plotly_white'
                )
                
                # Add trend line
                if len(scatter_data) > 10:
                    x_sorted = scatter_data[selected_variable].sort_values()
                    y_sorted = scatter_data['rating_index'].iloc[scatter_data[selected_variable].argsort()]
                    
                    # Calculate rolling average for trend line
                    window_size = min(20, max(5, len(scatter_data) // 10))
                    y_rolling = y_sorted.rolling(window=window_size).mean()
                    
                    fig_scatter.add_trace(
                        go.Scatter(
                            x=x_sorted,
                            y=y_rolling,
                            mode='lines',
                            line=dict(color=COLORS['highlight'], width=2, dash='dash'),
                            name='Trend'
                        )
                    )
            else:
                fig_scatter = go.Figure()
                fig_scatter.update_layout(title="Insufficient data for scatter plot")
        
        elif selected_variable == 'rating_index':
            # If rating_index is selected, show relationship with income instead
            scatter_data = tracts_data[['Median Household Income', 'rating_index','TRACTCE']].dropna()
            
            if len(scatter_data) > 0:
                fig_scatter = px.scatter(
                    scatter_data,
                    x='Median Household Income',
                    y='rating_index',
                    color='rating_index',
                    color_continuous_scale='Viridis',
                    opacity=0.7,
                    hover_data={
                        'TRACTCE': True,
                        'Median Household Income': True,
                        'rating_index': ':.2f'
                    },
                    title='Park Rating Index vs Median Income'
                )
                
                fig_scatter.update_traces(marker=dict(size=10, line=dict(width=0.5, color='white')))
                fig_scatter.update_layout(
                    xaxis_title='Median Household Income',
                    yaxis_title='Park Rating Index',
                    template='plotly_white'
                )
                
                # Add trend line if enough data points
                if len(scatter_data) > 10:
                    x_sorted = scatter_data['Median Household Income'].sort_values()
                    y_sorted = scatter_data['rating_index'].iloc[scatter_data['Median Household Income'].argsort()]
                    
                    # Calculate rolling average for trend line
                    window_size = min(20, max(5, len(scatter_data) // 10))
                    y_rolling = y_sorted.rolling(window=window_size).mean()
                    
                    fig_scatter.add_trace(
                        go.Scatter(
                            x=x_sorted,
                            y=y_rolling,
                            mode='lines',
                            line=dict(color=COLORS['highlight'], width=2, dash='dash'),
                            name='Trend'
                        )
                    )
            else:
                fig_scatter = go.Figure()
                fig_scatter.update_layout(title="Insufficient data for scatter plot")
        else:
            fig_scatter = go.Figure()
            fig_scatter.update_layout(title="Park Rating Index data not available")
        
        return fig_map, fig_histogram, fig_scatter
    
    # Add callback to load Kepler HTML content
    @app.callback(
        Output('kepler-container', 'children'),
        [Input('tabs', 'active_tab')]
    )
    def load_kepler_content(active_tab):
        if active_tab == "tab-kepler-map":
            # Path to your Kepler HTML file
            kepler_file_path = kepler_path if kepler_path else Path(__file__).parent / "chicago_parks_kepler.html"
            
            if kepler_file_path.exists():
                try:
                    with open(kepler_path, 'r', encoding='utf-8') as f:
                        kepler_html = f.read()
                    return html.Iframe(
                        srcDoc=kepler_html,
                        style={
                        'width': '100%', 
                        'height': '700px', 
                        'border': 'none',
                        'display': 'block',
                        'overflow': 'hidden',  # Prevent scrollbars
                        'position': 'relative'  # Make sure positioning works
                    }
                    )
                except Exception as e:
                    return html.Div([
                        html.P(f"Error loading Kepler map: {e}"),
                    ], className="alert alert-danger")
            else:
                return html.Div([
                    html.P("Kepler map HTML file not found."),
                ], className="alert alert-warning")
        return None

def main():
    data_parent = Path(__file__).parent.parent.parent
    path_tracts = data_parent / "data/grid_and_tracts/processed/merged/merged_tract_data.geojson"
    path_kepler = Path(__file__).parent.parent / "viz/chicago_parks_kepler.html"
    tracts_gdf = load_geojson_data(path_tracts)
    
    # Print metadata about the loaded tracts
    if tracts_gdf is not None:
        print(f"Loaded {len(tracts_gdf)} census tracts")
        print(f"Columns available: {tracts_gdf.columns.tolist()}")

    app = create_dashboard(tracts_gdf, path_kepler)
    app.run_server(debug=True)

if __name__ == "__main__":
    main()
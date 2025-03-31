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

# Color palette - Colorblind-friendly palette
COLORS = {
    'primary': '#440154',     # Deep purple
    'secondary': '#3b528b',   # Blue
    'tertiary': '#21918c',    # Teal
    'accent': '#5ec962',      # Green
    'highlight': '#fde725',   # Yellow
    'redlines' : "#f7022a",    #Red
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

def create_housing_tab_content(housing_data):
    """Create content for the housing data tab."""
    if housing_data is None or len(housing_data) == 0:
        return html.Div(["No housing data available."], className="alert alert-warning")
    
    # Calculate statistics
    total_units = len(housing_data)
    mean_rating = housing_data['rating_index'].mean()
    
    return html.Div([
        dbc.Row([
            # Left column with heatmap
            dbc.Col([
                html.H4("Housing distribution", style={'marginBottom': '15px', 'color': COLORS['secondary']}),
                dcc.Graph(
                    id='housing-heatmap',
                    figure=create_combined_map(housing_data),
                    style={'height': '80vh', 'border': f'1px solid {COLORS["secondary"]}', 'borderRadius': '5px'}
                )
            ], width=7),
            
            # Right column with statistics cards
            dbc.Col([
                # Cards for statistics
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Affordable Housing Buildings", 
                                         style={'backgroundColor': COLORS['secondary'], 'color': 'white', 'fontWeight': 'bold'}),
                            dbc.CardBody([
                                html.H2(f"{int(total_units):,}", className="card-title text-center"),
                                html.P("Affordable housing buildings across Chicago", className="card-text text-center")
                            ])
                        ], className="mb-4", style={'border': f'1px solid {COLORS["secondary"]}'}),
                    ], width=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Average Accessibility Index", 
                                         style={'backgroundColor': COLORS['secondary'], 'color': 'white', 'fontWeight': 'bold'}),
                            dbc.CardBody([
                                html.H2(f"{mean_rating:.2f}", className="card-title text-center"),
                                html.P("Mean green spaces accessibility index near housing", className="card-text text-center")
                            ])
                        ], className="mb-4", style={'border': f'1px solid {COLORS["secondary"]}'}),
                    ], width=6),
                ]),
                
                # Histogram
                dbc.Card([
                    dbc.CardHeader("Distribution of Accessibility Index", 
                                  style={'backgroundColor': COLORS['secondary'], 'color': 'white', 'fontWeight': 'bold'}),
                    dbc.CardBody([
                        dcc.Graph(
                            id='rating-histogram',
                            figure=create_rating_histogram(housing_data),
                        )
                    ])
                ], style={'border': f'1px solid {COLORS["secondary"]}'}),
            ], width=5)
        ])
    ])

def create_housing_heatmap(housing_data):
    """Create a heatmap of housing locations."""
    zmin = housing_data['rating_index'].min()
    zmax = housing_data['rating_index'].max()
    
    fig = px.density_map(
        housing_data,
        lat='latitude',
        lon='longitude',
        z='rating_index',
        radius=15,
        center={"lat": 41.8781, "lon": -87.6298},
        zoom=9.5,
        color_continuous_scale='Magma',
        opacity=0.3,
        title="Housing Locations by Green Rating Index",
        range_color=[zmin, zmax],
        labels={'rating_index': 'Accessibility Index'},
        hover_data={
            'park_count': True,
            'rating_index': ':.2f',
            'size_index': ':.2f'
        },
        map_style = 'light', 
    )
    
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title='Accessibility<br>Index',
            thicknessmode="pixels", thickness=15,
            lenmode="pixels", len=300,
            yanchor="top", y=1,
            ticks="outside"
        ), 
        map_style = 'light', 
    )
    return fig

def create_housing_scatter_map(housing_data):
    """Create a scatter map of housing locations colored by rating index."""
    fig = px.scatter_map(
        housing_data,
        lat='latitude',
        lon='longitude',
        color='rating_index',
        color_continuous_scale='Magma',
        size = "rating_index",
        size_max=15,
        zoom=10,
        center={"lat": 41.8781, "lon": -87.6298},
        title="Housing Locations by Accessibility Index",
        labels={'rating_index': 'Accessibility Index'},
        hover_data={
            'park_count': True,
            'rating_index': ':.2f',
            'size_index': ':.2f'
        },
        map_style='light',
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title='Accessibility<br>Index',
            thicknessmode="pixels", thickness=15,
            lenmode="pixels", len=300,
            yanchor="top", y=1,
            ticks="outside"
        ),
    )
    return fig

def create_combined_map(housing_data):
    """Combine heatmap and scatter map of housing locations."""
    heatmap_fig = create_housing_heatmap(housing_data)
    scatter_fig = create_housing_scatter_map(housing_data)

    # Combine the data from both figures
    combined_fig = heatmap_fig
    combined_fig.add_traces(scatter_fig.data)

    return combined_fig


def create_rating_histogram(housing_data):
    """Create a histogram of rating index values."""
    fig = px.histogram(
        housing_data,
        x='rating_index',
        nbins=30,
        color_discrete_sequence=[COLORS['tertiary']],
        opacity=0.7,
        marginal='box',
        title='Distribution of Green Spaces Accessibility Index'
    )
    
    fig.update_layout(
        xaxis_title="Accessibility Index",
        yaxis_title="Number of Housing Buildings",
        template='plotly_white'
    )
    
    return fig


def create_dashboard(tracts_gdf, housing_gdf, kepler_path=None):
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Clean up tracts data for visualization
    tracts_data = tracts_gdf.copy() if tracts_gdf is not None else None
    if tracts_data is not None:
        # Replace negative values with NaN in income data
        tracts_data.loc[tracts_data['Median Household Income'] < 0, 'Median Household Income'] = np.nan
    
    # Create project summary content (Tab 1)
    project_summary_content = create_project_summary()
    housing_tab_content = create_housing_tab_content(housing_gdf)
    # Create dashboard content
    dashboard_content = create_dashboard_content(tracts_data)
    # Create Kepler map content (Tab 3)
    kepler_map_content = create_kepler_map()
    
    # Main app layout with tabs
    app.layout = html.Div([
        # Sticky header
        html.Div([
            html.H1("Affordable Housing & Green Space Equity in Chicago", 
                  style={'color': COLORS['primary'], 'textAlign': 'center', 'margin': '0', 'padding': '15px'})
        ], style={
            'position': 'sticky', 
            'top': '0',
            'backgroundColor': COLORS['background'],
            'borderBottom': f'1px solid {COLORS["secondary"]}',
            'zIndex': '1000',  # Ensure the header stays above other content
            'width': '100%',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'  # Optional: adds a subtle shadow
        }),
        dbc.Container([
            dbc.Tabs([
            dbc.Tab(project_summary_content, label="Project Overview", tab_id="tab-overview",
                  label_style={"color": COLORS['secondary']}, active_label_style={"color": COLORS['primary']}),
            dbc.Tab(housing_tab_content, label="Housing Data", tab_id="tab-housing", 
                  label_style={"color": COLORS['secondary']}, active_label_style={"color": COLORS['primary']}),
            dbc.Tab(kepler_map_content, label="Detailed Index Map", tab_id="tab-index-map",
                  label_style={"color": COLORS['secondary']}, active_label_style={"color": COLORS['primary']}),
            dbc.Tab(dashboard_content, label="Tract-Level Dashboard", tab_id="tab-dashboard",
                  label_style={"color": COLORS['secondary']}, active_label_style={"color": COLORS['primary']}),
        ], id="tabs", active_tab="tab-overview"),
        
        ], fluid=True, style={'backgroundColor': COLORS['background'], 'minHeight': '100vh'})
    ])
    # Register callbacks
    register_callbacks(app, tracts_data, kepler_path)
    
    return app

def create_project_summary():
    """Creates the project summary/landing page content."""
    
    # Try to load markdown if exists, otherwise we will use HTML
    summary_path = Path(__file__).parent / "project_summary.md"
    
    if summary_path.exists():
        # Load from markdown file
        with open(summary_path, 'r') as f:
            markdown_content = f.read()
            
        return dbc.Card(
            dbc.CardBody([
                dcc.Markdown(markdown_content, style={'padding': '20px'}, dangerously_allow_html=True)
            ]),
            className="mt-4 mb-4",
            style={'border': f'1px solid {COLORS["secondary"]}'}
        )
    else:
        # Default HTML content
        return dbc.Card(
            dbc.CardBody([
                html.H2("Chicago Green Spaces and Demographics Analysis", className="card-title"),
                html.H4("Project Overview", className="card-subtitle mt-3 mb-4", style={'color': COLORS['secondary']}),
                html.P([
                    "This project explores the relationship between green spaces, housing, and demographic data in Chicago. ",
                    "We analyze how park access and quality correlate with income levels and racial demographics across census tracts."
                ], className="card-text"),
                html.H4("Key Questions", className="mt-4 mb-3", style={'color': COLORS['secondary']}),
                html.Ul([
                    html.Li("How does park access vary across different neighborhoods in Chicago?"),
                    html.Li("Is there a relationship between income levels and proximity to quality green spaces?"),
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
        html.H4("Detailed Index Map", className="mb-4", style={'color': COLORS['secondary']}),
        html.P([
            "This interactive map provides a detailed view of our data. Use the layer toggles on the right-hand side to display affordable housing buildings, green spaces, and the Accessibility Index hexbins. ",
            "Each hexbin represents the aggregated Accessibility Index for its area. Hover over a hexbin to see how many affordable housing buildings it contains and the corresponding index value."
        ], className="mb-4"),
        
        html.Div(id='kepler-container',
                 style={
                    'width': '80%', 
                    'height': '200px',
                    'position': 'relative',
                    'overflow': 'hidden',
                    'border': f'1px solid {COLORS["secondary"]}',
                    'background': '#f8f9fa', 
                    'marginBottom': '5px'
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
                        {'label': 'Affordable Housing Buildings', 'value': 'Affordable_Housing_Units'},
                        {'label': 'Median Household Income', 'value': 'Median Household Income'},
                        {'label': 'Green Spaces Accessibility Index', 'value': 'rating_index'},
                    ],
                    value='rating_index',
                    clearable=False,
                    style={'width': '100%'}
                ),
            ], style={'marginBottom': '15px'}),
            dcc.Graph(id='main-map', style={'height': '70vh', 'border': f'1px solid {COLORS["secondary"]}', 'borderRadius': '5px'}),
            
            # New card for average park index
            dbc.Card([
                dbc.CardHeader("Average Accessibility Index", 
                              style={'backgroundColor': COLORS['secondary'], 'color': 'white', 'fontWeight': 'bold'}),
                dbc.CardBody([
                    html.Div([
                        html.H3(id='avg-rating-display', className="card-title text-center"),
                        html.P("Mean value of green spaces accessibility index across census tracts", className="card-text text-center")
                    ])
                ])
            ], className="mt-3 mb-4", style={'border': f'1px solid {COLORS["secondary"]}'}), 
        ], width=7, className="mb-4"),
        
        # Right column with statistics
        dbc.Col([
            # Variable histogram
            dbc.Card([
                dbc.CardHeader("Variable Distribution", 
                              style={'backgroundColor': COLORS['secondary'], 'color': 'white', 'fontWeight': 'bold'}),
                dbc.CardBody([
                    dcc.Graph(id='variable-histogram', style={'height': '35vh'})
                ])
            ], className="mb-4", style={'border': f'1px solid {COLORS["secondary"]}'}),
            
            # Park Index vs Selected Variable scatter plot
            dbc.Card([
                dbc.CardHeader("Relationship with Average Accessibility Index by Tracts", 
                              style={'backgroundColor': COLORS['secondary'], 'color': 'white', 'fontWeight': 'bold'}),
                dbc.CardBody([
                    dcc.Graph(id='variable-scatter', style={'height': '45vh'})
                ])
            ], style={'border': f'1px solid {COLORS["secondary"]}'}),
        ], width=5)
    ])

def register_callbacks(app, tracts_data, kepler_path):
    """Register all callbacks for the app."""
    
    @app.callback(
        [Output('main-map', 'figure'),
         Output('variable-histogram', 'figure'),
         Output('variable-scatter', 'figure'),
         Output('avg-rating-display', 'children')],
        [Input('variable-selector', 'value'),
         Input('main-map', 'relayoutData'),
         Input('main-map', 'selectedData')
         ]
    )
    def update_dashboard(selected_variable, relayout_data, selected_data):
        if tracts_data is None or selected_variable not in tracts_data.columns:
            # Create empty figures if data not available
            empty_fig = go.Figure()
            empty_fig.update_layout(title="No data available")
            return empty_fig, empty_fig, empty_fig, "N/A"
        # Default center and zoom
        center = {"lat": 41.8761, "lon": -87.6298}
        zoom = 10.5
        
        if relayout_data and 'mapbox.center' in relayout_data and 'mapbox.zoom' in relayout_data:
            center = relayout_data['mapbox.center']
            zoom = relayout_data['mapbox.zoom']
        
        #Filter data on map zoom and selection
        filtered_data = tracts_data.copy()

        if relayout_data and 'mapbox._derived' in relayout_data:
            # Get the polygon coordinates
            coords = relayout_data['mapbox._derived']['coordinates'][0]
            # Extract lons and lats from polygon points
            lons = [pt[0] for pt in coords]
            lats = [pt[1] for pt in coords]
            min_lon, max_lon = min(lons), max(lons)
            min_lat, max_lat = min(lats), max(lats)
            filtered_data = filtered_data.cx[min_lon:max_lon, min_lat:max_lat]
        
        if selected_data and 'points' in selected_data:
            selected_ids = [p['customdata'][0] for p in selected_data['points'] if 'customdata' in p]
            if selected_ids:
                filtered_data = filtered_data[filtered_data['TRACTCE'].isin(selected_ids)]
        # Calculate average rating for the filtered data
        avg_rating = filtered_data['rating_index'].mean() if 'rating_index' in filtered_data.columns else float('nan')
        avg_rating_display = f"{avg_rating:.2f}" if not pd.isna(avg_rating) else "N/A"
            
        # Create map colored by selected variable
        fig_map = px.choropleth_map(
            filtered_data,
            geojson=filtered_data.__geo_interface__,
            locations=filtered_data.index,
            color=selected_variable,
            color_continuous_scale='Viridis',
            opacity=0.6,
            center=center,
            zoom = zoom,
            custom_data=['TRACTCE'],
            labels={
                'Median Household Income': 'Median Income ($)',
                'rating_index': 'Accessibility Index'
            },
            hover_data={
                'Median Household Income': True,
                'rating_index': ':.2f',
            },
        )
        
        # Update colorbar title based on selected variable
        title_mapping = {
            'Affordable_Housing_Units': 'Affordable<br>Housing<br>Buildings',
            'Median Household Income': 'Median<br>Income ($)',
            'rating_index': ' Accessibility<br>Index'
        }
        
        label_mapping = {
            'Affordable_Housing_Units': 'Affordable Housing Buildings',
            'Median Household Income': 'Median Household Income', 
            'rating_index': 'Accessibility Index'
        }
        display_name =  label_mapping.get(selected_variable, selected_variable)

        fig_map.update_layout(
            mapbox=dict(
                center=center,
                zoom=zoom
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            uirevision='constant',
            coloraxis_colorbar=dict(
                title=title_mapping.get(selected_variable, selected_variable),
                thicknessmode="pixels", thickness=15,
                lenmode="pixels", len=300,
                yanchor="top", y=1,
                ticks="outside"
            )
        )

        # Create histogram for selected variable
        valid_data = filtered_data[filtered_data[selected_variable].notna()]
        if len(valid_data) > 0:
            fig_histogram = px.histogram(
                valid_data,
                x=selected_variable,
                nbins=30,
                color_discrete_sequence=[COLORS['tertiary']],
                marginal='box',
                title=f'Distribution of {display_name}'
            )
            fig_histogram.update_layout(
                xaxis_title=selected_variable,
                yaxis_title='Number of Census Tracts',
                template='plotly_white'
            )
        else:
            fig_histogram = go.Figure()
            fig_histogram.update_layout(title=f"No data available for {display_name}")
        
        # Create scatter plot: Park Rating Index vs Selected Variable
        # (if selected variable is not the rating index itself)
        if selected_variable != 'rating_index' and 'rating_index' in filtered_data.columns:
            scatter_data = filtered_data[[selected_variable, 'rating_index', 'TRACTCE']].dropna()
            
            if len(scatter_data) > 0:
                fig_scatter = px.scatter(
                    scatter_data,
                    x=selected_variable,
                    y='rating_index',
                    color=selected_variable,
                    color_continuous_scale='Viridis',
                    opacity=0.7,
                    hover_data={
                        selected_variable: True,
                        'rating_index': ':.2f'
                    },
                    title=f'Green Spaces Accessibility Index vs {display_name}'
                )
                
                fig_scatter.update_traces(marker=dict(size=10, line=dict(width=0.5, color='white')))
                fig_scatter.update_layout(
                    xaxis_title=selected_variable,
                    yaxis_title='Accessibility Index',
                    coloraxis_colorbar=dict(title=''),
                    template='plotly_white', 
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.35,  # Position below the plot
                        xanchor="center",
                        x=0.5
                    )
                )
                
                # Add trend line
                if len(scatter_data) > 10:
                    valid_mask = ~(np.isnan(scatter_data[selected_variable]) | np.isnan(scatter_data['rating_index']))
                    x_vals = scatter_data[selected_variable].values[valid_mask]
                    y_vals = scatter_data['rating_index'].values[valid_mask]
                    
                    # Calculate linear regression
                    if len(x_vals) > 1:  # We need enough points
                        slope, intercept = np.polyfit(x_vals, y_vals, 1)
                        
                        # Create x values for the regression line
                        x_min = scatter_data[selected_variable].min()
                        x_max = scatter_data[selected_variable].max()
                        x_line = np.array([x_min, x_max])
                        y_line = slope * x_line + intercept
                        
                        # Add regression line to plot
                        fig_scatter.add_trace(
                            go.Scatter(
                                x=x_line, 
                                y=y_line,
                                mode='lines',
                                line=dict(color=COLORS['redlines'], width=2),
                                name=f'Trend (y = {slope:.4f}x + {intercept:.2f})'
                            )
                        )
            else:
                fig_scatter = go.Figure()
                fig_scatter.update_layout(title="Insufficient data for scatter plot")
        
        elif selected_variable == 'rating_index':
            # If rating_index is selected, show relationship with income instead
            scatter_data = filtered_data[['Median Household Income', 'rating_index','TRACTCE']].dropna()
            
            if len(scatter_data) > 0:
                fig_scatter = px.scatter(
                    scatter_data,
                    x='Median Household Income',
                    y='rating_index',
                    color='rating_index',
                    color_continuous_scale='Viridis',
                    opacity=0.7,
                    hover_data={
                        'Median Household Income': True,
                        'rating_index': ':.2f'
                    },
                    title='Green Spaces Accessibility Index vs Median Income'
                )
                
                fig_scatter.update_traces(marker=dict(size=10, line=dict(width=0.5, color='white')))
                fig_scatter.update_layout(
                    xaxis_title='Median Household Income',
                    yaxis_title='Green Spaces Accessibility Index',
                    template='plotly_white', 
                    coloraxis_colorbar=dict(title=''),
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.35,  # Position below the plot
                        xanchor="center",
                        x=0.5
                    )
                )
                
                # Add trend line if enough data points
                if len(scatter_data) > 10:
                    # Clean data for regression
                    valid_mask = ~(np.isnan(scatter_data['Median Household Income']) | np.isnan(scatter_data['rating_index']))
                    x_vals = scatter_data['Median Household Income'].values[valid_mask]
                    y_vals = scatter_data['rating_index'].values[valid_mask]
                    
                    # Calculate linear regression
                    if len(x_vals) > 1:
                        slope, intercept = np.polyfit(x_vals, y_vals, 1)
                        
                        # Create x values for the regression line
                        x_min = scatter_data['Median Household Income'].min()
                        x_max = scatter_data['Median Household Income'].max()
                        x_line = np.array([x_min, x_max])
                        y_line = slope * x_line + intercept
                        
                        # Add regression line to plot
                        fig_scatter.add_trace(
                            go.Scatter(
                                x=x_line, 
                                y=y_line,
                                mode='lines',
                                line=dict(color=COLORS['redlines'], width=2),
                                name=f'Trend (y = {slope:.4f}x + {intercept:.2f})'
                            )
                    )
            else:
                fig_scatter = go.Figure()
                fig_scatter.update_layout(title="Insufficient data for scatter plot")
        else:
            fig_scatter = go.Figure()
            fig_scatter.update_layout(title="Green Spaces Accessibility Index data not available")
        
        return fig_map, fig_histogram, fig_scatter, avg_rating_display
    
    # Add callback to populate Kepler HTML content
    @app.callback(
    [Output('kepler-container', 'children'),
     Output('kepler-container', 'style')],
    [Input('tabs', 'active_tab')]
    )
    def update_kepler(active_tab):
        if active_tab == "tab-index-map":
            container_style = {
                'width': '100%',
                'height': '80vh',
                'position': 'relative',
                'overflow': 'hidden',
                'border': f'1px solid {COLORS["secondary"]}',
                'background': '#f8f9fa',
                'marginBottom': '5px',
                'transition': 'height 0.5s ease-in-out'
            }
            
            kepler_file_path = kepler_path
            if kepler_file_path.exists():
                try:
                    with open(kepler_path, 'r', encoding='utf-8') as f:
                        kepler_html = f.read()
                    
                    # Improved JavaScript with more sophisticated loading and resizing logic
                    kepler_content = html.Div([
                        html.Script("""
                            // Function to properly resize the Kepler map
                            function resizeKepler() {
                                console.log("Resizing Kepler map...");
                                window.dispatchEvent(new Event('resize'));
                                var iframe = document.getElementById('kepler-iframe');
                                if (iframe && iframe.contentWindow) {
                                    iframe.contentWindow.dispatchEvent(new Event('resize'));
                                }
                            }
                            
                            // Set up iframe load event listener
                            document.addEventListener('DOMContentLoaded', function() {
                                var iframe = document.getElementById('kepler-iframe');
                                if (iframe) {
                                    iframe.onload = function() {
                                        console.log("Kepler iframe loaded!");
                                        
                                        // Staged resizing with increasing delays 
                                        // to ensure content has time to initialize
                                        setTimeout(resizeKepler, 1500);
                                        setTimeout(resizeKepler, 3000);
                                        setTimeout(resizeKepler, 3500);
                                        setTimeout(resizeKepler, 4000);
                                    };
                                }
                            });
                            
                            // Initial resize attempts
                            setTimeout(resizeKepler, 1500);
                            setTimeout(resizeKepler, 3500);
                            setTimeout(resizeKepler, 7000);
                        """),
                        html.Iframe(
                            id='kepler-iframe',
                            srcDoc=kepler_html,
                            style={
                                'width': '100%',  
                                'height': '100%', 
                                'border': 'none',
                                'display': 'block',
                                'position': 'absolute',
                                'top': 0,
                                'left': 0,
                                'right': 0,
                                'bottom': 0,
                            }
                        )
                    ], style={
                        'width': '100%',
                        'height': '100%',
                        'position': 'relative',
                        'overflow': 'hidden',
                    })
                    
                    return kepler_content, container_style
                    
                except Exception as e:
                    error_content = html.Div([
                        html.P(f"Error loading Kepler map: {e}"),
                    ], className="alert alert-danger")
                    return error_content, container_style
            else:
                not_found_content = html.Div([
                    html.P("Kepler map HTML file not found."),
                ], className="alert alert-warning")
                return not_found_content, container_style
        else:
            # When not on Kepler tab, return minimal content and smaller size
            container_style = {
                'width': '20%',
                'height': '200px',
                'position': 'relative',
                'overflow': 'hidden',
                'border': f'1px solid {COLORS["secondary"]}',
                'background': '#f8f9fa',
                'marginBottom': '5px',
                'transition': 'height 0.5s ease-in-out'
            }
            placeholder_content = html.Div("Select the Kepler Map tab to view the interactive map.")
            return placeholder_content, container_style

def main():
    data_parent = Path(__file__).parent.parent.parent
    path_tracts = data_parent / "data/grid_and_tracts/processed/merged/merged_tract_data.geojson"
    path_kepler = Path(__file__).parent.parent / "viz/chicago_parks_kepler.html"
    tracts_gdf = load_geojson_data(path_tracts)
    
    path_housing = data_parent / "data/housing_data_index.geojson"
    housing_gdf = load_geojson_data(path_housing)

    print("Dashboard running")
    app = create_dashboard(tracts_gdf, housing_gdf, path_kepler)
    app.run_server(debug=False)

if __name__ == "__main__":
    main()
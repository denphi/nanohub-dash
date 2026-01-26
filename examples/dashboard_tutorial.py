import os
import dash
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# --- 1. Data Setup (Using Built-in Gapminder) ---
df = px.data.gapminder()

# --- 2. Design System (Friendly Colors) ---
theme = {
    'bg_main': '#F0F2F5',       # Lightest Grey/Blue for background
    'bg_card': '#FFFFFF',       # White for cards
    'text_primary': '#2C3E50',  # Dark Blue-Grey for headings
    'text_secondary': '#7F8C8D',# Medium Grey for descriptions
    'accent': '#6C5CE7',        # Soft Purple for highlights
    'success': '#00B894',       # Green for good stats
    'font_family': '"Segoe UI", Roboto, Helvetica, Arial, sans-serif'
}

# Common Styles
CARD_STYLE = {
    'backgroundColor': theme['bg_card'],
    'borderRadius': '12px',
    'padding': '24px',
    'marginBottom': '24px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.05)',
    'border': 'none'
}

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "backgroundColor": theme['bg_card'],
    "boxShadow": "2px 0 5px rgba(0,0,0,0.05)",
    "zIndex": 100
}

CONTENT_STYLE = {
    "marginLeft": "19rem",
    "marginRight": "2rem",
    "padding": "2rem 1rem",
    "backgroundColor": theme['bg_main'],
    "minHeight": "100vh"
}

# --- 3. App Initialization ---
# suppress_callback_exceptions is set to True so we can use dynamic layouts (Multi-Page App)
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    routes_pathname_prefix=os.getenv("DASH_ROUTES_PATHNAME_PREFIX", ""),
    requests_pathname_prefix=os.getenv("DASH_REQUESTS_PATHNAME_PREFIX", ""),
    suppress_callback_exceptions=True
)

# --- 4. Sidebar & Navigation ---
sidebar = html.Div(
    [
        html.H2("Gapminder", style={'color': theme['accent'], 'fontWeight': 'bold'}),
        html.Hr(),
        html.P(
            "A modern dashboard exploring global development metrics over time.",
            style={'color': theme['text_secondary']}
        ),
        html.Br(),
        html.H6("Navigation", style={'textTransform': 'uppercase', 'fontSize': '12px', 'fontWeight': 'bold', 'color': theme['text_secondary']}),
        dbc.Nav(
            [
                dbc.NavLink("Global Overview", href="/", active="exact", style={'fontWeight': '500'}),
                dbc.NavLink("Country Details", href="/country", active="exact"),
                dbc.NavLink("Analytics", href="/analytics", active="exact"),
                dbc.NavLink("Source Code", href="/source", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# --- 5. Helper Components & layouts ---

# Filter for Overview Page
overview_filters = html.Div([
    html.H4("Filters", style={'color': theme['text_primary']}),
    dbc.Row([
        dbc.Col([
            html.Label("Select Year", style={'fontWeight': 'bold', 'color': theme['text_secondary']}),
            dcc.Slider(
                id='year-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                value=df['year'].max(),
                # Use unique years from the dataset for marks
                marks={str(year): str(year) for year in df['year'].unique()},
                step=None,
                tooltip={"placement": "bottom", "always_visible": True}
            ),
        ], width=12),
    ], className="mb-4")
], style=CARD_STYLE)

def draw_kpi(title, value, color):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H6(title, style={'color': theme['text_secondary'], 'textTransform': 'uppercase', 'fontSize': '12px'}),
                    html.H2(value, style={'color': color, 'fontWeight': 'bold'}),
                ]
            )
        ],
        style={**CARD_STYLE, 'textAlign': 'center', 'marginBottom': '0'} 
    )

# LAYOUT 1: Global Overview
def serve_overview():
    return html.Div([
        html.H1("Global Prosperity Dashboard", style={'color': theme['text_primary'], 'marginBottom': '10px'}),
        html.P("Analyzing Life Expectancy, GDP, and Population.", style={'color': theme['text_secondary'], 'marginBottom': '30px'}),
        
        overview_filters,

        dbc.Row(id='kpi-row', className="mb-4"),

        dbc.Row([
            dbc.Col(html.Div([
                    html.H4("Life Expectancy vs GDP", style={'color': theme['text_primary']}),
                    dcc.Graph(id='scatter-graph')
                ], style=CARD_STYLE), width=8),
            dbc.Col(html.Div([
                    html.H4("Top Continents by Pop", style={'color': theme['text_primary']}),
                    dcc.Graph(id='bar-graph')
                ], style=CARD_STYLE), width=4),
        ]),
        
        html.Div([
            html.H4("Recent Data", style={'color': theme['text_primary']}),
            html.Div(id='table-container')
        ], style=CARD_STYLE)
    ])

# LAYOUT 2: Country Details (Placeholder)
def serve_country_details():
    return html.Div([
        html.H1("Country Details", style={'color': theme['text_primary']}),
        html.Div([
            html.P("Select a country to view detailed trends.", style={'color': theme['text_secondary']}),
            dcc.Dropdown(
                id='country-select',
                options=[{'label': c, 'value': c} for c in df['country'].unique()],
                value='United States'
            ),
            dcc.Graph(id='country-graph')
        ], style=CARD_STYLE)
    ])

# LAYOUT 3: Analytics
def serve_analytics():
    return html.Div([
        html.H1("Advanced Analytics", style={'color': theme['text_primary']}),
        html.P("Correlation analysis and predictive modeling.", style={'color': theme['text_secondary'], 'marginBottom': '30px'}),
        
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.H4("Correlation Heatmap", style={'color': theme['text_primary']}),
                    dcc.Graph(id='corr-graph')
                ], style=CARD_STYLE), width=6
            ),
            dbc.Col(
                html.Div([
                    html.H4("GDP vs Life Expectancy Model", style={'color': theme['text_primary']}),
                    html.Label("Filter by Continent:", style={'fontWeight': 'bold', 'color': theme['text_secondary']}),
                    dcc.Dropdown(
                        id='analytics-continent',
                        options=[{'label': 'All Continents', 'value': 'All'}] + [{'label': c, 'value': c} for c in df['continent'].unique()],
                        value='All',
                        clearable=False
                    ),
                    dcc.Graph(id='reg-graph')
                ], style=CARD_STYLE), width=6
            )
        ])
    ])


# LAYOUT 4: Source Code
def serve_source_code():
    try:
        with open(__file__, 'r') as f:
            source_code = f.read()
    except Exception as e:
        source_code = f"Error reading source code: {str(e)}"
    
    return html.Div([
        html.H1("Application Source Code", style={'color': theme['text_primary']}),
        html.P("Below is the complete source code of this Dash application.", style={'color': theme['text_secondary'], 'marginBottom': '30px'}),
        
        html.Div([
            html.Pre(
                source_code,
                style={
                    'backgroundColor': '#F5F5F5',
                    'border': '1px solid #E0E0E0',
                    'borderRadius': '8px',
                    'padding': '20px',
                    'overflow': 'auto',
                    'fontFamily': '"Courier New", monospace',
                    'fontSize': '12px',
                    'color': '#333',
                    'lineHeight': '1.5'
                }
            )
        ], style=CARD_STYLE)
    ])


# --- 6. Main Layout Structure ---
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    html.Div(id="page-content", style=CONTENT_STYLE)
], style={'backgroundColor': theme['bg_main'], 'fontFamily': theme['font_family']})


# --- 7. Callbacks ---

# Routing Callback
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/" or pathname == "/overview":
        return serve_overview()
    elif pathname == "/country":
        return serve_country_details()
    elif pathname == "/analytics":
        return serve_analytics()
    elif pathname == "/source":
        return serve_source_code()
    # Default
    return serve_overview()

# Overview Page Callbacks
@app.callback(
    [Output('kpi-row', 'children'),
     Output('scatter-graph', 'figure'),
     Output('bar-graph', 'figure'),
     Output('table-container', 'children')],
    [Input('year-slider', 'value')]
)
def update_overview(selected_year):
    dff = df[df.year == selected_year]
    
    # KPIs
    avg_life = f"{dff['lifeExp'].mean():.1f} yrs"
    gdp_med = f"${dff['gdpPercap'].median():,.0f}"
    total_pop = f"{dff['pop'].sum() / 1e9:.2f} B"
    
    kpi_cards = [
        dbc.Col(draw_kpi("Avg Life Expectancy", avg_life, theme['success']), width=4),
        dbc.Col(draw_kpi("Median GDP", gdp_med, theme['accent']), width=4),
        dbc.Col(draw_kpi("Global Population", total_pop, theme['text_primary']), width=4),
    ]

    # Scatter
    fig_scatter = px.scatter(
        dff, x="gdpPercap", y="lifeExp", size="pop", color="continent", hover_name="country",
        log_x=True, size_max=60, title="",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_scatter.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_family=theme['font_family'], margin=dict(l=20, r=20, t=20, b=20)
    )

    # Bar
    cont_counts = dff.groupby("continent")['pop'].sum().reset_index()
    fig_bar = px.bar(
        cont_counts, x="continent", y="pop", 
        color="continent", color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_family=theme['font_family'], showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    # Table
    table = dash_table.DataTable(
        data=dff.head(10).to_dict('records'),
        columns=[{"name": i, "id": i} for i in ['country', 'continent', 'lifeExp', 'gdpPercap']],
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': theme['bg_main'], 'fontWeight': 'bold', 'border': 'none'},
        style_cell={'backgroundColor': 'white', 'border': '1px solid #f0f0f0', 'padding': '10px'}
    )
    return kpi_cards, fig_scatter, fig_bar, table

# Country Page Callbacks
@app.callback(
    Output('country-graph', 'figure'),
    [Input('country-select', 'value')]
)
def update_country_view(country):
    if not country:
        return px.line(title="Select a country")
    
    dff = df[df.country == country]
    fig = px.line(dff, x='year', y='gdpPercap', title=f"GDP per Capita: {country}", markers=True)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_family=theme['font_family']
    )
    return fig

# Analytics Page Callbacks
@app.callback(
    [Output('corr-graph', 'figure'),
     Output('reg-graph', 'figure')],
    [Input('analytics-continent', 'value')]
)
def update_analytics(continent):
    # Filter Data
    dff = df if continent == 'All' else df[df.continent == continent]
    
    if len(dff) == 0:
         return px.imshow(np.zeros((1,1)), title="No Data"), px.scatter(title="No Data")

    # 1. Correlation Heatmap (Numeric only)
    numeric_df = dff.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    
    fig_corr = px.imshow(corr, color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
    fig_corr.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_family=theme['font_family']
    )
    
    # 2. Regression (GDP -> LifeExp)
    try:
        # Drop NaNs and zeros/negative values for log
        reg_df = dff[['gdpPercap', 'lifeExp']].dropna()
        reg_df = reg_df[reg_df['gdpPercap'] > 0]
        
        if len(reg_df) < 5:
            raise ValueError("Not enough data points")

        X = np.log(reg_df[['gdpPercap']]) # Log transform GDP for better fit
        y = reg_df['lifeExp']
        
        model = LinearRegression()
        model.fit(X, y)
        r2 = model.score(X, y)
        
        # Create Trendline
        x_range = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        y_pred = model.predict(x_range)
        
        # Plot Scatter
        fig_reg = px.scatter(
            dff, x="gdpPercap", y="lifeExp", color="country", opacity=0.6,
            log_x=True, 
            title=f"R² Score: {r2:.3f} (Log-Linear Model)"
        )
        
        # Add Trendline
        real_x = np.exp(x_range)
        fig_reg.add_trace(
            go.Scatter(x=real_x.flatten(), y=y_pred, mode='lines', name='Trend', line=dict(color='red', width=3))
        )
    except Exception:
         fig_reg = px.scatter(title="Insufficient data for regression")
    
    fig_reg.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_family=theme['font_family'], showlegend=False
    )
    
    return fig_corr, fig_reg


if __name__ == "__main__":
    app.run(
        jupyter_server_url=os.environ.get("DASH_BASE_PROXY", ""),
        host=os.environ.get("DASH_HOST", "0.0.0.0"),
        port=os.environ.get("DASH_PORT", "8001"),
    )

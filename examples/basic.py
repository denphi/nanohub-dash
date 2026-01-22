from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import os

# Simple sample data
df = pd.DataFrame({
    "x": list(range(1, 11)),
    "y": [1, 4, 2, 8, 5, 7, 6, 9, 10, 3],
    "group": ["A"] * 5 + ["B"] * 5
})

app = Dash(__name__,
    routes_pathname_prefix=os.getenv("DASH_ROUTES_PATHNAME_PREFIX"),
    requests_pathname_prefix=os.getenv("DASH_REQUESTS_PATHNAME_PREFIX")
)

app.layout = html.Div(
    style={"maxWidth": "900px", "margin": "40px auto", "fontFamily": "Arial"},
    children=[
        html.H2("Basic Dash App"),
        html.P("Pick a group to filter the chart:"),

        dcc.Dropdown(
            id="group",
            options=[{"label": g, "value": g} for g in sorted(df["group"].unique())]
                    + [{"label": "All", "value": "ALL"}],
            value="ALL",
            clearable=False,
            style={"width": "250px"},
        ),

        dcc.Graph(id="plot"),
        html.Div(id="stats", style={"marginTop": "10px"})
    ],
)


@app.callback(
    Output("plot", "figure"),
    Output("stats", "children"),
    Input("group", "value"),
)
def update(group):
    dff = df if group == "ALL" else df[df["group"] == group]
    fig = px.line(dff, x="x", y="y", markers=True, title=f"y vs x ({group})")
    stats = f"Rows: {len(dff)} | y min: {dff['y'].min()} | y max: {dff['y'].max()}"
    return fig, stats

app.run(
    debug = True,
    jupyter_mode = "inline",
    jupyter_server_url = os.getenv("DASH_BASE_PROXY"),
    port = os.getenv("DASH_PORT"),
    host = os.getenv("DASH_HOST"),
)


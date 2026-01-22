Advanced Example
================

This example demonstrates a more complex Dash application with interactive callbacks,
multiple components, and file uploads running on nanoHUB.

Interactive Data Explorer
-------------------------

This example creates an interactive data exploration dashboard with:

- File upload capability
- Dynamic graph selection
- Interactive filtering
- Data table display

**Cell 1: Load the extension and configure environment**

.. code-block:: python

   %load_ext nanohubdash
   %set_dash_env --port 8001

**Cell 2: Create the advanced Dash app**

.. code-block:: python

   import os
   import base64
   import io

   from dash import Dash, html, dcc, dash_table, callback, Input, Output, State
   import plotly.express as px
   import pandas as pd
   import numpy as np

   # Create the Dash app
   app = Dash(__name__,
      routes_pathname_prefix=os.getenv("DASH_ROUTES_PATHNAME_PREFIX"),
      requests_pathname_prefix=os.getenv("DASH_REQUESTS_PATHNAME_PREFIX"),
      suppress_callback_exceptions=True
   )

   # Sample dataset
   np.random.seed(42)
   sample_df = pd.DataFrame({
       'x': np.random.randn(100),
       'y': np.random.randn(100),
       'category': np.random.choice(['A', 'B', 'C'], 100),
       'size': np.random.randint(10, 100, 100)
   })

   app.layout = html.Div([
       html.H1("Interactive Data Explorer", style={'textAlign': 'center'}),
       html.Hr(),

       # Tabs for different sections
       dcc.Tabs([
           # Tab 1: Upload and visualize data
           dcc.Tab(label='Data Upload', children=[
               html.Div([
                   html.H3("Upload Your Data"),
                   dcc.Upload(
                       id='upload-data',
                       children=html.Div([
                           'Drag and Drop or ',
                           html.A('Select a CSV File')
                       ]),
                       style={
                           'width': '100%',
                           'height': '60px',
                           'lineHeight': '60px',
                           'borderWidth': '1px',
                           'borderStyle': 'dashed',
                           'borderRadius': '5px',
                           'textAlign': 'center',
                           'margin': '10px'
                       },
                       multiple=False
                   ),
                   html.Div(id='upload-status'),
                   html.Hr(),
                   html.H3("Or Use Sample Data"),
                   html.Button("Load Sample Data", id='load-sample', n_clicks=0),
               ], style={'padding': '20px'})
           ]),

           # Tab 2: Visualization
           dcc.Tab(label='Visualization', children=[
               html.Div([
                   html.Div([
                       html.Label("Select Chart Type:"),
                       dcc.Dropdown(
                           id='chart-type',
                           options=[
                               {'label': 'Scatter Plot', 'value': 'scatter'},
                               {'label': 'Histogram', 'value': 'histogram'},
                               {'label': 'Box Plot', 'value': 'box'},
                               {'label': 'Violin Plot', 'value': 'violin'}
                           ],
                           value='scatter'
                       ),
                   ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

                   html.Div([
                       html.Label("X-Axis Column:"),
                       dcc.Dropdown(id='x-column'),
                   ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

                   html.Div([
                       html.Label("Y-Axis Column:"),
                       dcc.Dropdown(id='y-column'),
                   ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
               ]),

               dcc.Graph(id='main-graph'),
           ]),

           # Tab 3: Data Table
           dcc.Tab(label='Data Table', children=[
               html.Div([
                   html.H3("Data Preview"),
                   html.Div(id='data-table-container')
               ], style={'padding': '20px'})
           ]),

           # Tab 4: Statistics
           dcc.Tab(label='Statistics', children=[
               html.Div([
                   html.H3("Descriptive Statistics"),
                   html.Div(id='stats-container')
               ], style={'padding': '20px'})
           ])
       ]),

       # Store for the dataframe
       dcc.Store(id='stored-data')
   ])


   def parse_contents(contents, filename):
       """Parse uploaded file contents."""
       content_type, content_string = contents.split(',')
       decoded = base64.b64decode(content_string)
       try:
           if 'csv' in filename:
               df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
           elif 'xls' in filename:
               df = pd.read_excel(io.BytesIO(decoded))
           else:
               return None
           return df
       except Exception as e:
           print(e)
           return None


   @callback(
       Output('stored-data', 'data'),
       Output('upload-status', 'children'),
       Input('upload-data', 'contents'),
       Input('load-sample', 'n_clicks'),
       State('upload-data', 'filename'),
       prevent_initial_call=True
   )
   def update_data(contents, n_clicks, filename):
       from dash import ctx
       triggered = ctx.triggered_id

       if triggered == 'load-sample':
           return sample_df.to_json(date_format='iso', orient='split'), \
                  html.Div("Sample data loaded!", style={'color': 'green'})

       if contents is not None:
           df = parse_contents(contents, filename)
           if df is not None:
               return df.to_json(date_format='iso', orient='split'), \
                      html.Div(f"File '{filename}' uploaded successfully!", style={'color': 'green'})
           return None, html.Div("Error parsing file.", style={'color': 'red'})

       return None, ""


   @callback(
       Output('x-column', 'options'),
       Output('y-column', 'options'),
       Output('x-column', 'value'),
       Output('y-column', 'value'),
       Input('stored-data', 'data')
   )
   def update_column_options(data):
       if data is None:
           return [], [], None, None
       df = pd.read_json(io.StringIO(data), orient='split')
       numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
       options = [{'label': col, 'value': col} for col in numeric_cols]
       x_val = numeric_cols[0] if numeric_cols else None
       y_val = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0] if numeric_cols else None
       return options, options, x_val, y_val


   @callback(
       Output('main-graph', 'figure'),
       Input('chart-type', 'value'),
       Input('x-column', 'value'),
       Input('y-column', 'value'),
       Input('stored-data', 'data')
   )
   def update_graph(chart_type, x_col, y_col, data):
       if data is None or x_col is None:
           return px.scatter(title="Load data to visualize")

       df = pd.read_json(io.StringIO(data), orient='split')

       if chart_type == 'scatter':
           fig = px.scatter(df, x=x_col, y=y_col, title=f'{x_col} vs {y_col}')
       elif chart_type == 'histogram':
           fig = px.histogram(df, x=x_col, title=f'Distribution of {x_col}')
       elif chart_type == 'box':
           fig = px.box(df, y=y_col, title=f'Box Plot of {y_col}')
       elif chart_type == 'violin':
           fig = px.violin(df, y=y_col, title=f'Violin Plot of {y_col}')
       else:
           fig = px.scatter(df, x=x_col, y=y_col)

       return fig


   @callback(
       Output('data-table-container', 'children'),
       Input('stored-data', 'data')
   )
   def update_table(data):
       if data is None:
           return html.P("No data loaded. Please upload a file or load sample data.")

       df = pd.read_json(io.StringIO(data), orient='split')
       return dash_table.DataTable(
           data=df.head(100).to_dict('records'),
           columns=[{'name': i, 'id': i} for i in df.columns],
           page_size=20,
           style_table={'overflowX': 'auto'},
           style_cell={'textAlign': 'left'},
           style_header={'backgroundColor': 'paleturquoise', 'fontWeight': 'bold'}
       )


   @callback(
       Output('stats-container', 'children'),
       Input('stored-data', 'data')
   )
   def update_stats(data):
       if data is None:
           return html.P("No data loaded. Please upload a file or load sample data.")

       df = pd.read_json(io.StringIO(data), orient='split')
       stats = df.describe().round(3)

       return dash_table.DataTable(
           data=stats.reset_index().to_dict('records'),
           columns=[{'name': 'Statistic', 'id': 'index'}] + \
                   [{'name': i, 'id': i} for i in stats.columns],
           style_table={'overflowX': 'auto'},
           style_cell={'textAlign': 'right'},
           style_header={'backgroundColor': 'lightblue', 'fontWeight': 'bold'}
       )


   if __name__ == "__main__":
       app.run(
           jupyter_server_url=os.environ.get("DASH_BASE_PROXY"),
           host=os.environ.get("DASH_HOST", "0.0.0.0"),
           port=os.environ.get("DASH_PORT", "8001"),
           debug=False,
       )

Key Features Demonstrated
-------------------------

1. **Multiple Tabs**: Organized interface with tabs for different functionality
2. **File Upload**: Support for uploading CSV files
3. **Dynamic Dropdowns**: Column selectors that update based on loaded data
4. **Multiple Chart Types**: Switch between scatter, histogram, box, and violin plots
5. **Data Tables**: Interactive data table with pagination
6. **Statistics View**: Automatic descriptive statistics calculation
7. **State Management**: Using ``dcc.Store`` to share data between callbacks

Using Environment Variables
---------------------------

You can access the configured environment variables in your advanced app:

.. code-block:: python

   import os

   # Get the base proxy URL for constructing external links
   base_proxy = os.environ.get("DASH_BASE_PROXY", "")

   # Get the configured port
   port = os.environ.get("DASH_PORT", "8001")

   # Example: Create a shareable link
   requests_prefix = os.environ.get("DASH_REQUESTS_PATHNAME_PREFIX", "/")
   full_url = f"{base_proxy}{requests_prefix}"
   print(f"Your app is available at: {full_url}")

Running with start_dash
-----------------------

Save the advanced app to a file called ``advanced_app.py`` and run:

.. code-block:: bash

   start_dash --app advanced_app.py --debug True

The ``--debug True`` flag enables:

- Hot reloading when you modify the code
- Detailed error messages in the browser
- Stream logging from wrwroxy

Tips for Advanced Applications
------------------------------

1. **Use suppress_callback_exceptions**: Set ``suppress_callback_exceptions=True`` when using dynamic layouts
2. **Handle missing data gracefully**: Always check if data exists before processing
3. **Use dcc.Store for shared state**: Store data that needs to be accessed by multiple callbacks
4. **Optimize large datasets**: Use pagination in data tables and limit displayed data
5. **Add loading states**: Use ``dcc.Loading`` components for better user experience

Basic Example
=============

This example demonstrates a simple Dash application running on nanoHUB.

Jupyter Notebook Approach
-------------------------

Create a new Jupyter notebook on nanoHUB and add the following cells:

**Cell 1: Load the extension and configure environment**

.. code-block:: python

   %load_ext nanohubdash
   %set_dash_env

**Cell 2: Create and run the Dash app**

.. code-block:: python

   import os
   from dash import Dash, html, dcc
   import plotly.express as px
   import pandas as pd

   # Create sample data
   df = pd.DataFrame({
       "Fruit": ["Apples", "Oranges", "Bananas", "Grapes", "Strawberries"],
       "Amount": [4, 2, 5, 3, 6],
       "City": ["NYC", "LA", "Chicago", "Houston", "Phoenix"]
   })

   # Create the Dash app
   app = Dash(__name__)

   # Create a bar chart
   fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

   app.layout = html.Div([
       html.H1("Fruit Sales Dashboard", style={'textAlign': 'center'}),
       html.Hr(),
       dcc.Graph(
           id='fruit-chart',
           figure=fig
       ),
       html.Div([
           html.P("This is a simple Dash app running on nanoHUB!"),
           html.P("The environment has been configured automatically.")
       ], style={'textAlign': 'center', 'marginTop': '20px'})
   ])

   if __name__ == "__main__":
       app.run(
           host=os.environ.get("DASH_HOST", "0.0.0.0"),
           port=os.environ.get("DASH_PORT", "8001"),
           debug=False
       )

Understanding the Code
----------------------

1. **Loading the extension**: ``%load_ext nanohubdash`` registers the magic command
2. **Setting the environment**: ``%set_dash_env`` configures all necessary environment variables
3. **Creating the app**: Standard Dash application code
4. **Running the server**: ``app.run()`` starts the development server

The magic command automatically detects your nanoHUB session and configures:

- The correct URL prefixes for the weber proxy
- The host and port settings
- The base proxy URL for external access

Standalone Python File Approach
-------------------------------

You can also create a standalone Python file and use the ``start_dash`` command.

**app.py**

.. code-block:: python

   import os
   from dash import Dash, html, dcc
   import plotly.express as px
   import pandas as pd

   # Create sample data
   df = pd.DataFrame({
       "Fruit": ["Apples", "Oranges", "Bananas", "Grapes", "Strawberries"],
       "Amount": [4, 2, 5, 3, 6],
       "City": ["NYC", "LA", "Chicago", "Houston", "Phoenix"]
   })

   # Create the Dash app
   app = Dash(__name__)

   # Create a bar chart
   fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

   app.layout = html.Div([
       html.H1("Fruit Sales Dashboard", style={'textAlign': 'center'}),
       html.Hr(),
       dcc.Graph(
           id='fruit-chart',
           figure=fig
       )
   ])

   if __name__ == "__main__":
       app.run(
           host=os.environ.get("DASH_HOST", "0.0.0.0"),
           port=os.environ.get("DASH_PORT", "8001"),
       )

Then run from the terminal:

.. code-block:: bash

   start_dash --app app.py

This approach:

- Automatically configures the environment
- Launches the wrwroxy reverse proxy
- Injects a header bar with nanoHUB branding
- Provides a "Submit a ticket" link for support
- Includes a "Terminate Session" button

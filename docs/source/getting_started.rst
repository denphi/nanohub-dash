Getting Started
===============

This guide will help you get started with running Dash applications on nanoHUB.

Understanding the nanoHUB Environment
-------------------------------------

When running applications on nanoHUB, your app runs behind a reverse proxy (weber proxy)
that handles authentication and routing. This means your Dash application needs to be
configured with the correct URL prefixes to work properly.

The **nanohub-dash** package handles this configuration automatically by:

1. Reading the session information from environment variables
2. Parsing the nanoHUB resources file to get proxy configuration
3. Setting the appropriate environment variables for Dash

Using the Jupyter Magic Command
-------------------------------

The easiest way to configure your Dash app is using the ``%set_dash_env`` magic command
in a Jupyter notebook.

Loading the Extension
^^^^^^^^^^^^^^^^^^^^^

First, load the nanohubdash extension:

.. code-block:: python

   %load_ext nanohubdash

Setting the Environment
^^^^^^^^^^^^^^^^^^^^^^^

Then run the magic command to configure the environment:

.. code-block:: python

   %set_dash_env

This sets the following environment variables:

- ``DASH_REQUESTS_PATHNAME_PREFIX``: The weber proxy path for requests
- ``DASH_ROUTES_PATHNAME_PREFIX``: Set to ``/``
- ``DASH_HOST``: The host address for the Dash server (default: ``0.0.0.0``)
- ``DASH_PORT``: The port number for the Dash server (default: ``8001``)
- ``DASH_BASE_PROXY``: Base proxy URL (e.g., ``https://proxy.nanohub.org``)

Custom Port and Host
^^^^^^^^^^^^^^^^^^^^

You can specify a custom port and host:

.. code-block:: python

   %set_dash_env --port 8050 --host 127.0.0.1

Using the Command-Line Tool
---------------------------

For more advanced use cases, you can use the ``start_dash`` command-line tool.
This tool not only configures the environment but also:

- Launches the wrwroxy reverse proxy
- Injects a header bar with logo, support link, and session termination button
- Handles graceful shutdown on signals

Basic Usage
^^^^^^^^^^^

.. code-block:: bash

   start_dash --app myapp.py

With Debug Mode
^^^^^^^^^^^^^^^

.. code-block:: bash

   start_dash --app myapp.py --debug True

Custom Logo
^^^^^^^^^^^

.. code-block:: bash

   start_dash --app myapp.py --logo https://example.com/my-logo.png

Command-Line Options
^^^^^^^^^^^^^^^^^^^^

- ``--app``: (Required) Path to your Dash application Python file
- ``--debug``: Enable debug mode (True/False, default: False)
- ``--logo``: URL for the logo displayed in the header bar

Creating Your Dash Application
------------------------------

Your Dash application file must define an ``app`` variable that is a Dash instance:

.. code-block:: python

   from dash import Dash, html, dcc

   app = Dash(__name__)

   app.layout = html.Div([
       html.H1("My nanoHUB Dash App"),
       dcc.Graph(id='my-graph')
   ])

   if __name__ == "__main__":
       app.run_server()

Using Environment Variables in Your App
---------------------------------------

You can access the configured environment variables in your app:

.. code-block:: python

   import os
   from dash import Dash, html

   app = Dash(__name__)

   # Access environment variables
   base_proxy = os.environ.get("DASH_BASE_PROXY", "")
   port = os.environ.get("DASH_PORT", "8001")

   app.layout = html.Div([
       html.H1("Configuration"),
       html.P(f"Proxy: {base_proxy}"),
       html.P(f"Port: {port}")
   ])

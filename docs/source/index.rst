nanohub-dash Documentation
==========================

**nanohub-dash** is a Python package for running Dash applications on the nanoHUB platform.
It provides tools to configure the environment variables and proxy settings needed to deploy
Dash apps behind the nanoHUB weber proxy.

Features
--------

- **Jupyter Magic Command** (``%set_dash_env``): Configure environment variables for Dash apps directly in Jupyter notebooks
- **Command-line Tool** (``start_dash``): Launch Dash applications with automatic proxy configuration and header injection

Quick Start
-----------

Install the package:

.. code-block:: bash

   pip install nanohub-dash

In a Jupyter notebook on nanoHUB:

.. code-block:: python

   %load_ext nanohubdash
   %set_dash_env

   import os
   from dash import Dash, html

   app = Dash(__name__,
       routes_pathname_prefix=os.getenv("DASH_ROUTES_PATHNAME_PREFIX"),
       requests_pathname_prefix=os.getenv("DASH_REQUESTS_PATHNAME_PREFIX")
   )
   app.layout = html.Div("Hello nanoHUB!")

   if __name__ == "__main__":
       app.run(
           jupyter_server_url=os.environ.get("DASH_BASE_PROXY"),
           host=os.environ.get("DASH_HOST", "0.0.0.0"),
           port=os.environ.get("DASH_PORT", "8001"),
       )

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   getting_started
   examples/index
   api_reference

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

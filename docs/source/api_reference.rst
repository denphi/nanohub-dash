API Reference
=============

This section provides detailed API documentation for the nanohub-dash package.

Jupyter Magic Command
---------------------

.. py:function:: %set_dash_env [--port PORT] [--host HOST]

   Configure environment variables for running Dash on nanoHUB.

   :param port: Dash port (default: 8001)
   :type port: int
   :param host: Dash bind host (default: 0.0.0.0)
   :type host: str

   **Environment Variables Set:**

   - ``DASH_REQUESTS_PATHNAME_PREFIX``: Weber proxy path for requests (e.g., ``/weber/123/abc/456/proxy/8001/``)
   - ``DASH_ROUTES_PATHNAME_PREFIX``: Set to ``/``
   - ``DASH_HOST``: The host address for the Dash server
   - ``DASH_PORT``: The port number for the Dash server
   - ``DASH_BASE_PROXY``: Base proxy URL (e.g., ``https://proxy.nanohub.org``)

   **Example:**

   .. code-block:: python

      %load_ext nanohubdash
      %set_dash_env --port 8050 --host 0.0.0.0

Command-Line Tool
-----------------

start_dash
^^^^^^^^^^

Launch a Dash application with automatic proxy configuration and header injection.

**Usage:**

.. code-block:: bash

   start_dash --app APP_PATH [--debug DEBUG] [--logo LOGO_URL]

**Arguments:**

.. option:: --app APP_PATH

   Required. Path to the Dash application Python file.
   The file must define ``app = dash.Dash(...)``.

.. option:: --debug DEBUG

   Optional. Enable debug mode (True/False). Default: False.
   When enabled:

   - Hot reloading is active
   - Detailed error messages are shown
   - wrwroxy stream logging is enabled

.. option:: --logo LOGO_URL

   Optional. URL for the logo displayed in the header bar.
   Default: nanoHUB logo

**Example:**

.. code-block:: bash

   start_dash --app myapp.py --debug True --logo https://example.com/logo.png

**Header Injection:**

When using ``start_dash``, a header bar is automatically injected into your Dash app with:

- Logo image (customizable via ``--logo``)
- "Submit a ticket" link for support
- "Terminate Session" button

Python API
----------

nanohubdash module
^^^^^^^^^^^^^^^^^^

.. py:module:: nanohubdash

.. py:data:: __version__

   The current version of the nanohub-dash package.

.. py:function:: load_ipython_extension(ipython)

   Register the SetDashEnvMagic with IPython.

   This function is called automatically when the extension is loaded
   via ``%load_ext nanohubdash``.

   :param ipython: The IPython shell instance.

.. py:class:: SetDashEnvMagic

   IPython magic class for setting up Dash environment on nanoHUB.

   Provides the ``%set_dash_env`` line magic that configures environment
   variables needed for Dash applications running behind the nanoHUB
   weber proxy.

Environment Variables Reference
-------------------------------

The following environment variables are used or set by nanohub-dash:

**Input Variables (read from environment):**

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Variable
     - Description
   * - ``SESSION`` or ``SESSION_ID``
     - nanoHUB session identifier
   * - ``SESSIONDIR`` or ``SESSION_DIR``
     - Path to session directory containing resources file

**Output Variables (set by nanohub-dash):**

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Variable
     - Description
   * - ``DASH_REQUESTS_PATHNAME_PREFIX``
     - Full weber proxy path for Dash requests
   * - ``DASH_ROUTES_PATHNAME_PREFIX``
     - Always set to ``/``
   * - ``DASH_HOST``
     - Host address for Dash server
   * - ``DASH_PORT``
     - Port number for Dash server
   * - ``DASH_BASE_PROXY``
     - Base proxy URL (e.g., ``https://proxy.nanohub.org``)

**Additional Variables (set by start_dash):**

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Variable
     - Description
   * - ``HOST``
     - Host for the Dash server (used internally)
   * - ``PORT``
     - Port for the Dash server (used internally)
   * - ``DASH_DEBUG``
     - Debug mode flag
   * - ``APP_NAME``
     - Detected application name

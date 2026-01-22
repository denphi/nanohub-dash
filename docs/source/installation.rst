Installation
============

Requirements
------------

- Python >= 3.8
- IPython >= 7.0
- Must be running on a nanoHUB environment with ``SESSION`` and ``SESSIONDIR`` environment variables set

Installing from PyPI
--------------------

The recommended way to install nanohub-dash is via pip:

.. code-block:: bash

   pip install nanohub-dash

Installing from Source
----------------------

You can also install directly from the GitHub repository:

.. code-block:: bash

   pip install git+https://github.com/denphi/nanohub-dash.git

For development, clone the repository and install in editable mode:

.. code-block:: bash

   git clone https://github.com/denphi/nanohub-dash.git
   cd nanohub-dash
   pip install -e .

Verifying Installation
----------------------

After installation, you can verify that the package is installed correctly:

.. code-block:: python

   import nanohubdash
   print(nanohubdash.__version__)

Or check that the command-line tool is available:

.. code-block:: bash

   start_dash --help

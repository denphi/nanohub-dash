#  Copyright 2026 HUBzero Foundation, LLC.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

#  HUBzero is a registered trademark of Purdue University.

#  Authors:
#  Daniel Mejia (denphi), Purdue University (denphi@denphi.com)

"""
nanohubdash - Tools for running Dash applications on nanoHUB.

This package provides two main features:

1. Jupyter Magic Command (%set_dash_env):
   Configure environment variables for Dash apps in Jupyter notebooks.

   Usage:
       %load_ext nanohubdash
       %set_dash_env --port 8001 --host 0.0.0.0

   This sets:
       - DASH_REQUESTS_PATHNAME_PREFIX
       - DASH_ROUTES_PATHNAME_PREFIX
       - DASH_HOST
       - DASH_PORT
       - DASH_BASE_PROXY

2. Command-line Tool (start_dash):
   Launch Dash applications with automatic proxy configuration and header injection.

   Usage:
       start_dash --app myapp.py [--debug True] [--logo URL]

   This:
       - Configures the weber proxy paths
       - Injects a header bar with logo, support link, and terminate button
       - Starts the wrwroxy reverse proxy
       - Launches the Dash application

Requirements:
    - Must be running on a nanoHUB environment
    - SESSION and SESSIONDIR environment variables must be set
"""

from .dash_env import SetDashEnvMagic, load_ipython_extension
from ._version import __version__

__all__ = ["SetDashEnvMagic", "load_ipython_extension", "__version__"]

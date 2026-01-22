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
dash_env - IPython magic commands for configuring Dash environment on nanoHUB.

This module provides the %set_dash_env magic command that configures
environment variables needed to run Dash applications behind the
nanoHUB weber proxy.

Usage in Jupyter:
    %load_ext nanohubdash
    %set_dash_env --port 8001 --host 0.0.0.0
"""

import os
from IPython.core.magic import magics_class, Magics, line_magic
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring


def _normalize(p: str) -> str:
    """
    Normalize a URL path to ensure it starts and ends with '/'.

    Args:
        p: Path string to normalize.

    Returns:
        Normalized path with leading and trailing slashes.
    """
    if not p.startswith("/"):
        p = "/" + p
    if not p.endswith("/"):
        p += "/"
    return p


def _get_session():
    """
    Retrieve session information from environment variables.

    Returns:
        tuple: (session_id, session_directory)

    Raises:
        RuntimeError: If SESSION/SESSIONDIR environment variables are not set.
    """
    session = os.getenv("SESSION") or os.getenv("SESSION_ID")
    sessiondir = os.getenv("SESSIONDIR") or os.getenv("SESSION_DIR")
    if not session or not sessiondir:
        raise RuntimeError("SESSION / SESSIONDIR not set")
    return session, sessiondir


def _get_requests_prefix_and_url(dash_port: int):
    """
    Parse nanoHUB resources file and construct proxy URL information.

    Reads the session's resources file to extract hub_url, filexfer_port,
    and filexfer_cookie, then constructs the appropriate weber proxy paths.

    Args:
        dash_port: The port number where Dash will be running.

    Returns:
        tuple: (requests_prefix, browser_url, proxy_url)
            - requests_prefix: Path for DASH_REQUESTS_PATHNAME_PREFIX
            - browser_url: Full URL to access the Dash app in browser
            - proxy_url: Base proxy URL (https://proxy.<hub_host>)

    Raises:
        RuntimeError: If required fields cannot be parsed from resources file.
    """
    session, sessiondir = _get_session()
    fn = os.path.join(sessiondir, "resources")

    url = fxp = fxc = None
    with open(fn) as f:
        for line in f:
            if line.startswith("hub_url"):
                url = line.split()[1]
            elif line.startswith("filexfer_port"):
                fxp = str(int(line.split()[1]) % 1000)
            elif line.startswith("filexfer_cookie"):
                fxc = line.split()[1]

    if not (url and fxp and fxc):
        raise RuntimeError("Could not parse hub_url/filexfer_port/filexfer_cookie from resources")

    weber = f"/weber/{session}/{fxc}/{fxp}/"
    proxy_seg = f"proxy/{dash_port}/"  # appended AFTER weber path

    requests_prefix = _normalize(weber + proxy_seg)
    proxy_url = "https://proxy." + url.split("//", 1)[1]
    browser_url = proxy_url + requests_prefix
    return requests_prefix, browser_url, proxy_url


@magics_class
class SetDashEnvMagic(Magics):
    """
    IPython magic class for setting up Dash environment on nanoHUB.

    Provides the %set_dash_env line magic that configures environment
    variables needed for Dash applications running behind the nanoHUB
    weber proxy.
    """

    @magic_arguments()
    @argument("--port", type=int, default=8001, help="Dash port (default 8001)")
    @argument("--host", type=str, default="0.0.0.0", help="Dash bind host (default 0.0.0.0)")
    @line_magic
    def set_dash_env(self, line):
        """
        Configure environment variables for running Dash on nanoHUB.

        Usage:
            %set_dash_env [--port 8001] [--host 0.0.0.0]

        This magic command sets the following environment variables:
            - DASH_REQUESTS_PATHNAME_PREFIX: Weber proxy path for requests
            - DASH_ROUTES_PATHNAME_PREFIX: Set to '/'
            - DASH_HOST: The host address for the Dash server
            - DASH_PORT: The port number for the Dash server
            - DASH_PROXY: Base proxy URL (https://proxy.<hub_host>)

        After execution, prints the browser URL where the Dash app
        will be accessible.

        Args:
            line: Command line arguments string.
        """
        args = parse_argstring(self.set_dash_env, line)

        req_prefix, browser_url, proxy_url = _get_requests_prefix_and_url(args.port)

        os.environ["DASH_REQUESTS_PATHNAME_PREFIX"] = req_prefix
        os.environ["DASH_ROUTES_PATHNAME_PREFIX"] = "/"
        os.environ["DASH_HOST"] = args.host
        os.environ["DASH_PORT"] = str(args.port)
        os.environ["DASH_PROXY"] = proxy_url

        print("Dash environment set:")
        print(f"  DASH_REQUESTS_PATHNAME_PREFIX={os.environ['DASH_REQUESTS_PATHNAME_PREFIX']}")
        print(f"  DASH_ROUTES_PATHNAME_PREFIX={os.environ['DASH_ROUTES_PATHNAME_PREFIX']}")
        print(f"  DASH_HOST={os.environ['DASH_HOST']}")
        print(f"  DASH_PORT={os.environ['DASH_PORT']}")
        print(f"  DASH_PROXY={os.environ['DASH_PROXY']}")
        print()
        print("Open in browser:")
        print(f"  {browser_url}")


def load_ipython_extension(ipython):
    """
    Register the SetDashEnvMagic with IPython.

    This function is called automatically when the extension is loaded
    via %load_ext nanohubdash.

    Args:
        ipython: The IPython shell instance.
    """
    ipython.register_magics(SetDashEnvMagic)



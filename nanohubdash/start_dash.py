#!/usr/bin/env python3
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
start_dash - Command-line tool to run Dash applications on nanoHUB.

This script launches a Dash application with the proper proxy configuration
for running on the nanoHUB platform. It automatically:

- Configures the Dash request/route pathname prefixes for the nanoHUB proxy
- Starts the wrwroxy reverse proxy to handle incoming connections
- Injects a header bar with logo, support ticket link, and session termination button
- Handles graceful shutdown on SIGINT, SIGTERM, and SIGHUP signals

Usage:
    start_dash --app myapp.py [--debug True] [--logo URL]

Arguments:
    --app     Required. Path to the Dash application Python file.
              The file must define `app = dash.Dash(...)`.
    --debug   Optional. Enable debug mode (True/False). Default: False.
    --logo    Optional. URL for the logo displayed in the header bar.

Example:
    start_dash --app my_dashboard.py --debug True

Requirements:
    - Must be run on a nanoHUB environment with SESSION and SESSIONDIR set
    - The wrwroxy tool must be available (use -e wrwroxy-0.2)
    - python3 must be on PATH
"""

import argparse
import binascii
import glob
import os
import shutil
import signal
import sys
import tempfile
import time
from subprocess import Popen

# Global process handles for cleanup on shutdown
dashProcess = None
wrwProcess = None


def normalize_prefix(p: str) -> str:
    """
    Normalize a URL path prefix to ensure it starts and ends with '/'.

    Args:
        p: The path prefix string to normalize.

    Returns:
        The normalized path with leading and trailing slashes.

    Example:
        >>> normalize_prefix("weber/123")
        '/weber/123/'
    """
    if not p.startswith("/"):
        p = "/" + p
    if not p.endswith("/"):
        p += "/"
    return p


def get_session():
    """
    Retrieve the nanoHUB session ID and session directory from environment.

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


def get_cookie():
    """
    Retrieve the weber authentication cookie name and token for the session.

    This reads the VNC password file and constructs the authentication token
    needed for weber proxy authentication.

    Returns:
        tuple: (cookie_name, token) or ("", "") if not running on a hub.
    """
    cookie_name = ""
    try:
        session = int(os.environ['SESSION'])
        pwfile = glob.glob('/var/run/Xvnc/passwd-*')[0]
        with open(pwfile, 'rb') as f:
            pwd = binascii.hexlify(f.read()).decode('utf-8')
            token = "%d:%s" % (session, str(pwd))

        fn = os.path.join(os.environ['SESSIONDIR'], 'resources')
        with open(fn, 'r') as f:
            res = f.read()
        for line in res.split('\n'):
            if line.startswith('hub_url'):
                url = line.split()[1]
                host = url[url.find('//') + 2:]
                cookie_name = 'weber-auth-' + host.replace('.', '-')
                break
    except Exception:
        # Not running on a hub
        return "", ""
    return cookie_name, token


def get_proxy_addr():
    """
    Parse the nanoHUB resources file to construct proxy URL information.

    Reads hub_url, filexfer_port, and filexfer_cookie from the session's
    resources file to construct the weber proxy path and full URL.

    Returns:
        tuple: (normalized_path, full_proxy_url, filexfer_port)

    Raises:
        RuntimeError: If required fields cannot be parsed from resources file.
    """
    session, sessiondir = get_session()
    fn = os.path.join(sessiondir, "resources")

    url = fxp = fxc = None
    with open(fn) as f:
        for line in f:
            if line.startswith("hub_url"):
                url = line.split(" ", 1)[1].strip().replace('"', "")
            elif line.startswith("filexfer_port"):
                full_port = int(line.split()[1])
                fxp = str(full_port % 1000)
            elif line.startswith("filexfer_cookie"):
                fxc = line.split()[1]

    if not (url and fxp and fxc):
        raise RuntimeError("Could not parse resources file")

    path = f"/weber/{session}/{fxc}/{fxp}/"
    proxy_url = "https://proxy." + url.split("//", 1)[1] + path
    return normalize_prefix(path), proxy_url, full_port


def str2bool(v):
    """
    Convert a string value to boolean.

    Args:
        v: Value to convert (string, int, or bool).

    Returns:
        bool: True if value represents a truthy string, False otherwise.

    Example:
        >>> str2bool("True")
        True
        >>> str2bool("0")
        False
    """
    return str(v).lower() in ("1", "true", "yes", "on")


def shutdown(signum, frame):
    """
    Signal handler for graceful shutdown of Dash and wrwroxy processes.

    Terminates both the Dash application and wrwroxy processes when
    a shutdown signal is received.

    Args:
        signum: Signal number received.
        frame: Current stack frame (unused).
    """
    global dashProcess, wrwProcess
    print(f"{time.ctime()} signal {signum}", flush=True)

    for name, proc in (("wrwroxy", wrwProcess), ("dash", dashProcess)):
        if proc and proc.poll() is None:
            print(f"terminating {name} pid={proc.pid}", flush=True)
            proc.terminate()


def get_tool_details():
    """
    Extract tool/application details from the nanoHUB environment.

    Determines the application name from multiple sources (in order):
    1. TOOLDIR environment variable (e.g., /apps/mytool/r123)
    2. SUBMIT_APPLICATION_REVISION environment variable
    3. application_name field in the resources file

    Also constructs URLs for support tickets and session termination.

    Returns:
        tuple: (app_name, hub_host, ticket_url, hub_url, session_id)
    """
    import re

    # Extract hub hostname from uname (e.g., "nanohub-xyz" -> "nanohub")
    host = os.uname()[1]
    lhost = host.split('-')[0].lower()

    # Determine application name from various sources
    app = "unknown"

    # Try TOOLDIR first (e.g., /apps/mytool/r123)
    tooldir = os.getenv('TOOLDIR')
    if tooldir:
        match = re.search(r'\/apps\/([a-zA-Z0-9]+)\/r[0-9]+', tooldir)
        if match:
            app = match.group(1)

    # Try SUBMIT_APPLICATION_REVISION (e.g., mytool_r123)
    if app == "unknown":
        rev = os.getenv('SUBMIT_APPLICATION_REVISION')
        if rev:
            match = re.search(r'([a-zA-Z0-9]+)_r[0-9]+', rev)
            if match:
                app = match.group(1)

    # Try resources file
    if app == "unknown":
        session, sessiondir = get_session()
        fn = os.path.join(sessiondir, "resources")
        if os.path.exists(fn):
            with open(fn, "r") as f:
                for line in f:
                    if line.startswith("application_name"):
                        parts = line.split(" ", 1)
                        if len(parts) > 1:
                            app = parts[1].strip().replace('"', "").replace(" ", "_")
                        break

    app = app.lower()

    # Construct support ticket URL
    remote_url = f"https://{lhost}.org/feedback/report_problems?group=app-{app}"

    # Get hub_url from resources file
    session, sessiondir = get_session()
    fn = os.path.join(sessiondir, "resources")
    hub_url = "https://nanohub.org"  # default
    if os.path.exists(fn):
        with open(fn, "r") as f:
            for line in f:
                if line.startswith("hub_url"):
                    hub_url = line.split(" ", 1)[1].strip().replace('"', "")
                    break

    home_url = hub_url
    return app, lhost, remote_url, home_url, session


def write_runner(app_path: str, remote_url: str, home_url: str, proxy_url: str, logo_url: str) -> str:
    """
    Create a temporary Python runner script for the Dash application.

    Generates a runner script that:
    - Imports the user's Dash app module
    - Overrides pathname prefixes from environment variables
    - Injects a header bar with logo, support link, and terminate button
    - Starts the Dash server with appropriate host/port settings

    Args:
        app_path: Absolute path to the user's Dash application file.
        remote_url: URL for the "Submit a ticket" support link.
        home_url: URL for the "Terminate Session" button.
        proxy_url: The full proxy URL where the app will be accessible.
        logo_url: URL for the logo image in the header.

    Returns:
        str: Path to the generated temporary runner script.
    """
    app_dir = os.path.dirname(app_path)
    mod = os.path.splitext(os.path.basename(app_path))[0]

    runner_code = f"""\
import os, sys, importlib
sys.path.insert(0, {app_dir!r})

m = importlib.import_module({mod!r})

# Accept either:
#  - app = Dash(...)
#  - server = Flask app (from app.server)
app = getattr(m, "app", None)
if app is None:
    raise RuntimeError("Your app file must define `app = dash.Dash(...)` for dev-run fallback.")

# Override pathname prefixes with environment variables
requests_prefix = os.getenv("DASH_REQUESTS_PATHNAME_PREFIX")
routes_prefix = os.getenv("DASH_ROUTES_PATHNAME_PREFIX")
if requests_prefix and hasattr(app, 'config'):
    app.config.requests_pathname_prefix = requests_prefix
    print(f"Overriding requests_pathname_prefix to: {{requests_prefix}}", flush=True)
if routes_prefix and hasattr(app, 'config'):
    app.config.routes_pathname_prefix = routes_prefix
    print(f"Overriding routes_pathname_prefix to: {{routes_prefix}}", flush=True)

host = os.getenv("HOST", "0.0.0.0")
port = int(os.getenv("PORT", "8001"))
debug = os.getenv("DASH_DEBUG", "False").lower() in ("1","true","yes","on")

# Suppress Flask/Werkzeug banner
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
if not debug:
    os.environ['WERKZEUG_RUN_MAIN'] = 'true' # Suppress reloader message if possible

print(f"🚀 Dash is ready! Access it here: {proxy_url}", flush=True)

# Inject Header
try:
    from dash import html
except ImportError:
    try:
        import dash_html_components as html
    except ImportError:
        html = None

if app is not None and html is not None:
    try:
        _orig_layout = app.layout
        _orig_layout = app.layout
        def _wrapped_layout():
            # Styles
            header_style = {{
                'display': 'flex',
                'align-items': 'center',
                'justify-content': 'flex-end',
                'background-color': '#f8f9fa',
                'padding': '10px 20px',
                'border-bottom': '1px solid #dee2e6',
                'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
            }}
            btn_base_style = {{
                'display': 'inline-block',
                'font-weight': '400',
                'text-align': 'center',
                'vertical-align': 'middle',
                'user-select': 'none',
                'padding': '0.375rem 0.75rem',
                'font-size': '1rem',
                'line-height': '1.5',
                'border-radius': '0.25rem',
                'transition': 'color 0.15s, background-color 0.15s, border-color 0.15s',
                'cursor': 'pointer',
                'text-decoration': 'none',
                'margin-left': '10px',
                'border': '1px solid transparent'
            }}
            btn_info_style = {{**btn_base_style, 'color': '#fff', 'background-color': '#17a2b8', 'border-color': '#17a2b8'}}
            btn_danger_style = {{**btn_base_style, 'color': '#fff', 'background-color': '#dc3545', 'border-color': '#dc3545'}}

            header = html.Div([
                html.Img(src=f"{logo_url}", style={{'height': '40px', 'marginRight': 'auto'}}),
                html.A("Submit a ticket", href="{remote_url}", target="_blank", style=btn_info_style),
                html.A("Terminate Session", href="{home_url}", style=btn_danger_style),
            ], style=header_style)

            if callable(_orig_layout):
                content = _orig_layout()
            else:
                content = _orig_layout
            return html.Div([header, content])
        app.layout = _wrapped_layout
    except Exception as e:
        print(f"Warning: Could not inject header: {{e}}")

app.run(host=host, port=port, debug=debug)
"""
    fd, path = tempfile.mkstemp(prefix="dash_runner_", suffix=".py")
    with os.fdopen(fd, "w") as f:
        f.write(runner_code)
    return path


def main():
    """
    Main entry point for the start_dash command.

    Parses command-line arguments, sets up the environment, and launches
    both the Dash application and wrwroxy reverse proxy.

    The function:
    1. Parses --app, --debug, and --logo arguments
    2. Configures environment variables for Dash pathname prefixes
    3. Creates a runner script that wraps the user's app with header injection
    4. Launches the Dash app on port 8001
    5. Launches wrwroxy on port 8000 to proxy requests
    6. Waits for the Dash process to exit and performs cleanup

    Returns:
        int: Exit code from the Dash process.

    Raises:
        RuntimeError: If the app file is not found or python3 is not on PATH.
    """
    global dashProcess, wrwProcess

    ap = argparse.ArgumentParser(
        prog="start_dash",
        description="Run a Dash application on nanoHUB with proxy configuration.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  start_dash --app myapp.py
  start_dash --app dashboard.py --debug True
  start_dash --app app.py --logo https://example.com/logo.png
        """
    )
    ap.add_argument(
        "--app",
        required=True,
        help="Path to the Dash application Python file (must define app = dash.Dash(...))"
    )
    ap.add_argument(
        "--debug",
        default="False",
        help="Enable debug mode (True/False, default: False)"
    )
    ap.add_argument(
        "--logo",
        default="https://nanohub.org/app/site/media/images/PressKit/nanoHUB_logo_color.jpg",
        help="URL for the logo displayed in the header bar"
    )
    args = ap.parse_args()

    debug = str2bool(args.debug)
    logo_url = args.logo
    app_path = os.path.abspath(args.app)
    if not os.path.exists(app_path):
        raise RuntimeError(f"{app_path} not found")

    # Get nanoHUB proxy configuration
    p_path, p_url, p_port = get_proxy_addr()

    # Configure Dash environment variables
    os.environ["DASH_REQUESTS_PATHNAME_PREFIX"] = p_path
    os.environ["DASH_ROUTES_PATHNAME_PREFIX"] = "/"
    os.environ["HOST"] = "0.0.0.0"
    os.environ["PORT"] = "8001"
    os.environ["DASH_DEBUG"] = "True" if debug else "False"

    print(f"Proxy URL : {p_url}", flush=True)
    print(f"Dash port : 8001", flush=True)
    print(f"Proxy port: 8000", flush=True)

    # Set up environment for subprocess
    env = os.environ.copy()
    app_dir = os.path.dirname(app_path)
    env["PYTHONPATH"] = app_dir + os.pathsep + env.get("PYTHONPATH", "")

    # Get tool details for header bar
    app_name, lhost, remote_url, home_url, session = get_tool_details()
    os.environ["APP_NAME"] = app_name
    print(f"App: {app_name}, Host: {lhost}", flush=True)

    # Construct session termination URL
    base_host = home_url.rstrip("/")
    terminate_url = f"{base_host}/tools/{app_name}/stop?sess={session}"

    # Verify python3 is available
    if shutil.which("python3") is None:
        raise RuntimeError("python3 not found on PATH")

    # Launch Dash application
    print("Starting Dash (dev runner)", flush=True)
    runner = write_runner(app_path, remote_url, terminate_url, p_url, logo_url)
    dashProcess = Popen([sys.executable, runner], env=env)

    # Launch wrwroxy reverse proxy
    wrw_cmd = (
        "use -e wrwroxy-0.2 && "
        "exec wrwroxy "
        "--listenHost 0.0.0.0 "
        "--listenPort 8000 "
        "--forwardHost 127.0.0.1 "
        "--forwardPort 8001 "
    )
    if debug:
        wrw_cmd += " --stream-log"

    print("Starting wrwroxy", flush=True)
    wrw_env = os.environ.copy()
    s_id, _ = get_session()
    wrw_env['SESSION'] = s_id
    wrwProcess = Popen(["bash", "-lc", wrw_cmd], env=wrw_env)

    # Wait for Dash to exit and clean up
    rc = dashProcess.wait()
    shutdown(None, None)
    return rc


if __name__ == "__main__":
    for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(s, shutdown)
    sys.exit(main())

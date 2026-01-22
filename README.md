# nanohub-dash

Jupyter magic commands for configuring Dash apps on nanoHUB.

## Installation

```bash
pip install nanohub-dash
```

## Usage

In a Jupyter notebook:

```python
# Load the extension
%load_ext nanohubdash

# Set up the Dash environment (uses default port 8001 and host 0.0.0.0)
%set_dash_env

# Or specify custom port and host
%set_dash_env --port 8050 --host 127.0.0.1
```

This magic command sets the following environment variables:
- `DASH_REQUESTS_PATHNAME_PREFIX` - The proxy path prefix for Dash requests
- `DASH_ROUTES_PATHNAME_PREFIX` - Set to `/`
- `DASH_HOST` - The bind host for Dash
- `DASH_PORT` - The port for Dash
- `DASH_BASE_PROXY` - The proxy URL (https://proxy.<hub_host>)

After running the magic, it will print the browser URL where you can access your Dash app.

## Example

```python
%load_ext nanohubdash
%set_dash_env --port 8001

from dash import Dash, html

app = Dash(__name__)
app.layout = html.Div("Hello nanoHUB!")

if __name__ == "__main__":
    app.run_server()
```

## Requirements

- Python >= 3.8
- IPython >= 7.0
- Must be running on a nanoHUB environment with `SESSION` and `SESSIONDIR` environment variables set

## License

MIT

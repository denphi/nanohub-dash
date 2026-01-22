# nanohub-dash

[![Documentation Status](https://readthedocs.org/projects/nanohub-dash/badge/?version=latest)](https://nanohub-dash.readthedocs.io/en/latest/?badge=latest)

Tools for running Dash applications on nanoHUB.

## Documentation

Full documentation is available at [https://nanohub-dash.readthedocs.io](https://nanohub-dash.readthedocs.io)

## Installation

```bash
pip install nanohub-dash
```

## Features

- **Jupyter Magic Command** (`%set_dash_env`): Configure environment variables for Dash apps directly in Jupyter notebooks
- **Command-line Tool** (`start_dash`): Launch Dash applications with automatic proxy configuration and header injection

## Quick Start

### Jupyter Notebook

```python
%load_ext nanohubdash
%set_dash_env

import os
from dash import Dash, html

app = Dash(__name__)
app.layout = html.Div("Hello nanoHUB!")

if __name__ == "__main__":
    app.run(
        host=os.environ.get("DASH_HOST", "0.0.0.0"),
        port=os.environ.get("DASH_PORT", "8001"),
    )
```

### Command Line

```bash
start_dash --app myapp.py
```

## Environment Variables

The magic command sets the following environment variables:

- `DASH_REQUESTS_PATHNAME_PREFIX` - The proxy path prefix for Dash requests
- `DASH_ROUTES_PATHNAME_PREFIX` - Set to `/`
- `DASH_HOST` - The bind host for Dash
- `DASH_PORT` - The port for Dash
- `DASH_BASE_PROXY` - The proxy URL (https://proxy.<hub_host>)

## Requirements

- Python >= 3.8
- IPython >= 7.0
- Must be running on a nanoHUB environment with `SESSION` and `SESSIONDIR` environment variables set

## License

MIT License - Copyright 2026 HUBzero Foundation, LLC.

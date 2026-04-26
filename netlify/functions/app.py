"""
Netlify Functions entry point.
Wraps the Flask WSGI app with the `awsgi` adapter so it runs as an
AWS Lambda-compatible handler (which Netlify Functions uses under the hood).
"""

import sys
import os

# ---------------------------------------------------------------------------
# Make the project root importable so we can import `app` and `ml_runtime`
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import awsgi
from app import app  # the Flask application object


def handler(event, context):
    """AWS Lambda / Netlify Functions entry point."""
    return awsgi.response(app, event, context, base64_content_types={"image/png", "image/jpeg", "image/gif", "image/webp"})

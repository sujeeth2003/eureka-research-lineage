import feedparser
import time
import os
import ssl
import urllib.error
import urllib.request


def _create_ssl_context():
    """Create a verified SSL context, preferring certifi when available."""
    try:
        import certifi  # Optional dependency for reliable CA bundle on Windows.

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()



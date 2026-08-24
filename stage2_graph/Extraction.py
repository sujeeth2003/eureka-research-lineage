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


def fetch_papers(search_query, max_results=50, start=0):
    base_url = "https://export.arxiv.org/api/query?"
    query = f"search_query={search_query}&start={start}&max_results={max_results}&sortBy=submittedDate&sortOrder=ascending"
    url = base_url + query
    #print(url)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    verify_ssl = os.getenv("ARXIV_SSL_VERIFY", "1") != "0"
    ssl_context = _create_ssl_context() if verify_ssl else ssl._create_unverified_context()

    try:
        response = urllib.request.urlopen(request, context=ssl_context, timeout=30)
    except urllib.error.URLError as exc:
        # Keep secure defaults and provide actionable guidance for cert issues.
        if isinstance(exc.reason, ssl.SSLCertVerificationError):
            raise RuntimeError(
                "SSL certificate verification failed. Install/upgrade certifi "
                "(pip install -U certifi) or set ARXIV_SSL_VERIFY=0 only for local testing."
            ) from exc
        raise
    feed = feedparser.parse(response.read())
    

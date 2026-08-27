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
    
    papers = []
    for entry in feed.entries:
        paper = {
            "arxiv_id": entry.id.split('/abs/')[-1],  # e.g. "quant-ph/0307015" or "2301.00001"
            "title": entry.title.replace('\n', ' ').strip(),
            "abstract": entry.summary.replace('\n', ' ').strip(),
            "published": entry.published,       # ISO 8601, e.g. "2003-07-07T13:46:39-04:00"
            "updated": entry.updated,
            "authors": [a.name for a in entry.authors],
            "primary_category": entry.arxiv_primary_category['term'],
            "categories": [t['term'] for t in entry.tags],
            "pdf_url": next((l.href for l in entry.links if l.type == 'application/pdf'), None),
            "comment": entry.get('arxiv_comment', None),   # often has page count, "accepted at X"
            "journal_ref": entry.get('arxiv_journal_ref', None),
            "doi": entry.get('arxiv_doi', None),
        }
        papers.append(paper)
    return papers

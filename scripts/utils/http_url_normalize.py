"""RFC-safe HTTP(S) URL path encoding for scrapers and loaders."""

from __future__ import annotations

from urllib.parse import quote, unquote, urlparse, urlunparse


def normalize_http_url_path_encoding(url: str) -> str:
    """
    Percent-encode characters that are illegal in URL paths (e.g. raw spaces) without
    double-encoding existing ``%xx`` sequences. Query string is left unchanged; fragment stripped.
    """
    raw = (url or "").strip()
    if not raw:
        return raw
    try:
        p = urlparse(raw)
    except Exception:
        return raw
    if p.scheme not in ("http", "https") or not p.netloc:
        return raw
    try:
        path = quote(unquote(p.path), safe="/")
        return urlunparse((p.scheme, p.netloc, path, p.params, p.query, ""))
    except Exception:
        return raw

"""
Path helpers shared with ``scripts/utils/log_sync.py`` and ``export_bronze_to_json.py``.

- ``LOG_GDRIVE_MOUNT`` / ``gdrive_mount_path()`` — used by **log sync** and wikidata export to copy
  into Google Drive.
- ``resolve_scraped_meetings_output_root()`` — **meetings scraper** default is the repo cache
  (``data/cache/scraped_meetings``), same family as ``data/cache/wikidata``. Override with
  ``SCRAPED_MEETINGS_ROOT`` (e.g. a mounted Drive path) when you want artifacts outside the repo.
"""
from __future__ import annotations

import os
from pathlib import Path

_DEFAULT_LOG_GDRIVE_MOUNT = "/mnt/g/My Drive"

# ``scripts/utils/gdrive_paths.py`` → repo root is two parents up from ``scripts/``.
_REPO_ROOT = Path(__file__).resolve().parents[2]


def gdrive_mount_path() -> Path:
    """Mounted Google Drive root (default ``/mnt/g/My Drive``)."""
    return Path(os.getenv("LOG_GDRIVE_MOUNT", _DEFAULT_LOG_GDRIVE_MOUNT)).expanduser()


def default_scraped_meetings_data_cache() -> Path:
    """Default meetings artifact root: ``<repo>/data/cache/scraped_meetings`` (gitignored ``data/``)."""
    return _REPO_ROOT / "data" / "cache" / "scraped_meetings"


def scraped_meetings_root_resolution_note() -> str:
    """Which env branch :pyfunc:`resolve_scraped_meetings_output_root` used (for logs / manifests)."""
    explicit = (os.getenv("SCRAPED_MEETINGS_ROOT") or "").strip()
    if explicit:
        return "SCRAPED_MEETINGS_ROOT"
    return "DATA_CACHE (repo data/cache/scraped_meetings/)"


def resolve_scraped_meetings_output_root() -> Path:
    """
    Resolve where meeting PDFs should be stored.

    - If ``SCRAPED_MEETINGS_ROOT`` is set → that path (full override, e.g. Google Drive mount).
    - Else → ``<open-navigator>/data/cache/scraped_meetings`` (with ``{state}/{type}/{id}/…`` under it).
    """
    explicit = (os.getenv("SCRAPED_MEETINGS_ROOT") or "").strip()
    if explicit:
        return Path(explicit).expanduser()
    return default_scraped_meetings_data_cache()

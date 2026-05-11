"""
Extract contact hints from HTML fetched during meetings / jurisdiction crawls.

Collects ``mailto:`` and ``tel:`` links plus a conservative pass for visible email addresses
and US-style phone numbers in page text. Intended for manifest enrichment, not as verified CRM data.
"""

from __future__ import annotations

import re
from html import unescape
from typing import Any, Dict, List, Set
from urllib.parse import unquote

_MAILTO_RE = re.compile(r"mailto:([^?#\"'>\s\\]+)", re.I)
_TEL_RE = re.compile(r"tel:([^?#\"'>\s\\]+)", re.I)
# Visible emails: avoid matching long hex-like strings
_EMAIL_RE = re.compile(
    r"(?<![a-z0-9._%+-])"
    r"[a-z0-9][a-z0-9._%+-]{0,63}"
    r"@[a-z0-9][a-z0-9.-]{0,253}\.[a-z]{2,63}"
    r"(?![a-z0-9._%+-])",
    re.I,
)
_PHONE_RE = re.compile(
    r"(?:\+?1[-.\s]?)?(?:\(?[0-9]{3}\)?[-.\s/]?[0-9]{3}[-.\s/]?[0-9]{4})\b"
)
_BOGUS_EMAIL_SUFFIX = re.compile(
    r"\.(png|jpe?g|gif|webp|svg|ico|css|js|map|woff2?|ttf|eot)(\b|$)",
    re.I,
)


def _clean_mailto(raw: str) -> str:
    s = unescape(unquote((raw or "").strip()))
    if "," in s:
        s = s.split(",")[0].strip()
    return s.strip().lower()


def _normalize_phone_display(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return (raw or "").strip()[:24]


def extract_contacts_from_page(
    html: str,
    page_url: str,
    *,
    max_emails: int = 35,
    max_phones: int = 20,
) -> Dict[str, Any]:
    """
    Return ``{ "page_url", "emails": [...], "phones": [...] }`` for one HTML document.
    """
    emails: Set[str] = set()
    phones: Set[str] = set()
    text = html or ""

    for m in _MAILTO_RE.finditer(text):
        em = _clean_mailto(m.group(1))
        if "@" in em and not _BOGUS_EMAIL_SUFFIX.search(em):
            emails.add(em)

    for m in _TEL_RE.finditer(text):
        raw_tel = unquote(m.group(1).strip())
        if ";" in raw_tel:
            raw_tel = raw_tel.split(";", 1)[0].strip()
        digits = re.sub(r"\D", "", raw_tel)
        if len(digits) >= 10:
            phones.add(_normalize_phone_display(digits))

    # mailto already counted; skip those spans in a crude way — still OK if duplicate
    for m in _EMAIL_RE.finditer(text):
        em = m.group(0).strip().lower()
        if not _BOGUS_EMAIL_SUFFIX.search(em) and "@" in em:
            emails.add(em)

    for m in _PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if len(digits) >= 10:
            phones.add(_normalize_phone_display(m.group(0)))

    return {
        "page_url": page_url,
        "emails": sorted(emails)[:max_emails],
        "phones": sorted(phones)[:max_phones],
    }


def merge_contact_manifest_rows(
    rows: List[Dict[str, Any]],
    *,
    max_distinct_emails: int = 80,
    max_distinct_phones: int = 50,
    max_pages_in_manifest: int = 28,
) -> Dict[str, Any]:
    """
    Merge per-page dicts from ``extract_contacts_from_page`` into one manifest object.
    """
    all_emails: Set[str] = set()
    all_phones: Set[str] = set()
    by_page: List[Dict[str, Any]] = []
    for row in rows:
        if not row:
            continue
        em = row.get("emails") or []
        ph = row.get("phones") or []
        if not em and not ph:
            continue
        by_page.append(row)
        all_emails.update(em)
        all_phones.update(ph)
    return {
        "emails": sorted(all_emails)[:max_distinct_emails],
        "phones": sorted(all_phones)[:max_distinct_phones],
        "by_page": by_page[:max_pages_in_manifest],
    }

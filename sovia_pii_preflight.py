"""Offline metadata-only PII/credential *pattern* preflight (not de-identification).

Conservative fail-closed heuristic gate for SOVIA direct audit's two modes
and the existing approved-local sanitized converter pathway.
No source values, matches, field names or paths are logged or returned.
No claim of comprehensive PII detection, consent, or legal compliance.
"""
from __future__ import annotations

import ipaddress
import re

MAX_DEPTH = 16
MAX_NODES = 20_000
MAX_STRING_LENGTH = 4096

EMAIL = re.compile(r"(?i)(?<![\w.+-])[\w.+-]+@[\w.-]+\.[a-z]{2,}(?![\w-])")
KR_MOBILE = re.compile(r"(?<!\d)(?:(?:\+?82)[._ -]?)?0?10[._ -]?\d{4}[._ -]?\d{4}(?!\d)")
KR_RESIDENT_ID = re.compile(r"(?<!\d)\d{6}[._-]?[1-8]\d{6}(?!\d)")
IPV4 = re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)")
UUID = re.compile(r"(?i)(?<![a-f0-9])[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}(?![a-f0-9])")
ACCESS_KEY = re.compile(r"(?<![A-Za-z0-9])(?:AKIA|ASIA)[A-Z0-9]{16}(?![A-Za-z0-9])")
SECRET_TOKEN = re.compile(
    r"(?i)(?:sk[-_][A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|"
    r"xox[baprs]-[A-Za-z0-9-]{20,})"
)
JWT_LIKE = re.compile(r"(?:eyJ[A-Za-z0-9_-]{10,}\.)[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")
CARD_DIGITS = re.compile(r"(?<!\d)(?:\d[ ._-]?){12,18}\d(?!\d)")
LONG_OPAQUE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9_-]{40,}(?![A-Za-z0-9])")


class PreflightError(ValueError):
    """Generic non-disclosing failure. This is not a PII proof."""


def _luhn(value):
    digits = [int(ch) for ch in value if ch.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def _high_risk_pattern(text):
    # Not user-facing: only an opaque refusal code is returned on match.
    if (EMAIL.search(text) or KR_MOBILE.search(text) or
            KR_RESIDENT_ID.search(text) or UUID.search(text) or
            ACCESS_KEY.search(text) or SECRET_TOKEN.search(text) or
            JWT_LIKE.search(text) or LONG_OPAQUE.search(text)):
        return True
    for candidate in IPV4.finditer(text):
        try:
            ipaddress.IPv4Address(candidate.group())
        except ipaddress.AddressValueError:
            continue
        return True
    return any(_luhn(match.group()) for match in CARD_DIGITS.finditer(text))


def assert_no_high_risk_patterns(*documents):
    """Reject recognizable PII/secrets in sanitized metadata and supplied policy.

    Entire operation is in-process/offline. Input is the bounded JSON already
    decoded by the canonical SOVIA reader. Does NOT inspect raw n8n payloads.
    Returns no matched content, and does NOT automatically modify input.
    """
    nodes = 0
    for document in documents:
        stack = [(document, 0)]
        while stack:
            value, depth = stack.pop()
            nodes += 1
            if nodes > MAX_NODES or depth > MAX_DEPTH:
                raise PreflightError("PREFLIGHT_LIMIT_EXCEEDED")
            if isinstance(value, dict):
                for key, item in value.items():
                    if type(key) is not str:
                        raise PreflightError("PREFLIGHT_INVALID_METADATA")
                    stack.append((item, depth + 1))
                    stack.append((key, depth + 1))
            elif isinstance(value, list):
                stack.extend((item, depth + 1) for item in value)
            elif type(value) is str:
                if len(value) > MAX_STRING_LENGTH:
                    raise PreflightError("PREFLIGHT_STRING_TOO_LONG")
                if _high_risk_pattern(value):
                    raise PreflightError("PREFLIGHT_SUSPECT_METADATA")
            elif value is not None and type(value) not in (bool, int, float):
                raise PreflightError("PREFLIGHT_INVALID_METADATA")
    return "HEURISTIC_PATTERN_SCAN_CLEAR_NOT_PII_CERTIFIED"

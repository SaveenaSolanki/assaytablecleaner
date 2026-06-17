"""Shared utilities for the assaytablecleaner package."""

import re


def strip_units(raw: str) -> str:
    """Remove common unit wrappers like brackets from a unit string.

    Examples:
        '[uM]' -> 'uM'
        ' (nM)' -> 'nM'
    """
    return raw.strip("[]() ")


def parse_range(raw: str) -> list[float] | None:
    """Attempt to parse a value range like '10-20' or '1.5 - 3.0'.

    Returns a list of two floats or None.
    """
    parts = re.split(r"\s*-\s*", raw.strip(), maxsplit=1)
    if len(parts) != 2:
        return None
    try:
        lo = float(parts[0])
        hi = float(parts[1])
        return [lo, hi]
    except ValueError:
        return None

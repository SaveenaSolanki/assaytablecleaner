"""Core assay table cleaning logic: parse values, standardize units, convert to molar."""

import math

import pandas as pd

# Unit conversion factors to molar (M)
UNIT_FACTORS: dict[str, float] = {
    "M": 1.0,
    "mM": 1e-3,
    "uM": 1e-6,
    "µm": 1e-6,  # mu symbol
    "μM": 1e-6,   # Greek mu (different Unicode char)
    "nM": 1e-9,
    "pM": 1e-12,
}


def parse_value(raw_value) -> tuple[float | None, str | None]:
    """Parse a measurement value that may include operators like >, <, =, >=, <=, ~.

    Returns (numeric_value, operator) tuple.
    If value cannot be parsed, returns (None, None).
    """
    if pd.isna(raw_value):
        return None, None

    s = str(raw_value).strip()
    if not s:
        return None, None

    # Check for operators
    operator = None
    for op in [">=", "<=", ">", "<", "=", "~"]:
        if s.startswith(op):
            operator = op
            s = s[len(op):].strip()
            break

    # Try to parse numeric part
    try:
        numeric = float(s)
        return numeric, operator
    except ValueError:
        pass

    return None, None


def convert_to_molar(value: float, unit: str) -> float | None:
    """Convert a value in the given unit to molar.

    Returns None if unit is unknown.
    """
    unit = unit.strip()
    # Normalize mu variants
    if unit in ("µM", "μm", "uM"):
        unit = "uM"

    if unit in UNIT_FACTORS:
        return value * UNIT_FACTORS[unit]

    # Try case-insensitive match
    for known_unit, factor in UNIT_FACTORS.items():
        if known_unit.lower() == unit.lower():
            return value * factor

    return None


def compute_pactivity(value_molar: float) -> float | None:
    """Compute pActivity = -log10(value_molar).

    Returns None if value <= 0 (log undefined).
    """
    if value_molar is None or value_molar <= 0:
        return None
    try:
        return -math.log10(value_molar)
    except (ValueError, OverflowError):
        return None


def flag_measurement(
    value: float | None,
    operator: str | None,
    value_molar: float | None,
    unit: str,
) -> str:
    """Flag potentially problematic measurements.

    Returns empty string if OK, or a flag description.
    """
    flags = []

    if value is None:
        flags.append("unparseable_value")

    if value_molar is None and value is not None:
        flags.append("unknown_unit")

    if operator in (">", ">="):
        flags.append("above_limit")
    elif operator in ("<", "<="):
        flags.append("below_limit")

    if operator == "~":
        flags.append("approximate")

    if value_molar is not None:
        if value_molar > 1.0:
            flags.append("high_concentration")
        if value_molar < 1e-15:
            flags.append("ultra_low_concentration")

    return "; ".join(flags)


def clean_assay_row(
    raw_value,
    unit: str,
    compound_id: str = "",
    target_id: str = "",
    assay_type: str = "",
) -> dict:
    """Process a single assay measurement row.

    Returns a dict with all computed fields.
    """
    result = {
        "compound_id": str(compound_id),
        "target_id": str(target_id),
        "assay_type": str(assay_type),
        "raw_value": raw_value,
        "raw_unit": unit,
        "parsed_value": None,
        "operator": None,
        "standardized_unit": None,
        "value_molar": None,
        "pactivity": None,
        "flags": "",
    }

    value, operator = parse_value(raw_value)
    result["parsed_value"] = value
    result["operator"] = operator

    if value is not None:
        value_molar = convert_to_molar(value, unit)
        result["value_molar"] = value_molar
        result["standardized_unit"] = "M" if value_molar is not None else None

        if value_molar is not None:
            result["pactivity"] = compute_pactivity(value_molar)

    result["flags"] = flag_measurement(value, operator, result["value_molar"], unit)

    return result


def clean_assay_table(
    df: pd.DataFrame,
    value_col: str = "value",
    unit_col: str = "unit",
    compound_col: str = "compound_id",
    target_col: str = "target_id",
    assay_col: str = "assay_type",
) -> pd.DataFrame:
    """Clean an entire assay table.

    Returns a DataFrame with cleaned and computed columns.
    """
    results = []
    for _, row in df.iterrows():
        result = clean_assay_row(
            raw_value=row.get(value_col),
            unit=str(row.get(unit_col, "")),
            compound_id=str(row.get(compound_col, "")),
            target_id=str(row.get(target_col, "")),
            assay_type=str(row.get(assay_col, "")),
        )
        results.append(result)

    return pd.DataFrame(results)

<div align="center">

# 🧫 assaytablecleaner

**Parse, standardize & convert bioassay measurement values — unit-aware, flag-driven, reproducible.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-ac946f)](https://www.python.org/)
[![Tests](https://github.com/SaveenaSolanki/assaytablecleaner/actions/workflows/tests.yml/badge.svg)](https://github.com/SaveenaSolanki/assaytablecleaner/actions/workflows/tests.yml)
[![Last Commit](https://img.shields.io/github/last-commit/SaveenaSolanki/assaytablecleaner)](https://github.com/SaveenaSolanki/assaytablecleaner)
[![Repo Size](https://img.shields.io/github/repo-size/SaveenaSolanki/assaytablecleaner)](https://github.com/SaveenaSolanki/assaytablecleaner)
[![Part of CompBio Toolkit Suite](https://img.shields.io/badge/CompBio%20Toolkit%20Suite-Core%20Tool-ac946f)](https://github.com/SaveenaSolanki/compbio-toolkit-suite)

</div>

---

## Overview

Assay measurement tables in computational biology and drug discovery often contain
heterogeneous data: values with inequality operators (`>`, `<`, `>=`, `<=`, `~`),
mixed concentration units (M, mM, µM, nM, pM), unparseable entries, and missing values.
**assaytablecleaner** reads a CSV table and produces a cleaned, standardized version with:

- **Parsed numeric values** extracted from operator-prefixed strings
- **Standardized units** — all concentrations converted to molar (M)
- **pActivity** — computed as `-log10(value_molar)` for each measurement
- **Data quality flags** — above/below limit, approximate, missing, unparseable, out-of-range

## Installation

Requires **Python ≥ 3.10**.

```bash
# From source (recommended for now)
git clone https://github.com/SaveenaSolanki/assaytablecleaner.git
cd assaytablecleaner
pip install -e ".[dev]"
```

> PyPI release is planned. For now, install from source.

## Quick Start

```bash
# Clean a CSV file with default column names
assay-clean clean --input measurements.csv --out cleaned.csv

# Specify non-standard column names
assay-clean clean \
    --input data.csv \
    --value-col measurement \
    --unit-col concentration_unit \
    --out results.csv
```

### Input CSV format

Expected columns (default names, configurable):

| Column       | Default        | Description                       |
|--------------|----------------|-----------------------------------|
| `compound_id`| `compound_id`  | Compound identifier               |
| `target_id`  | `target_id`    | Biological target identifier      |
| `assay_type` | `assay_type`   | Assay type (IC50, EC50, Kd, etc.) |
| `value`      | `value`        | Measurement value (may have ops)  |
| `unit`       | `unit`         | Concentration unit                |

```csv
compound_id,target_id,assay_type,value,unit
CMP001,TGT001,IC50,5.2,uM
CMP002,TGT001,EC50,>100,uM
```

### Output columns

| Column             | Description                                        |
|--------------------|----------------------------------------------------|
| `raw_value`        | Original raw value string                          |
| `raw_unit`         | Original unit string                               |
| `parsed_value`     | Numeric value extracted (float or None)            |
| `operator`         | Operator if present (`>`, `<`, `>=`, `<=`, `=`, `~`) |
| `standardized_unit`| `"M"` if successfully converted to molar           |
| `value_molar`      | Value in molar (M)                                 |
| `pactivity`        | `-log10(value_molar)`                              |
| `flags`            | Semicolon-separated data quality flags             |

### Flag definitions

| Flag                        | Meaning                                  |
|-----------------------------|------------------------------------------|
| `unparseable_value`         | Value could not be parsed as a number    |
| `unknown_unit`              | Unit not recognized                      |
| `above_limit`               | Value prefixed with `>` or `>=`          |
| `below_limit`               | Value prefixed with `<` or `<=`          |
| `approximate`               | Value prefixed with `~`                  |
| `high_concentration`        | `value_molar > 1.0 M`                    |
| `ultra_low_concentration`   | `value_molar < 10⁻¹⁵ M`                  |

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=assaytablecleaner --cov-report=term-missing

# Lint
ruff check src/ tests/
```

## Data & Privacy

Example files and test fixtures contain **only synthetic, non-sensitive sample data**.
No real compound structures, proprietary assay results, patient data, or personally
identifiable information. All processing is local — no telemetry, no network calls.

## License

[MIT](LICENSE) — part of the [CompBio Toolkit Suite](https://github.com/SaveenaSolanki/compbio-toolkit-suite).

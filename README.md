# assaytablecleaner

Parse, standardize, and convert bioassay measurement values.

[![Tests](https://github.com/compbio-toolkit-suite/assaytablecleaner/actions/workflows/tests.yml/badge.svg)](https://github.com/compbio-toolkit-suite/assaytablecleaner/actions/workflows/tests.yml)

## Overview

Assay measurement tables in computational biology and drug discovery often contain
heterogeneous data: values with inequality operators (`>`, `<`, `>=`, `<=`, `~`),
mixed concentration units (M, mM, µM, nM, pM), unparseable entries, and missing
values. **assaytablecleaner** reads a CSV table and produces a cleaned,
standardized version with:

- **Parsed numeric values** extracted from operator-prefixed strings
- **Standardized units** — all concentrations converted to molar (M)
- **pActivity** — computed as `-log10(value_molar)` for each measurement
- **Data quality flags** — identifying above/below limit, approximate, missing,
  unparseable, or out-of-range measurements

## Installation

```bash
pip install assaytablecleaner
```

For development:

```bash
git clone https://github.com/compbio-toolkit-suite/assaytablecleaner.git
cd assaytablecleaner
pip install -e ".[dev]"
```

## Quick start

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
|-------------|----------------|-----------------------------------|
| compound_id | compound_id    | Compound identifier               |
| target_id   | target_id      | Biological target identifier      |
| assay_type  | assay_type     | Assay type (IC50, EC50, Kd, etc.) |
| value       | value          | Measurement value (may have ops)  |
| unit        | unit           | Concentration unit                |

Example:

```csv
compound_id,target_id,assay_type,value,unit
CMP001,TGT001,IC50,5.2,uM
CMP002,TGT001,EC50,>100,uM
```

### Output columns

The cleaned output adds:

| Column           | Description                                         |
|-----------------|-----------------------------------------------------|
| raw_value       | Original raw value string                           |
| raw_unit        | Original unit string                                |
| parsed_value    | Numeric value extracted (float or None)             |
| operator        | Operator if present (>, <, >=, <=, =, ~)            |
| standardized_unit | "M" if successfully converted to molar            |
| value_molar     | Value in molar (M)                                  |
| pactivity       | -log10(value_molar)                                 |
| flags           | Semicolon-separated data quality flags              |

### Flag definitions

| Flag                  | Meaning                                    |
|----------------------|--------------------------------------------|
| unparseable_value    | Value could not be parsed as a number      |
| unknown_unit         | Unit not recognized                        |
| above_limit          | Value prefixed with > or >=                |
| below_limit          | Value prefixed with < or <=               |
| approximate          | Value prefixed with ~                      |
| high_concentration   | value_molar > 1.0 M                        |
| ultra_low_concentration | value_molar < 10⁻¹⁵ M                   |

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=assaytablecleaner --cov-report=term-missing

# Lint
ruff check src/ tests/
```

## Non-sensitive data statement

This tool is designed for processing bioassay measurement data. The example files
and test fixtures included in this repository contain **only synthetic, non-sensitive
sample data**. No real compound structures, proprietary assay results, patient data,
or personally identifiable information are included.

## Non-Sensitive Data Statement

This repository contains generic utility code and toy/public-data examples only. It does not include unpublished datasets, internal lab data, trained models, manuscript-specific results, or confidential project assets.

## License

MIT

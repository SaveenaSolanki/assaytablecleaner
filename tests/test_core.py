"""Tests for assaytablecleaner.core module."""

import math

import numpy as np
import pandas as pd
import pytest

from assaytablecleaner.core import (
    clean_assay_row,
    clean_assay_table,
    compute_pactivity,
    convert_to_molar,
    flag_measurement,
    parse_value,
)

# --------------------------------------------------------------------------- #
# parse_value
# --------------------------------------------------------------------------- #

class TestParseValue:
    """Tests for parse_value function."""

    def test_plain_number(self):
        value, operator = parse_value("5.2")
        assert value == 5.2
        assert operator is None

    def test_integer_string(self):
        value, operator = parse_value("100")
        assert value == 100.0
        assert operator is None

    def test_negative_number(self):
        value, operator = parse_value("-3.5")
        assert value == -3.5
        assert operator is None

    def test_greater_than(self):
        value, operator = parse_value(">100")
        assert value == 100.0
        assert operator == ">"

    def test_less_than(self):
        value, operator = parse_value("<10")
        assert value == 10.0
        assert operator == "<"

    def test_greater_equal(self):
        value, operator = parse_value(">=50")
        assert value == 50.0
        assert operator == ">="

    def test_less_equal(self):
        value, operator = parse_value("<=0.5")
        assert value == 0.5
        assert operator == "<="

    def test_equals(self):
        value, operator = parse_value("=1.0")
        assert value == 1.0
        assert operator == "="

    def test_approximate(self):
        value, operator = parse_value("~2.5")
        assert value == 2.5
        assert operator == "~"

    def test_operator_with_space(self):
        value, operator = parse_value("> 100")
        assert value == 100.0
        assert operator == ">"

    def test_nan_value(self):
        value, operator = parse_value(np.nan)
        assert value is None
        assert operator is None

    def test_pandas_na(self):
        value, operator = parse_value(pd.NA)
        assert value is None
        assert operator is None

    def test_none_value(self):
        value, operator = parse_value(None)
        assert value is None
        assert operator is None

    def test_empty_string(self):
        value, operator = parse_value("")
        assert value is None
        assert operator is None

    def test_whitespace_only(self):
        value, operator = parse_value("   ")
        assert value is None
        assert operator is None

    def test_unparseable_string(self):
        value, operator = parse_value("invalid_value")
        assert value is None
        assert operator is None

    def test_scientific_notation(self):
        value, operator = parse_value("1.5e-3")
        assert value == 1.5e-3
        assert operator is None

    def test_operator_precedence_ge_over_g(self):
        """Ensure >= is checked before >"""
        value, operator = parse_value(">=10")
        assert value == 10.0
        assert operator == ">="


# --------------------------------------------------------------------------- #
# convert_to_molar
# --------------------------------------------------------------------------- #

class TestConvertToMolar:
    """Tests for convert_to_molar function."""

    def test_molar_identity(self):
        assert convert_to_molar(1.0, "M") == 1.0

    def test_millimolar(self):
        assert convert_to_molar(5.0, "mM") == 5e-3

    def test_micromolar_ascii(self):
        assert convert_to_molar(5.2, "uM") == 5.2e-6

    def test_micromolar_greek_mu(self):
        assert convert_to_molar(5.2, "μM") == 5.2e-6

    def test_micromolar_mu_symbol(self):
        assert convert_to_molar(5.2, "µm") == 5.2e-6

    def test_nanomolar(self):
        assert convert_to_molar(120.0, "nM") == pytest.approx(120e-9)

    def test_picomolar(self):
        assert convert_to_molar(10.0, "pM") == 10e-12

    def test_case_insensitive(self):
        assert convert_to_molar(3.5, "MM") == 3.5e-3  # mM upper case

    def test_unknown_unit(self):
        assert convert_to_molar(1.0, "kg") is None

    def test_empty_unit(self):
        assert convert_to_molar(1.0, "") is None

    def test_unit_with_whitespace(self):
        assert convert_to_molar(2.0, "  uM  ") == 2e-6


# --------------------------------------------------------------------------- #
# compute_pactivity
# --------------------------------------------------------------------------- #

class TestComputePactivity:
    """Tests for compute_pactivity function."""

    def test_1_molar(self):
        assert compute_pactivity(1.0) == 0.0

    def test_1_micromolar(self):
        expected = -math.log10(1e-6)
        assert compute_pactivity(1e-6) == pytest.approx(expected)

    def test_5_micromolar(self):
        # IC50 = 5.2 uM -> value_molar = 5.2e-6, pActivity = -log10(5.2e-6)
        expected = -math.log10(5.2e-6)
        assert compute_pactivity(5.2e-6) == pytest.approx(expected)

    def test_none_value(self):
        assert compute_pactivity(None) is None

    def test_zero_value(self):
        assert compute_pactivity(0.0) is None

    def test_negative_value(self):
        assert compute_pactivity(-1.0) is None


# --------------------------------------------------------------------------- #
# flag_measurement
# --------------------------------------------------------------------------- #

class TestFlagMeasurement:
    """Tests for flag_measurement function."""

    def test_ok_measurement(self):
        flags = flag_measurement(5.2, None, 5.2e-6, "uM")
        assert flags == ""

    def test_unparseable(self):
        flags = flag_measurement(None, None, None, "uM")
        assert "unparseable_value" in flags

    def test_unknown_unit(self):
        flags = flag_measurement(1.0, None, None, "XYZ")
        assert "unknown_unit" in flags

    def test_above_limit(self):
        flags = flag_measurement(100.0, ">", 100e-6, "uM")
        assert "above_limit" in flags

    def test_below_limit(self):
        flags = flag_measurement(10.0, "<", 10e-9, "nM")
        assert "below_limit" in flags

    def test_approximate(self):
        flags = flag_measurement(0.8, "~", 0.8e-6, "uM")
        assert "approximate" in flags

    def test_high_concentration(self):
        flags = flag_measurement(2.0, None, 2.0, "M")
        assert "high_concentration" in flags

    def test_ultra_low_concentration(self):
        flags = flag_measurement(1.0, None, 1e-16, "M")
        assert "ultra_low_concentration" in flags

    def test_multiple_flags(self):
        flags = flag_measurement(None, ">", None, "uM")
        assert "unparseable_value" in flags
        assert "above_limit" in flags


# --------------------------------------------------------------------------- #
# clean_assay_row
# --------------------------------------------------------------------------- #

class TestCleanAssayRow:
    """Tests for clean_assay_row function."""

    def test_basic_row(self):
        result = clean_assay_row(5.2, "uM", "CMP001", "TGT001", "IC50")
        assert result["compound_id"] == "CMP001"
        assert result["target_id"] == "TGT001"
        assert result["assay_type"] == "IC50"
        assert result["parsed_value"] == 5.2
        assert result["value_molar"] == pytest.approx(5.2e-6)
        assert result["pactivity"] == pytest.approx(-math.log10(5.2e-6))
        assert result["flags"] == ""

    def test_operator_row(self):
        result = clean_assay_row(">100", "uM")
        assert result["parsed_value"] == 100.0
        assert result["operator"] == ">"
        assert result["value_molar"] == pytest.approx(100e-6)
        assert "above_limit" in result["flags"]

    def test_unparseable_row(self):
        result = clean_assay_row("invalid_value", "mM")
        assert result["parsed_value"] is None
        assert result["value_molar"] is None
        assert "unparseable_value" in result["flags"]

    def test_unknown_unit(self):
        result = clean_assay_row(1.0, "furlongs")
        assert result["parsed_value"] == 1.0
        assert result["value_molar"] is None
        assert "unknown_unit" in result["flags"]

    def test_empty_value(self):
        result = clean_assay_row("", "uM")
        assert result["parsed_value"] is None
        assert result["value_molar"] is None
        assert "unparseable_value" in result["flags"]

    def test_default_ids(self):
        result = clean_assay_row(1.0, "nM")
        assert result["compound_id"] == ""
        assert result["target_id"] == ""
        assert result["assay_type"] == ""


# --------------------------------------------------------------------------- #
# clean_assay_table
# --------------------------------------------------------------------------- #

class TestCleanAssayTable:
    """Tests for clean_assay_table function."""

    def test_full_table(self):
        df = pd.DataFrame({
            "compound_id": ["CMP001", "CMP002"],
            "target_id": ["TGT001", "TGT001"],
            "assay_type": ["IC50", "EC50"],
            "value": ["5.2", ">100"],
            "unit": ["uM", "uM"],
        })
        result = clean_assay_table(df)
        assert len(result) == 2
        assert result.iloc[0]["value_molar"] == pytest.approx(5.2e-6)
        assert result.iloc[1]["operator"] == ">"
        assert "above_limit" in result.iloc[1]["flags"]

    def test_custom_column_names(self):
        df = pd.DataFrame({
            "cpd": ["CMP001"],
            "tgt": ["TGT002"],
            "type": ["Kd"],
            "measurement": ["0.8"],
            "units": ["uM"],
        })
        result = clean_assay_table(
            df,
            value_col="measurement",
            unit_col="units",
            compound_col="cpd",
            target_col="tgt",
            assay_col="type",
        )
        assert len(result) == 1
        assert result.iloc[0]["compound_id"] == "CMP001"
        assert result.iloc[0]["value_molar"] == pytest.approx(0.8e-6)

    def test_mixed_validity(self):
        df = pd.DataFrame({
            "compound_id": ["CMP001", "CMP002", "CMP003"],
            "value": ["5.2", "invalid", ""],
            "unit": ["uM", "mM", "uM"],
        })
        result = clean_assay_table(df, target_col=None, assay_col=None)
        assert len(result) == 3
        assert result.iloc[0]["value_molar"] is not None
        assert pd.isna(result.iloc[1]["value_molar"])
        assert pd.isna(result.iloc[2]["value_molar"])

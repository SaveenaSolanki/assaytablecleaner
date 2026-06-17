"""Tests for assaytablecleaner CLI."""

import pytest
from typer.testing import CliRunner

from assaytablecleaner.cli import app

runner = CliRunner()


def test_help():
    """Test that --help runs and shows expected content."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "assay-clean" in result.stdout
    assert "clean" in result.stdout


def test_clean_help():
    """Test that clean --help shows options."""
    result = runner.invoke(app, ["clean", "--help"])
    assert result.exit_code == 0
    assert "--input" in result.stdout
    assert "--out" in result.stdout
    assert "--value-col" in result.stdout
    assert "--unit-col" in result.stdout


def test_version():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "assay-clean" in result.stdout


def test_clean_file_not_found():
    """Test clean with non-existent file."""
    result = runner.invoke(app, ["clean", "--input", "/nonexistent/file.csv"])
    assert result.exit_code != 0


def test_clean_valid_csv(tmp_path):
    """Test clean with a valid CSV file."""
    import os

    import pandas as pd

    # Create a temporary CSV
    input_path = tmp_path / "test_input.csv"
    df = pd.DataFrame({
        "compound_id": ["CMP001", "CMP002"],
        "target_id": ["TGT001", "TGT002"],
        "assay_type": ["IC50", "EC50"],
        "value": ["5.2", "120"],
        "unit": ["uM", "nM"],
    })
    df.to_csv(input_path, index=False)

    output_path = tmp_path / "out.csv"
    result = runner.invoke(app, [
        "clean",
        "--input", str(input_path),
        "--out", str(output_path),
        "--no-console",
    ])
    assert result.exit_code == 0
    assert os.path.exists(output_path)

    # Verify output
    out_df = pd.read_csv(output_path)
    assert len(out_df) == 2
    assert "value_molar" in out_df.columns
    assert "pactivity" in out_df.columns
    assert out_df.loc[0, "value_molar"] == pytest.approx(5.2e-6)

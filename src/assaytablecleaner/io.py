"""I/O utilities for reading and writing assay tables."""

import os

import pandas as pd


def read_csv(filepath: str, **kwargs) -> pd.DataFrame:
    """Read a CSV file into a DataFrame with default settings.

    Args:
        filepath: Path to the CSV file.
        **kwargs: Additional arguments passed to pd.read_csv.

    Returns:
        pandas DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")
    return pd.read_csv(filepath, **kwargs)


def write_csv(df: pd.DataFrame, filepath: str, **kwargs) -> str:
    """Write a DataFrame to CSV, creating parent directories as needed.

    Args:
        df: DataFrame to write.
        filepath: Output file path.
        **kwargs: Additional arguments passed to df.to_csv.

    Returns:
        The output filepath.
    """
    parent_dir = os.path.dirname(filepath)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    defaults = {"index": False}
    defaults.update(kwargs)
    df.to_csv(filepath, **defaults)
    return filepath

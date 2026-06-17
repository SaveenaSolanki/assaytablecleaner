"""Typer CLI for assay table cleaning."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from assaytablecleaner.core import clean_assay_table
from assaytablecleaner.io import read_csv, write_csv

app = typer.Typer(
    name="assay-clean",
    help="Parse, standardize, and convert bioassay measurement values.",
)
console = Console()


@app.command()
def clean(
    input: Path = typer.Option(
        ..., "--input", "-i", exists=True, dir_okay=False, readable=True,
        help="Input CSV file with assay measurements.",
    ),
    output: Path = typer.Option(
        None, "--out", "-o",
        help="Output CSV file path. "
             "If not given, writes to <input_stem>_cleaned.csv.",
    ),
    value_col: str = typer.Option(
        "value", "--value-col",
        help="Column name for measurement values.",
    ),
    unit_col: str = typer.Option(
        "unit", "--unit-col",
        help="Column name for units.",
    ),
    compound_col: str = typer.Option(
        "compound_id", "--compound-col",
        help="Column name for compound IDs.",
    ),
    target_col: str = typer.Option(
        "target_id", "--target-col",
        help="Column name for target IDs.",
    ),
    assay_col: str = typer.Option(
        "assay_type", "--assay-col",
        help="Column name for assay types.",
    ),
    no_console: bool = typer.Option(
        False, "--no-console",
        help="Suppress rich console output.",
    ),
):
    """Clean a bioassay measurement table: parse values, standardize units,
    convert to molar, compute pActivity, and flag issues.
    """
    # Determine output path
    if output is None:
        output = input.parent / f"{input.stem}_cleaned.csv"

    # Read input
    try:
        df = read_csv(str(input))
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error reading CSV:[/red] {e}")
        raise typer.Exit(code=1)

    # Validate required columns exist
    required_cols = [value_col, unit_col]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        console.print(
            f"[red]Error:[/red] Missing required columns: "
            f"{', '.join(missing)}"
        )
        console.print(f"Available columns: {', '.join(df.columns)}")
        raise typer.Exit(code=1)

    # Clean the table
    console.print(
        f"[bold]Input:[/bold] {input} "
        f"([green]{len(df)} rows[/green])"
    )
    cleaned = clean_assay_table(
        df,
        value_col=value_col,
        unit_col=unit_col,
        compound_col=compound_col,
        target_col=target_col,
        assay_col=assay_col,
    )

    # Write output
    write_csv(cleaned, str(output))
    console.print(
        f"[bold]Output:[/bold] {output} "
        f"([green]{len(cleaned)} rows[/green])"
    )

    # Summary stats
    total = len(cleaned)
    parsed = cleaned["parsed_value"].notna().sum()
    converted = cleaned["value_molar"].notna().sum()
    with_pactivity = cleaned["pactivity"].notna().sum()
    flagged = (cleaned["flags"] != "").sum()
    has_operators = (
        cleaned["operator"].notna().sum()
        if "operator" in cleaned.columns
        else 0
    )

    if not no_console:
        def _pct(n: int) -> str:
            return f"{n / total * 100:.1f}%" if total else "—"

        table = Table(title="Cleaning Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Percent", style="yellow")

        table.add_row("Total rows", str(total), "—")
        table.add_row("Values parsed", str(parsed), _pct(parsed))
        table.add_row("Converted to molar", str(converted), _pct(converted))
        table.add_row(
            "pActivity computed", str(with_pactivity), _pct(with_pactivity)
        )
        table.add_row("Rows flagged", str(flagged), _pct(flagged))
        table.add_row(
            "Has operators", str(has_operators), _pct(has_operators)
        )

        console.print(table)

        # Show flagged rows if any
        if flagged > 0:
            console.print(
                "\n[bold yellow]Flagged rows:[/bold yellow]"
            )
            flag_table = Table(
                title="Flagged Measurements", show_lines=False
            )
            flag_table.add_column("Row", style="dim")
            flag_table.add_column("Compound", style="cyan")
            flag_table.add_column("Value", style="white")
            flag_table.add_column("Unit", style="magenta")
            flag_table.add_column("Flags", style="yellow")

            for idx, row in cleaned.iterrows():
                if row["flags"]:
                    flag_table.add_row(
                        str(idx),
                        str(row.get("compound_id", "")),
                        str(row.get("raw_value", "")),
                        str(row.get("raw_unit", "")),
                        str(row["flags"]),
                    )

            console.print(flag_table)


@app.command()
def version():
    """Print version and exit."""
    from assaytablecleaner import __version__
    console.print(f"assay-clean v{__version__}")


if __name__ == "__main__":
    app()

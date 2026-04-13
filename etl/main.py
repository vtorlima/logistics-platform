"""
ETL pipeline entry point.

Usage:
    python -m etl.main path/to/VCTrans_2026-01.xlsx
    python -m etl.main path/to/seed/output/
"""

import sys
from pathlib import Path

from etl.reader import read_workbook
from etl.transformer import transform
from etl.loader import load
from etl.connection import get_connection


def _extract_month(path: Path) -> str:
    """
    Extract the month string from the filename.
    e.g. VCTrans_2026-01.xlsx → '2026-01'
    Raises ValueError if the filename doesn't match the expected pattern.
    """
    stem = path.stem  # 'VCTrans_2026-01'
    parts = stem.split("_")
    if len(parts) < 2:
        raise ValueError(
            f"Cannot extract month from filename '{path.name}'. "
            "Expected format: VCTrans_YYYY-MM.xlsx"
        )
    month = parts[-1]  # '2026-01'
    # Basic validation
    if len(month) != 7 or month[4] != "-":
        raise ValueError(f"Month '{month}' extracted from '{path.name}' is not in YYYY-MM format.")
    return month


def _resolve_files(target: str) -> list[Path]:
    """
    Return a sorted list of XLSX files to process.
    target can be a single .xlsx file or a directory.
    """
    p = Path(target)
    if p.is_file():
        if p.suffix.lower() != ".xlsx":
            raise ValueError(f"'{target}' is not an XLSX file.")
        return [p]
    elif p.is_dir():
        files = sorted(p.glob("VCTrans_*.xlsx"))
        if not files:
            raise FileNotFoundError(f"No VCTrans_*.xlsx files found in '{target}'.")
        return files
    else:
        raise FileNotFoundError(f"'{target}' does not exist.")


def run(target: str):
    """
    Run the full ETL pipeline for all XLSX files at target path.
    Opens one database connection shared across all files.
    """
    files = _resolve_files(target)
    print(f"Files to process: {len(files)}")
    for f in files:
        print(f"  {f.name}")

    conn = get_connection()
    print(f"\nConnected to database.")

    total_counts: dict[str, int] = {}

    try:
        for xlsx_path in files:
            month = _extract_month(xlsx_path)
            print(f"\n=== {month} ({xlsx_path.name}) ===")

            # Extract
            raw = read_workbook(str(xlsx_path))

            # Transform
            clean = transform(raw, month)

            # Load
            counts = load(clean, conn)

            # Accumulate totals
            for table, n in counts.items():
                total_counts[table] = total_counts.get(table, 0) + n

    finally:
        conn.close()

    # Summary
    print("\n=== Summary ===")
    for table, n in total_counts.items():
        print(f"  {table}: {n} rows total")
    print("\nETL complete.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m etl.main <path-to-xlsx-or-directory>")
        sys.exit(1)

    target = sys.argv[1]
    try:
        run(target)
    except (FileNotFoundError, ValueError, EnvironmentError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

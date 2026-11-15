"""Preview module for inspecting generated or input datasets.

Prints the first N rows of a dataset tabularly, along with basic metadata
(shape, columns, memory usage).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core import registry


def run(context: registry.Context) -> int:
    """CLI entry point for the 'preview' command."""
    input_path = Path(context.args.input)
    rows = int(getattr(context.args, "rows", 10))

    if not input_path.is_file():
        print(f"[preview] error: input file not found: {input_path}")
        return 1

    try:
        df = pd.read_csv(input_path, nrows=rows)
        total_rows = sum(1 for _ in open(input_path, mode="r", encoding="utf-8", errors="ignore")) - 1
    except Exception as exc:
        print(f"[preview] error reading CSV: {exc}")
        return 2

    print(f"\n[preview] File: {input_path.name}")
    print(f"          Total rows: {total_rows:,} | Columns: {len(df.columns)}")
    print(f"          Showing first {min(rows, len(df))} rows:\n")

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 160)
    print(df.to_string(index=False))
    print()
    return 0

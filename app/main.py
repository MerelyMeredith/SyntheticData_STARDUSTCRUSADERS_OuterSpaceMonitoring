"""Terminal interface for the STARDUST CRUSADERS synthetic-data pipeline.

This is the entry point the user runs. It parses arguments (or shows an
interactive menu) and dispatches each command to a future module under
``app/modules`` via :mod:`app.core.registry`. Run it from the project root::

    python app/main.py
    python app/main.py info
    python app/main.py generate --records 1000 --output output/dataset.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core import paths, registry  # noqa: E402

BANNER = "STARDUST CRUSADERS  |  Synthetic Health Data Generator"


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} GB"


def _list_dir(directory: Path, pattern: str = "*") -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob(pattern) if p.is_file())


def command_info(context: registry.Context) -> int:
    """Show data sources, module status, config and output files."""
    print(BANNER)
    print("=" * len(BANNER))

    print("\nData sources (dataSources/):")
    sources = _list_dir(context.data_dir, "*.csv")
    if not sources:
        print("  (none found)")
    for path in sources:
        print(f"  - {path.name:<55} {_human_size(path.stat().st_size)}")

    print("\nModules (app/modules/):")
    for name, help_text in registry.MODULE_COMMANDS.items():
        status = "ready" if registry.module_available(name) else "pending"
        print(f"  [{status:^7}] {name:<10} {help_text}")

    print("\nConfiguration (config/):")
    configs = _list_dir(context.config_dir, "*.json")
    print("  (none yet)" if not configs else "")
    for path in configs:
        print(f"  - {path.name}")

    print("\nOutput (output/):")
    outputs = _list_dir(context.output_dir)
    print("  (none yet)" if not outputs else "")
    for path in outputs:
        print(f"  - {path.name:<45} {_human_size(path.stat().st_size)}")

    patients_dir = context.output_dir / "patients"
    if patients_dir.is_dir():
        patient_files = _list_dir(patients_dir, "*.csv")
        print(f"  - patients/ ({len(patient_files)} individual user files)")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stardust",
        description="Synthetic health-data generator (vitals + retinal + fitness + sleep).",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="show tracebacks on error")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("info", help="list data sources, modules, config and output")

    generate = sub.add_parser("generate", help="generate longitudinal synthetic patient data")
    generate.add_argument("-n", "--records", type=int, default=1000, help="target total observation rows")
    generate.add_argument("-p", "--patients", type=int, default=None, help="number of distinct patient users")
    generate.add_argument("-d", "--days", type=int, default=None, help="days across time per patient")
    generate.add_argument("-o", "--output", default=str(paths.OUTPUT_DIR / "dataset.csv"), help="consolidated CSV output")
    generate.add_argument("--patients-dir", default=str(paths.OUTPUT_DIR / "patients"), help="directory for individual patient files")
    generate.add_argument("--config", default=None, help="path to config JSON")

    configure = sub.add_parser("configure", help="write config/*.json causal parameters")
    configure.add_argument(
        "-o", "--output", default=str(paths.CONFIG_DIR / "synthetic_data_config.json")
    )

    validate = sub.add_parser("validate", help="audit a generated dataset")
    validate.add_argument("-i", "--input", required=True, help="dataset CSV to validate")
    validate.add_argument("-r", "--report", default=str(paths.OUTPUT_DIR / "validation_report.md"))

    preview = sub.add_parser("preview", help="print the first rows of a dataset")
    preview.add_argument("-i", "--input", required=True, help="dataset CSV to preview")
    preview.add_argument("-n", "--rows", type=int, default=10)

    return parser


def _interactive() -> int:
    while True:
        print()
        print("=" * 56)
        print(f"  {BANNER}")
        print("=" * 56)
        print("  1) info       list data sources, modules and outputs")
        print("  2) configure  write config/*.json parameters")
        print("  3) generate   generate a synthetic dataset")
        print("  4) validate   audit a dataset")
        print("  5) preview    show the first rows of a dataset")
        print("  q) quit")
        choice = input("\nselect an option: ").strip().lower()

        if choice in {"q", "quit", "exit"}:
            return 0
        if choice in {"1", "info"}:
            return command_info(
                registry.Context(command="info", args=argparse.Namespace(verbose=False))
            )
        if choice in {"2", "configure"}:
            output = input(f"output path [{paths.CONFIG_DIR / 'synthetic_data_config.json'}]: ").strip()
            args = argparse.Namespace(
                output=output or str(paths.CONFIG_DIR / "synthetic_data_config.json")
            )
            return registry.dispatch(registry.Context(command="configure", args=args))
        if choice in {"3", "generate"}:
            records = input("number of target records [1000]: ").strip()
            patients = input("number of patients (leave empty for auto): ").strip()
            days = input("days across time (leave empty for auto): ").strip()
            output = input(f"output path [{paths.OUTPUT_DIR / 'dataset.csv'}]: ").strip()
            args = argparse.Namespace(
                records=int(records) if records else 1000,
                patients=int(patients) if patients else None,
                days=int(days) if days else None,
                output=output or str(paths.OUTPUT_DIR / "dataset.csv"),
                patients_dir=str(paths.OUTPUT_DIR / "patients"),
                config=None,
            )
            return registry.dispatch(registry.Context(command="generate", args=args))
        if choice in {"4", "validate"}:
            input_path = input("dataset CSV to validate: ").strip()
            args = argparse.Namespace(
                input=input_path,
                report=str(paths.OUTPUT_DIR / "validation_report.md"),
            )
            return registry.dispatch(registry.Context(command="validate", args=args))
        if choice in {"5", "preview"}:
            input_path = input("dataset CSV to preview: ").strip()
            rows = input("rows [10]: ").strip()
            args = argparse.Namespace(
                input=input_path, rows=int(rows) if rows else 10
            )
            return registry.dispatch(registry.Context(command="preview", args=args))

        print(f"unknown option: {choice!r}")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if not argv:
        return _interactive()

    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "info":
        return command_info(registry.Context(command="info", args=args, verbose=args.verbose))

    return registry.dispatch(
        registry.Context(command=args.command, args=args, verbose=args.verbose)
    )


if __name__ == "__main__":
    raise SystemExit(main())

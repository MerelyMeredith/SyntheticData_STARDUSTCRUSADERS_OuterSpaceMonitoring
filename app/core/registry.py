"""Command registry that connects CLI commands to future modules.

Contract: every ``app/modules/<command>.py`` must expose ``run(context) -> int``
where ``context`` is a :class:`Context` and the return value is a process exit
code (0 = success). Modules are imported lazily so the CLI works before they
exist.
"""

from __future__ import annotations

import argparse
import importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from . import paths

MODULE_PACKAGE = "app.modules"

MODULE_COMMANDS: dict[str, str] = {
    "configure": "Build config/*.json causal parameters (data-configurator).",
    "generate": "Generate the synthetic patient dataset (data-synthesizer).",
    "validate": "Audit a dataset and write a validation report (data-validator).",
    "preview": "Print the first N rows of a dataset.",
}


@dataclass
class Context:
    """Shared state handed to every module's ``run`` function."""

    command: str
    args: argparse.Namespace
    project_root: Path = field(default_factory=lambda: paths.PROJECT_ROOT)
    data_dir: Path = field(default_factory=lambda: paths.DATA_DIR)
    config_dir: Path = field(default_factory=lambda: paths.CONFIG_DIR)
    output_dir: Path = field(default_factory=lambda: paths.OUTPUT_DIR)
    verbose: bool = False


def module_path(command: str) -> Path:
    """Return the expected file for a command's module."""
    return paths.MODULES_DIR / f"{command}.py"


def module_available(command: str) -> bool:
    """True when the command's module file exists on disk."""
    return module_path(command).is_file()


def load_module(command: str):
    """Import ``app.modules.<command>`` or raise :class:`ModuleNotFoundError`."""
    return importlib.import_module(f"{MODULE_PACKAGE}.{command}")


def dispatch(context: Context) -> int:
    """Run the module for ``context.command`` and return its exit code."""
    command = context.command

    if not module_available(command):
        print(
            f"[pending] module '{MODULE_PACKAGE}.{command}' is not implemented yet.\n"
            f"          expected file: {module_path(command)}"
        )
        return 2

    try:
        module = load_module(command)
    except Exception as error:  # pragma: no cover - surfaced to the user
        print(f"[error] could not import {MODULE_PACKAGE}.{command}: {error}")
        return 3

    run = getattr(module, "run", None)
    if not callable(run):
        print(
            f"[error] {MODULE_PACKAGE}.{command} must define run(context) -> int"
        )
        return 4

    try:
        return int(run(context))
    except Exception as error:  # pragma: no cover - surfaced to the user
        print(f"[error] {command} failed: {error}")
        if context.verbose:
            import traceback

            traceback.print_exc()
        return 5

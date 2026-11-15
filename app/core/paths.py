"""Canonical filesystem locations used by the CLI and its future modules."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_ROOT / "app"
CORE_DIR = APP_DIR / "core"
MODULES_DIR = APP_DIR / "modules"
DATA_DIR = PROJECT_ROOT / "dataSources"
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_DIR = PROJECT_ROOT / "output"


def ensure_dir(path: Path) -> Path:
    """Create ``path`` (and parents) if needed and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path

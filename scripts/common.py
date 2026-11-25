"""Shared helpers for the site scripts."""

from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data"
SCHEMAS = ROOT / "schemas"
PHOTOS = ROOT / "photos"
IMAGES = ROOT / "assets" / "images"

PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class DuplicateKeyError(yaml.MarkedYAMLError):
    pass


class StrictLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate keys instead of silently keeping the last one."""


def _construct_mapping(loader: StrictLoader, node: yaml.MappingNode, deep: bool = False):
    seen = {}
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise DuplicateKeyError(
                "while constructing a mapping", node.start_mark,
                f"found duplicate key {key!r}", key_node.start_mark,
            )
        seen[key] = True
    return loader.construct_mapping(node, deep=deep)


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as f:
        return yaml.load(f, Loader=StrictLoader)


def dates_to_str(obj):
    """YAML turns 2027-06-14 into a date object; JSON Schema expects strings."""
    if isinstance(obj, (dt.date, dt.datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: dates_to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [dates_to_str(v) for v in obj]
    return obj


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def report(level: str, message: str, file: Path | None = None, line: int | None = None) -> None:
    """Print a message; inside GitHub Actions, as an annotation shown on the PR."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        loc = ""
        if file is not None:
            loc = f" file={rel(file)}" + (f",line={line}" if line else "")
        print(f"::{level}{loc}::{message}")
    else:
        where = f"{rel(file)}{':' + str(line) if line else ''}: " if file is not None else ""
        print(f"{level.upper()}: {where}{message}")

"""Shared helpers for the site scripts."""

from __future__ import annotations

import datetime as dt
import os
from collections.abc import Hashable
from pathlib import Path
from typing import NotRequired, TypedDict, cast

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


def _construct_mapping(
    loader: StrictLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Hashable, object]:
    # PyYAML's type stubs leave node contents and marks as Any
    pairs = cast(list[tuple[yaml.Node, yaml.Node]], node.value)
    seen: set[object] = set()
    for key_node, _ in pairs:
        key: object = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise DuplicateKeyError(
                "while constructing a mapping",
                cast(yaml.Mark, node.start_mark),
                f"found duplicate key {key!r}",
                cast(yaml.Mark, key_node.start_mark),
            )
        seen.add(key)
    return loader.construct_mapping(node, deep=deep)


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def load_yaml(path: Path) -> object:
    """Parse a YAML file. The result is unchecked: see load_event/load_committee."""
    with path.open(encoding="utf-8") as f:
        data: object = yaml.load(f, Loader=StrictLoader)
    return data


# Typed views of the data files, covering only the fields the scripts use.
# The full rules are in schemas/*.schema.json.


class HeaderImage(TypedDict):
    photo: str
    focus: NotRequired[list[float]]


class Event(TypedDict, total=False):
    start_date: dt.date | None
    end_date: dt.date | None
    header_image: HeaderImage | None


class Role(TypedDict):
    id: str
    title: str
    multiple: NotRequired[bool]


class Member(TypedDict):
    id: str
    name: str
    affiliation: str
    roles: list[str]
    photo: NotRequired[str]
    photo_focus: NotRequired[list[float]]


class Committee(TypedDict):
    roles: list[Role]
    members: list[Member]


# The casts below are safe only because scripts/validate.py checks the files
# against the schemas first (make and CI always run it before other scripts).


def load_event() -> Event:
    data = load_yaml(DATA / "event.yml")
    return cast(Event, data if data is not None else {})  # an empty file is allowed


def load_committee() -> Committee:
    return cast(Committee, load_yaml(DATA / "committee.yml"))


def dates_to_str(obj: object) -> object:
    """YAML turns 2027-06-14 into a date object; JSON Schema expects strings."""
    if isinstance(obj, (dt.date, dt.datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        items = cast(dict[object, object], obj).items()
        return {k: dates_to_str(v) for k, v in items}
    if isinstance(obj, list):
        return [dates_to_str(v) for v in cast(list[object], obj)]
    return obj


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def report(
    level: str, message: str, file: Path | None = None, line: int | None = None
) -> None:
    """Print a message; inside GitHub Actions, as an annotation shown on the PR."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        loc = ""
        if file is not None:
            loc = f" file={rel(file)}" + (f",line={line}" if line is not None else "")
        print(f"::{level}{loc}::{message}")
    else:
        where = (
            f"{rel(file)}{':' + str(line) if line is not None else ''}: "
            if file is not None
            else ""
        )
        print(f"{level.upper()}: {where}{message}")

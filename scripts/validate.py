#!/usr/bin/env python3
"""Check the site's data files before building.

Catches the errors that broke last year's site: invalid YAML, duplicate keys,
misspelt or missing fields, IDs that are reused or don't match, and references
to files that do not exist.

Usage: python scripts/validate.py      (exit status 1 if anything is wrong)
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple, cast

import yaml
from common import (
    DATA,
    PHOTO_EXTENSIONS,
    PHOTOS,
    SCHEMAS,
    Event,
    dates_to_str,
    load_yaml,
    report,
)
from jsonschema import Draft202012Validator

MAX_PHOTO_MB = 15

errors = 0
warnings = 0
_FAILED = object()


def error(msg: str, file: Path | None = None, line: int | None = None) -> None:
    global errors
    errors += 1
    report("error", msg, file, line)


def warning(msg: str, file: Path | None = None) -> None:
    global warnings
    warnings += 1
    report("warning", msg, file)


def load(path: Path) -> object:
    """Parse a YAML file, returning _FAILED (after reporting) if it is invalid."""
    try:
        return load_yaml(path)
    except yaml.MarkedYAMLError as e:
        mark = e.problem_mark if e.problem_mark is not None else e.context_mark
        error(
            f"invalid YAML: {e.problem if e.problem is not None else e.context}",
            path,
            mark.line + 1 if mark is not None else None,
        )
    except yaml.YAMLError as e:
        error(f"invalid YAML: {e}", path)
    return _FAILED


def as_dict(value: object) -> dict[object, object]:
    """value if it is a mapping, else an empty one (for data not yet known to be valid)."""
    return cast(dict[object, object], value) if isinstance(value, dict) else {}


def as_list(value: object) -> list[object]:
    """value if it is a list, else an empty one (for data not yet known to be valid)."""
    return cast(list[object], value) if isinstance(value, list) else []


def describe_path(data: object, path: Sequence[str | int]) -> str:
    """members.3.name -> 'members[4] (jane-doe).name' so people can find the entry."""
    out: list[str] = []
    node = data
    for p in path:
        is_list = isinstance(node, list)  # (not narrowed inline: node stays `object`)
        if isinstance(p, int) and is_list:
            items = as_list(node)
            item = items[p] if p < len(items) else None
            label = as_dict(item).get("id")
            prefix = out[-1] if len(out) > 0 else ""
            suffix = f" ({label})" if label is not None else ""
            out[-1:] = [f"{prefix}[{p + 1}]{suffix}"]
            node = item
        else:
            out.append(str(p))
            node = as_dict(node).get(p)
    return ".".join(out) if len(out) > 0 else "(top level)"


class SchemaError(NamedTuple):
    path: list[str | int]
    message: str
    validator: str
    instance: object


def _where(e: SchemaError) -> list[str]:
    return [str(p) for p in e.path]


def schema_errors(data: object, schema_name: str) -> list[SchemaError]:
    """The schema violations in data, sorted by where they occur."""
    schema = cast(dict[str, object], json.loads((SCHEMAS / schema_name).read_text()))
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,  # pyrefly: ignore[explicit-any-use]
    )
    # jsonschema types most of its results as Any; this is the only place they are used.
    found = [
        SchemaError(list(e.absolute_path), e.message, str(e.validator), e.instance)  # pyrefly: ignore[explicit-any-use]
        for e in validator.iter_errors(dates_to_str(data))  # pyrefly: ignore[explicit-any-use, partially-unknown-type]
    ]
    return sorted(found, key=_where)


def check_schema(data: object, schema_name: str, path: Path) -> bool:
    found = schema_errors(data, schema_name)
    for e in found:
        msg = e.message
        if e.validator == "additionalProperties":
            msg += " - check the spelling of the field name"
        elif e.validator == "pattern" and len(e.path) > 0 and e.path[-1] == "id":
            msg = f"id {e.instance!r} must be lowercase letters, digits and single hyphens, e.g. jane-doe"
        error(f"{describe_path(data, e.path)}: {msg}", path)
    return len(found) == 0


def check_photo(owner: str, photo: str, folder: Path, data_file: Path) -> None:
    file = folder / photo
    if Path(photo).suffix.lower() not in PHOTO_EXTENSIONS:
        error(
            f"{owner}: photo {photo!r} must be one of {', '.join(sorted(PHOTO_EXTENSIONS))}",
            data_file,
        )
    elif not file.is_file():
        matches = (
            [p.name for p in folder.iterdir() if p.name.lower() == photo.lower()]
            if folder.is_dir()
            else []
        )
        hint = (
            f" (did you mean {matches[0]!r}? names are case-sensitive)"
            if len(matches) > 0
            else ""
        )
        error(
            f"{owner}: photo {photo!r} not found in {folder.relative_to(PHOTOS.parent)}/{hint}",
            data_file,
        )
    elif file.stat().st_size > MAX_PHOTO_MB * 1024 * 1024:
        warning(
            f"{owner}: {photo} is over {MAX_PHOTO_MB} MB; consider downsizing the original before committing",
            file,
        )


def check_unused_photos(folder: Path, used: set[str]) -> None:
    if folder.is_dir():
        for p in sorted(folder.iterdir()):
            if not p.name.startswith(".") and p.name not in used:
                warning(f"photo not used anywhere: {p.name}", p)


def check_event() -> None:
    path = DATA / "event.yml"
    data = load(path)
    if data is _FAILED:
        return
    if data is None:  # an empty file
        data = dict[str, object]()
    if not check_schema(data, "event.schema.json", path):
        return
    event = cast(Event, data)  # safe now that it matches the schema
    start, end = event.get("start_date"), event.get("end_date")
    if start is not None and end is not None and end < start:
        error(f"end_date {end} is before start_date {start}", path)
    if (start is None) != (end is None):
        warning("only one of start_date/end_date is set", path)
    used: set[str] = set()
    header_image = event.get("header_image")
    if header_image is not None:
        photo = header_image["photo"]
        used.add(photo)
        check_photo("header_image", photo, PHOTOS / "site", path)
    check_unused_photos(PHOTOS / "site", used)


def check_committee() -> None:
    path = DATA / "committee.yml"
    data = load(path)
    if data is _FAILED:
        return
    if data is None:  # an empty file
        data = dict[str, object]()
    check_schema(data, "committee.schema.json", path)
    # Carry on after schema errors so everything wrong is reported in one go,
    # so the data can't be trusted to match the schema here. Entries too
    # malformed to check further (not a mapping, or no string id) are skipped.
    top = as_dict(data)

    def entries(key: str) -> list[tuple[str, dict[object, object]]]:
        found: list[tuple[str, dict[object, object]]] = []
        for x in as_list(top.get(key)):
            entry = as_dict(x)
            if isinstance(entry_id := entry.get("id"), str):
                found.append((entry_id, entry))
        return found

    roles: dict[str, dict[object, object]] = {}
    for rid, r in entries("roles"):
        if rid in roles:
            error(f"role id {rid!r} is defined more than once", path)
        roles[rid] = r

    members = entries("members")
    if len(members) == 0:
        warning("no committee members listed yet", path)

    seen_ids: set[str] = set()
    used_photos: set[str] = set()
    holders: dict[str, list[str]] = {rid: [] for rid in roles}
    for mid, m in members:
        if mid in seen_ids:
            error(f"member id {mid!r} is used more than once", path)
        seen_ids.add(mid)

        member_roles = [r for r in as_list(m.get("roles")) if isinstance(r, str)]
        if len(set(member_roles)) != len(member_roles):
            error(f"{mid}: a role is listed twice", path)
        for rid in member_roles:
            if rid not in roles:
                error(
                    f"{mid}: unknown role {rid!r}; known roles: {', '.join(roles)}",
                    path,
                )
            else:
                holders[rid].append(mid)

        if isinstance(photo := m.get("photo"), str):
            used_photos.add(photo)
            check_photo(mid, photo, PHOTOS / "committee", path)

    for rid, people in holders.items():
        if roles[rid].get("multiple", True) is False and len(people) > 1:
            error(
                f"role {rid!r} allows one person but has {len(people)}: {', '.join(people)}",
                path,
            )

    check_unused_photos(PHOTOS / "committee", used_photos)


def main() -> int:
    check_event()
    check_committee()
    print(f"validate: {errors} error(s), {warnings} warning(s)")
    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Check the site's data files before building.

Catches the errors that broke last year's site: invalid YAML, duplicate keys,
misspelt or missing fields, IDs that are reused, and references to files that
do not exist.

Usage: python scripts/validate.py      (exit status 1 if anything is wrong)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from common import DATA, PHOTO_EXTENSIONS, PHOTOS, SCHEMAS, dates_to_str, load_yaml, report

MAX_PHOTO_MB = 15

errors = 0
warnings = 0


def error(msg: str, file: Path | None = None, line: int | None = None) -> None:
    global errors
    errors += 1
    report("error", msg, file, line)


def warning(msg: str, file: Path | None = None) -> None:
    global warnings
    warnings += 1
    report("warning", msg, file)


_FAILED = object()


def load(path: Path):
    """Parse a YAML file, returning _FAILED (after reporting) if it is invalid."""
    try:
        return load_yaml(path)
    except yaml.MarkedYAMLError as e:
        mark = e.problem_mark or e.context_mark
        error(f"invalid YAML: {e.problem or e.context}", path, mark.line + 1 if mark else None)
    except yaml.YAMLError as e:
        error(f"invalid YAML: {e}", path)
    return _FAILED


def check_schema(data, schema_name: str, path: Path) -> bool:
    schema = json.loads((SCHEMAS / schema_name).read_text())
    validator = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
    ok = True
    for e in sorted(validator.iter_errors(dates_to_str(data)), key=lambda e: list(e.absolute_path)):
        ok = False
        parts = list(e.absolute_path)
        if parts and isinstance(parts[0], int) and isinstance(data, list):
            entry = data[parts[0]]
            label = entry.get("id") if isinstance(entry, dict) else None
            parts[0] = f"entry {parts[0] + 1}" + (f" ({label})" if label else "")
        where = ".".join(str(p) for p in parts) or "(top level)"
        msg = e.message
        if e.validator == "additionalProperties":
            msg += " - check the spelling of the field name"
        elif e.validator == "pattern" and e.absolute_path and e.absolute_path[-1] == "id":
            msg = f"id {e.instance!r} must be lowercase letters, digits and single hyphens, e.g. jane-doe"
        error(f"{where}: {msg}", path)
    return ok


def check_event() -> None:
    path = DATA / "event.yml"
    data = load(path)
    if data is _FAILED:
        return
    data = data or {}
    if not check_schema(data, "event.schema.json", path):
        return
    start, end = data.get("start_date"), data.get("end_date")
    if start and end and end < start:
        error(f"end_date {end} is before start_date {start}", path)
    if bool(start) != bool(end):
        warning("only one of start_date/end_date is set", path)


def check_committee() -> None:
    path = DATA / "committee.yml"
    data = load(path)
    if data is _FAILED:
        return
    if not data:
        warning("no committee members listed", path)
        return
    if not check_schema(data, "committee.schema.json", path):
        return

    folder = PHOTOS / "committee"
    seen_ids: set[str] = set()
    used_photos: set[str] = set()
    for m in data:
        mid = m["id"]
        if mid in seen_ids:
            error(f"id {mid!r} is used more than once", path)
        seen_ids.add(mid)

        photo = m.get("photo")
        if not photo:
            continue
        used_photos.add(photo)
        file = folder / photo
        if Path(photo).suffix.lower() not in PHOTO_EXTENSIONS:
            error(f"{mid}: photo {photo!r} must be one of {', '.join(sorted(PHOTO_EXTENSIONS))}", path)
        elif not file.is_file():
            hint = ""
            matches = [p.name for p in folder.iterdir() if p.name.lower() == photo.lower()] if folder.is_dir() else []
            if matches:
                hint = f" (did you mean {matches[0]!r}? names are case-sensitive)"
            error(f"{mid}: photo {photo!r} not found in photos/committee/{hint}", path)
        elif file.stat().st_size > MAX_PHOTO_MB * 1024 * 1024:
            warning(f"{mid}: {photo} is over {MAX_PHOTO_MB} MB; consider downsizing the original before committing", file)

    if folder.is_dir():
        for p in sorted(folder.iterdir()):
            if p.name.startswith(".") or p.name in used_photos:
                continue
            warning(f"photo not used by any committee entry: {p.name}", p)


def main() -> int:
    check_event()
    check_committee()
    print(f"validate: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

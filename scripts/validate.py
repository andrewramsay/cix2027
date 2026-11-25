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
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from common import DATA, PHOTO_EXTENSIONS, PHOTOS, SCHEMAS, dates_to_str, load_yaml, report

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


def describe_path(data, path) -> str:
    """members.3.name -> 'members[4] (jane-doe).name' so people can find the entry."""
    out, node = [], data
    for p in path:
        if isinstance(p, int) and isinstance(node, list):
            item = node[p] if p < len(node) else None
            label = item.get("id") if isinstance(item, dict) else None
            out[-1:] = [f"{out[-1] if out else ''}[{p + 1}]" + (f" ({label})" if label else "")]
            node = item
        else:
            out.append(str(p))
            node = node.get(p) if isinstance(node, dict) else None
    return ".".join(out) or "(top level)"


def check_schema(data, schema_name: str, path: Path) -> bool:
    schema = json.loads((SCHEMAS / schema_name).read_text())
    validator = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
    ok = True
    for e in sorted(validator.iter_errors(dates_to_str(data)), key=lambda e: list(map(str, e.absolute_path))):
        ok = False
        msg = e.message
        if e.validator == "additionalProperties":
            msg += " - check the spelling of the field name"
        elif e.validator == "pattern" and e.absolute_path and e.absolute_path[-1] == "id":
            msg = f"id {e.instance!r} must be lowercase letters, digits and single hyphens, e.g. jane-doe"
        error(f"{describe_path(data, e.absolute_path)}: {msg}", path)
    return ok


def check_photo(owner: str, photo: str, folder: Path, data_file: Path) -> None:
    file = folder / photo
    if Path(photo).suffix.lower() not in PHOTO_EXTENSIONS:
        error(f"{owner}: photo {photo!r} must be one of {', '.join(sorted(PHOTO_EXTENSIONS))}", data_file)
    elif not file.is_file():
        matches = [p.name for p in folder.iterdir() if p.name.lower() == photo.lower()] if folder.is_dir() else []
        hint = f" (did you mean {matches[0]!r}? names are case-sensitive)" if matches else ""
        error(f"{owner}: photo {photo!r} not found in {folder.relative_to(PHOTOS.parent)}/{hint}", data_file)
    elif file.stat().st_size > MAX_PHOTO_MB * 1024 * 1024:
        warning(f"{owner}: {photo} is over {MAX_PHOTO_MB} MB; consider downsizing the original before committing", file)


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
    data = data or {}
    if not check_schema(data, "event.schema.json", path):
        return
    start, end = data.get("start_date"), data.get("end_date")
    if start and end and end < start:
        error(f"end_date {end} is before start_date {start}", path)
    if bool(start) != bool(end):
        warning("only one of start_date/end_date is set", path)
    used = set()
    if data.get("header_image"):
        photo = data["header_image"]["photo"]
        used.add(photo)
        check_photo("header_image", photo, PHOTOS / "site", path)
    check_unused_photos(PHOTOS / "site", used)


def check_committee() -> None:
    path = DATA / "committee.yml"
    data = load(path)
    if data is _FAILED:
        return
    data = data or {}
    check_schema(data, "committee.schema.json", path)
    # Carry on after schema errors so everything wrong is reported in one go;
    # entries too malformed to check further are skipped.
    def entries(key):
        items = data.get(key) if isinstance(data, dict) else None
        return [x for x in items if isinstance(x, dict) and isinstance(x.get("id"), str)] if isinstance(items, list) else []

    roles = {}
    for r in entries("roles"):
        if r["id"] in roles:
            error(f"role id {r['id']!r} is defined more than once", path)
        roles[r["id"]] = r

    members = entries("members")
    if not members:
        warning("no committee members listed yet", path)

    seen_ids: set[str] = set()
    used_photos: set[str] = set()
    holders: dict[str, list[str]] = {rid: [] for rid in roles}
    for m in members:
        mid = m["id"]
        if mid in seen_ids:
            error(f"member id {mid!r} is used more than once", path)
        seen_ids.add(mid)

        member_roles = [r for r in m.get("roles") or [] if isinstance(r, str)] if isinstance(m.get("roles"), list) else []
        if len(set(member_roles)) != len(member_roles):
            error(f"{mid}: a role is listed twice", path)
        for rid in member_roles:
            if rid not in roles:
                error(f"{mid}: unknown role {rid!r}; known roles: {', '.join(roles)}", path)
            else:
                holders[rid].append(mid)

        if isinstance(m.get("photo"), str):
            used_photos.add(m["photo"])
            check_photo(mid, m["photo"], PHOTOS / "committee", path)

    for rid, people in holders.items():
        if not roles[rid].get("multiple", True) and len(people) > 1:
            error(f"role {rid!r} allows one person but has {len(people)}: {', '.join(people)}", path)

    check_unused_photos(PHOTOS / "committee", used_photos)


def main() -> int:
    check_event()
    check_committee()
    print(f"validate: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

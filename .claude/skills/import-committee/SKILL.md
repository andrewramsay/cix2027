---
name: import-committee
description: Import or re-sync committee members from a spreadsheet (e.g. the organisers' Google Sheet exported as CSV, or pasted rows) into _data/committee.yml, including headshots. Use when someone provides a sheet, CSV or table of committee members and asks to import, seed or update the committee from it.
---

# Import the committee from a spreadsheet

The repo's `_data/committee.yml` is the live version. A spreadsheet is only an
input: never set up anything that pulls from it automatically.

## Getting the data

Google Sheets links usually need a sign-in, so prefer, in order:
1. A CSV file in the request or committed to the branch (File > Download >
   Comma-separated values). Don't leave it in the repo afterwards.
2. Rows pasted into the request.
3. A sheet shared as "Anyone with the link": try
   `curl -sSfL "https://docs.google.com/spreadsheets/d/<sheet-id>/export?format=csv&gid=<gid>"`.
   If that returns HTML or fails, ask for option 1 or 2.

## Mapping

1. Read `_data/committee.yml` first.
2. Show how you are mapping the columns (name, affiliation, role, photo, URL,
   anything ignored) before relying on it; if a column's meaning is unclear, ask.
3. Roles: map each cell's text to existing role ids, case-insensitively and
   allowing obvious variants ("TPC", "Technical Program Chair" →
   `technical-programme-chair`; "PC" → `programme-committee`). A cell may list
   several roles, and a person may appear on several rows: merge them into one
   member with several roles. Don't create new roles without asking; list any
   text you couldn't map.
4. Match people to existing members by `id` (derived from the name as in
   add-committee-member), falling back to a case- and accent-insensitive name
   match. Update changed fields, add new people in sheet order, and never
   change an existing id.
5. People in the file but not in the sheet: keep them and list them in your
   summary. Remove them only if asked.
6. Skip rows with no name; flag rows missing an affiliation or role rather than
   guessing.

## Photos

- A Google Drive link (`.../file/d/<file-id>/...` or `open?id=<file-id>`) can be
  downloaded only if shared publicly:
  `curl -sSfL -o photos/committee/<id>.jpg "https://drive.google.com/uc?export=download&id=<file-id>"`.
  Check the result really is an image (`file photos/committee/<id>.jpg`); Drive
  returns an HTML page when it refuses. Fix the extension if it is a PNG/WebP.
- Other URLs: download the same way.
- Keep originals unchanged; set `photo:` only for files that downloaded. List
  the people whose photos are missing or failed.
- Run `make images` and look at a few generated photos; set `photo_focus` on
  any where the face is badly cropped.

## Finishing

1. Run `make check` (or at least `make validate`) and fix any errors.
2. Commit on a branch ("Import committee from sheet") and open a pull request
   whose description summarises: added, updated (which fields), unchanged,
   in the repo but not the sheet, unmapped roles, missing photos.

---
name: add-committee-member
description: Add, update or remove one or a few committee members, including their roles and photos. Use when someone asks to add a person to the committee, change their details or role, replace their photo, or remove them. For importing many people from a spreadsheet, use import-committee instead.
---

# Add or update a committee member

All committee data is in `_data/committee.yml`: `roles` (the sections of the
/committee/ page, in display order) and `members` (the people).

1. Read `_data/committee.yml`. Within a role, people appear in the order of
   `members`; add new people at the end unless told otherwise.
2. Choose an `id` from the name: lowercase ASCII, hyphen-separated, accents
   removed ("José Núñez-Pérez" → `jose-nunez-perez`). It must be unique.
   Never change an existing person's id.
3. Fill in `name` (as given, accents kept), `affiliation`, and `roles`: a list
   of role ids from `roles` (e.g. `[local-chair, web-chair]`). Map what people
   say to the existing ids ("TPC" → `technical-programme-chair`, "PC member" →
   `programme-committee`). Only add a new role to `roles` if asked; if a role
   is unclear, ask. Add `url` if given. Don't invent details: if something
   required is missing, ask (or, with no one to ask, leave the person out and
   say why).
   Only ever use the role(s) asked for. If one can't be used (e.g. it allows
   one person, `multiple: false`, and is already held), don't put the person
   in a different role instead: make no change, explain why, and ask what to do.
4. Photo, if one was supplied:
   - Save the original unchanged as `photos/committee/<id>.<ext>` (lowercase
     extension). If it is a link (e.g. a GitHub issue attachment), download it:
     `curl -sSfL -o photos/committee/<id>.jpg "<url>"`.
   - Set `photo: <id>.<ext>`.
   - Adding a photo to an existing member who has none works the same way.
   - Replacing a photo: if the old original has the same file name, the new
     one simply overwrites it. Otherwise delete the old original with
     `git rm photos/committee/<old file>` (plain `rm` may not be allowed).
5. Run `make images` and look at `assets/images/generated/committee/<id>.jpg`.
   If the face is cut off, set `photo_focus: [x, y]` (0–1, default
   `[0.5, 0.35]`; lower y moves the crop up) and run again.
6. Removing someone: delete their entry and their original photo (with `git rm`).
7. Run `make check` (or at least `make validate`) and fix any errors.
8. Commit on a branch ("Add Jane Doe to committee as Local Chair") and open a
   pull request.

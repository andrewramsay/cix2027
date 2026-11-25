---
name: add-committee-member
description: Add, update or remove a member of the organising committee, including their photo. Use when someone asks to add a person to the committee, change their details or role, replace their photo, or remove them.
---

# Add or update a committee member

1. Read `_data/committee.yml` to see existing entries and their order. The list
   order is the display order; add new people at the end unless told otherwise.
2. Choose an `id` from the name: lowercase ASCII, hyphen-separated, accents
   removed (e.g. "José Núñez-Pérez" → `jose-nunez-perez`). It must be unique.
   Never change an existing person's id.
3. Fill in `name` (as given, accents kept), `affiliation`, and if provided
   `role` and `url`. Don't invent details: if something required is missing,
   ask for it (or, with no one to ask, leave the person out and say why).
4. Photo, if one was supplied:
   - Save the original unchanged to `photos/committee/<id>.<ext>` (keep its
     extension, lowercase it). If it is a link (e.g. a GitHub issue attachment),
     download it: `curl -sSfL -o photos/committee/<id>.jpg "<url>"`.
   - Set `photo: <id>.<ext>`.
   - Replacing a photo: delete the old original if its name differs.
5. Run `make images` and look at the generated `assets/images/committee/<id>.jpg`.
   If the face is cut off, set `photo_focus: [x, y]` (0–1, default `[0.5, 0.35]`;
   lower y moves the crop up) and run again.
6. Removing someone: delete their entry and their original in `photos/committee/`.
7. Run `make check` (or at least `make validate`) and fix any errors.
8. Commit on a branch with a message like "Add Jane Doe to organising committee"
   and open a pull request.

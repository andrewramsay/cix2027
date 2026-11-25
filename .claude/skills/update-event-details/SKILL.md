---
name: update-event-details
description: Change the event's dates, summer school date, venue, city, contact email or home page banner photo. Use when someone confirms or changes when or where the event takes place, the contact address, or the header image.
---

# Update event details

1. Edit `_data/event.yml`. Dates are `YYYY-MM-DD`; `end_date` must not be before
   `start_date`. Leave a field empty rather than guessing: it then shows as "TBC"
   (the summer school line is hidden until `summer_school_date` is set).
2. If the dates or place also appear in prose (`index.md`, `cfp/index.md`,
   `timetable/index.md`), update those mentions too so nothing contradicts the
   facts block. Search for the old values with grep.
3. Banner photo: put the original in `photos/site/`, set `header_image.photo`,
   delete the old original, then run `make images` and look at
   `assets/images/generated/header.jpg`. Adjust `header_image.focus` if the
   12:5 crop cuts off what matters.
4. If the event moves to another time zone, update `timezone` in `_config.yml`
   (an IANA name such as `Europe/London`).
5. Run `make check` (or at least `make validate`) and fix any errors.
6. Commit on a branch ("Set summer school date to 29 June") and open a pull request.

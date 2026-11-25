---
name: update-event-details
description: Change the event's dates, venue, city, country or contact email shown on the home page. Use when someone confirms or changes when or where the event takes place, or the contact address.
---

# Update event details

1. Edit `_data/event.yml`. Dates are `YYYY-MM-DD`; `end_date` must not be before
   `start_date`. Leave a field empty rather than guessing: it then shows as "TBC".
2. If the dates or place also appear in prose (`index.md`, `cfp/index.md`), update
   those mentions too so nothing contradicts the facts block. Search for the old
   values with grep.
3. If the event moves to another time zone, update `timezone` in `_config.yml`
   (an IANA name such as `Europe/London`).
4. Run `make check` (or at least `make validate`) and fix any errors.
5. Commit on a branch ("Set S³CIX 2027 dates to 14–18 June") and open a pull request.

# CompInt’27 website

Jekyll site for CompInt’27, the ACM Conference on Computational Interaction
(held with the Summer School on Computational Interaction), built on the
[jekyll-theme-conference](https://github.com/DigitaleGesellschaft/jekyll-theme-conference)
gem (pinned to 5.4.x, Bootstrap 5) and deployed to GitHub Pages by `.github/workflows/site.yml`.

The people asking for changes are conference organisers, not necessarily developers.
Keep explanations short and non-technical, and always say what you changed.

## Current scope

A minimal pre-announcement site: a home page (banner photo, dates/location,
intro text), a committee page, a call-for-papers page whose text the organisers
write themselves, and a timetable page showing the outline schedule as a grid.

The timetable uses the theme's programme feature in a simplified way: the two
columns (Conference, Summer school) are "rooms" in `_rooms/`, and each kind of
block (Keynote, Talks, Teaching, …) is one "talk" in `_talks/`, reused in every
time slot it occupies. All are `hide: true`, so they have no pages of their own.
Block colours and the legend are "tracks" in `_config.yml`. There are
deliberately no individual talks or speakers yet (`_speakers/` exists only
because the theme requires it); don't add them unless asked.

## Where things live

| What | File |
|---|---|
| Conference & summer school editions, dates, venue, contact email, banner photo | `_data/event.yml` (schema: `schemas/event.schema.json`) |
| Committee roles and members | `_data/committee.yml` (schema: `schemas/committee.schema.json`) |
| Photo originals | `photos/committee/`, `photos/site/` (banner) |
| Home page text | `index.md` |
| Committee page | `committee/index.md`, rendered by `_includes/committee.html` |
| Timetable intro text and grid settings | `timetable/index.md` |
| Timetable: days (tab labels, e.g. "Wed 30 June"), columns and times of each block | `_data/program.yml` |
| Start time shown in each timetable block (copy of a theme include) | `_includes/show_talk.html` |
| Timetable blocks (name, colour) and columns | `_talks/`, `_rooms/` |
| Timetable colours and legend | `conference.talks.tracks` in `_config.yml` |
| Call for papers | `cfp/index.md` |
| Navigation bar, site title, theme settings | `_config.yml` |
| Custom CSS (incl. the home banner) | `assets/css/main.scss` |

Generated, never edit or commit: `assets/images/generated/` (made by
`scripts/process_images.py` from `photos/`), `_site/`.

Skills: `add-committee-member`, `import-committee` (from a spreadsheet/CSV),
`update-event-details`.

## Rules

- Structured facts go in `_data/*.yml`, not hard-coded into pages. Only add a
  field after adding it to the matching schema in `schemas/`.
- Committee `id`s are lowercase-hyphenated (`jane-doe`) and must stay stable:
  the generated photo is named after the id. Members refer to roles by role id.
- The text of the call for papers and timetable is written by the organisers.
  Only change its wording when asked; formatting fixes are fine.
- Photos: put the original, as received, in `photos/...` and reference it by
  file name. Never resize by hand or put photos in `assets/images/generated/`.
- Don't override theme layouts (`_layouts/`) unless asked; prefer includes and
  page content. If you must, copy the file from the 5.4.x gem and keep the diff small.
- Icons are Bootstrap Icons via `{% include icon.html name="..." %}`, not Font Awesome.
- Don't edit `.github/workflows/` unless asked.

## Checking your work

Run before every commit and fix anything it reports:

```
make check     # validate data, generate images, build the site
```

`make validate` alone is fast and needs only Python. If Ruby/Jekyll is not
available, run at least `make images` and say that the Jekyll build was not run.
For a local preview: `make serve`.

## Git

Work on a branch and open a pull request; never push to `main`. The Site workflow
checks every pull request. Use a short, plain-English commit message describing
the content change (e.g. "Add Jane Doe to organising committee").

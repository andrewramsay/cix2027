# S³CIX 2027 website

Jekyll site for the S³CIX 2027 summer school and symposium, built on the
[jekyll-theme-conference](https://github.com/DigitaleGesellschaft/jekyll-theme-conference)
gem (pinned to 5.4.x, Bootstrap 5) and deployed to GitHub Pages by `.github/workflows/site.yml`.

The people asking for changes are conference organisers, not necessarily developers.
Keep explanations short and non-technical, and always say what you changed.

## Current scope

A minimal pre-announcement site: a home page (logo, dates/location, intro text,
organising committee) and a call-for-participation page. There is deliberately
no programme, talks, speakers or rooms yet; the theme's `_talks/`, `_speakers/`,
`_rooms/` and `_data/program.yml` exist only because the theme requires them.
Don't add those features unless asked.

## Where things live

| What | File |
|---|---|
| Dates, venue, city, contact email | `_data/event.yml` (schema: `schemas/event.schema.json`) |
| Organising committee | `_data/committee.yml` (schema: `schemas/committee.schema.json`) |
| Committee photos, originals | `photos/committee/` |
| Home page text | `index.md` |
| Call for participation | `cfp/index.md` |
| Navigation bar, site title, theme settings | `_config.yml` |
| Custom CSS | `assets/css/main.scss` |
| Home page snippets | `_includes/event_facts.html`, `_includes/committee.html` |

Generated, never edit or commit: `assets/images/committee/` (made by
`scripts/process_images.py` from `photos/`), `_site/`.

## Rules

- Structured facts go in `_data/*.yml`, not hard-coded into pages. Only add a
  field after adding it to the matching schema in `schemas/`.
- Committee `id`s are lowercase-hyphenated (`jane-doe`) and must stay stable:
  the generated photo is named after the id.
- Photos: put the original, as received, in `photos/committee/` and reference
  it by file name. Never resize by hand or put photos in `assets/images/committee/`.
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

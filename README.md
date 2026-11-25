# S³CIX 2027 website

Built with Jekyll and [jekyll-theme-conference](https://github.com/DigitaleGesellschaft/jekyll-theme-conference) 5.4.x,
deployed to GitHub Pages on every push to `main`.

## Making changes

Pick whichever suits you. All of them end in a pull request that is checked automatically;
merge it once the checks pass, and the site updates a minute or two later.

- **Ask Claude in an issue:** open an issue describing the change and include `@claude`,
  e.g. "@claude add Jane Doe (University of Example, Programme Chair) to the committee,
  photo attached". Claude replies in the issue and opens a pull request.
- **Claude Code on the web:** at [claude.ai/code](https://claude.ai/code), pick this
  repository and describe the change.
- **Edit directly on GitHub:** edit the files below in the web editor and choose
  "Create a new branch and start a pull request" when saving.
- **Locally:** `make install` once, then `make serve` to preview at http://localhost:4000.

## What to edit

| To change | Edit |
|---|---|
| Dates, venue, contact email | `_data/event.yml` |
| Organising committee | `_data/committee.yml`, photos in `photos/committee/` |
| Home page text | `index.md` |
| Call for participation | `cfp/index.md` |
| Menu and site title | `_config.yml` |

Photos can be any size: put the original in `photos/committee/` and the build makes
the small web version. If a check fails, the error message names the file and the problem.

`make check` runs the same checks and build as CI.

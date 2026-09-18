# Where this stands

Working notes for picking the site back up. Not part of the published site
(excluded in `_config.yml`).

## Status

All work is **local only**. Nothing has been committed or pushed — `git status`
still shows every change as uncommitted, and `magics.png` (the old robot logo)
is staged for deletion but recoverable from git history.

## To see the site

    cd ~/Desktop/GradSchool/USF/usf-magics.github.io
    python3 tools/serve.py

Then open http://127.0.0.1:4321/ — rebuilds and serves with caching disabled, so
a plain reload always shows the current build.

## Pages

| URL | Source | In nav |
|---|---|---|
| `/` | `index.md` | yes |
| `/meetings/` | `meetings/index.md` | yes |
| `/projects/` | `projects/index.md` | yes |
| `/publications/` | `publications/index.md` | yes |
| `/people/` | `people/index.md` | yes |
| `/alumni/` | `alumni/index.md` | yes |
| `/recordings/` | `recordings/index.md` | **no — hidden, `noindex`** |

## Open question

The page measures perfectly symmetric (left and right gaps identical) at every
width from 320px to 2200px, but the layout was reported as "not centered". Two
candidates not yet resolved:

1. Below about 1180px the text runs nearly edge to edge, with only a 24px
   gutter. This followed from removing the reading-width cap on `.prose`.
2. The masthead is left-weighted: logo and tagline sit left with a large empty
   green field to their right.

## Known content gaps

* `projects/index.md` and `publications/index.md` still list Paul Intrevado as
  an author and project member. Left alone deliberately — historical record,
  not current staffing.
* Faaz Arshad's Google Scholar link was removed (the profile 404s) and no
  replacement could be verified.
* `people/index-table.md` is an unused alternate version of the Lab Members
  page, excluded from the build and now well out of date.
* "AJ Alston & Dain Brownlow" were supplied joined by an ampersand and are
  listed as two separate people.
* Kellie Clark appears both as Lab Manager and as a research assistant.

## Tools

| Script | Does |
|---|---|
| `tools/serve.py` | rebuild + serve the preview, no-cache |
| `tools/preview.py` | build `preview/` only |
| `tools/redraw_logo.py` | regenerate `assets/img/magics-mark.png` |
| `tools/make_favicon.py` | regenerate the favicon set |
| `tools/make_pdf.py` | export every page to one PDF (server must be running) |

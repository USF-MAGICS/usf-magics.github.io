# magics.cs.usfca.edu

Source for the MAGICS Research Lab website at the University of San Francisco, built with
[Jekyll](https://jekyllrb.com/) and served by GitHub Pages.

## Editing the site

| What you want to change | File |
|---|---|
| Home page | `index.md` |
| Research Projects page | `projects/index.md` |
| Meetings page (day/time/room/Zoom) | `meetings/index.md` |
| Publications page | `publications/index.md` |
| Lab Members page | `people/index.md` |
| Lab Alumni page | `alumni/index.md` |
| Recorded Meetings (hidden) | `recordings/index.md` |
| Navigation tabs, header, footer | `_layouts/default.html` |
| Colors, fonts, spacing | `assets/css/style.scss` |
| Site title and tagline | `_config.yml` |

Each page begins with a small block of front matter between `---` lines. Leave
it in place and edit the text below it — it is ordinary Markdown.

## Hidden pages

`recordings/index.md` is built and served at `/recordings/` but is deliberately
left out of the navigation and the footer, and its front matter carries
`noindex: true`, which makes the layout emit `<meta name="robots"
content="noindex, nofollow">`.

**This hides the page; it does not protect it.** GitHub Pages serves every file
in this repository publicly, and the repository itself is public, so anyone with
the address can read it and the Markdown source is visible on GitHub. Do not put
anything on it that cannot be public. For genuinely restricted recordings, keep
the files in Zoom, Google Drive, or Canvas with access limited there, and link
to them only once the page is published.

To publish it: add a nav entry in `_layouts/default.html` and remove the
`noindex: true` line from the page's front matter.

## Logo

The mark is redrawn from the original artwork at high resolution, in USF brand
colours. `tools/redraw_logo.py` regenerates the mark and `tools/make_favicon.py`
regenerates the icon set, so either can be re-exported at any size.

| File | Where it appears |
|---|---|
| `assets/img/magics-mark.png` | masthead and home page hero |
| `favicon*`, `apple-touch-icon.png`, `android-chrome-*.png` | browser tab and app icons |

The geometry (bracket frame, stroke weights, wordmark tracking) is measured from
the original and reproduced exactly; the palette is USF Green and USF Gold, and
the type is set in Helvetica to match the original letterforms.

## Branding

Colors and typography follow the University of San Francisco brand as published
on `usfca.edu`:

* USF Green `#00543C`
* USF Gold `#FDBB30`
* Body text `#333333`
* IBM Plex Serif (headings), Fira Sans (body), Fira Sans Extra Condensed (navigation)

The official USF logo lockups are issued by the Office of Marketing
Communications and are not included here. See the
[logo guidelines](https://myusf.usfca.edu/marketing-communications/resources/graphics-resources/logo-guidelines).

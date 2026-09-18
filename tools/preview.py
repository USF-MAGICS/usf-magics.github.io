#!/usr/bin/env python3
"""Render a local, browsable preview of the MAGICS Jekyll site.

This is a preview only -- it substitutes the small amount of Liquid used in
_layouts/default.html and renders the Markdown with pandoc. GitHub Pages does
the real build. Output goes to preview/ which is gitignored.
"""
import io, os, re, shutil, subprocess, sys, time

ROOT = os.path.expanduser("~/Desktop/GradSchool/USF/usf-magics.github.io")
OUT = os.path.join(ROOT, "preview")

SITE_TITLE = "MAGICS Lab"
SITE_DESC = "Machine Learning · Artificial Intelligence · Game Intelligence · Computing at Scale"
YEAR = "2026"

# source markdown -> (output file, nav section key, <title>)
PAGES = [
    ("index.md",              "index.html",              "",             "Home"),
    ("projects/index.md",     "projects/index.html",     "projects",     "Research Projects"),
    ("meetings/index.md",     "meetings/index.html",     "meetings",     "Meetings"),
    ("publications/index.md", "publications/index.html", "publications", "Publications"),
    ("people/index.md",       "people/index.html",       "people",       "Lab Members"),
    ("alumni/index.md",       "alumni/index.html",       "alumni",       "Lab Alumni"),
    # hidden: built and browsable, but deliberately absent from the navigation
    ("recordings/index.md",   "recordings/index.html",   "recordings",   "Recorded Meetings", True),
]

CACHE_BUST = str(int(time.time()))   # forces the browser to refetch the CSS


def strip_front_matter(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2].lstrip("\n")
    return text


def md_to_html(path):
    with io.open(path, encoding="utf-8") as f:
        body = strip_front_matter(f.read())
    proc = subprocess.run(
        ["pandoc", "-f", "markdown+markdown_in_html_blocks", "-t", "html5"],
        input=body.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode:
        sys.exit("pandoc failed on %s: %s" % (path, proc.stderr.decode()))
    return proc.stdout.decode("utf-8")


def render(template, section, title, content, noindex=False):
    t = template
    t = t.replace('{% seo %}', '<title>%s | %s</title>' % (title, SITE_TITLE))
    t = t.replace('{{ site.lang | default: "en-US" }}', "en-US")
    t = t.replace('{{ "/assets/css/style.css?v=" | append: site.github.build_revision | relative_url }}',
                  "/style.css?v=" + CACHE_BUST)
    t = t.replace('{{ "/" | absolute_url }}', "/")
    t = re.sub(r'\{\{ "(/assets/img/[^"]+)" \| relative_url \}\}', lambda m: m.group(1), t)
    t = t.replace("{{ site.title | default: site.github.repository_name }}", SITE_TITLE)
    t = t.replace("{{ site.title }}", SITE_TITLE)
    t = t.replace("{{ site.description }}", SITE_DESC)
    t = t.replace("{{ site.description | default: site.github.project_tagline }}", SITE_DESC)
    t = t.replace('{{ site.time | date: "%Y" }}', YEAR)

    # drop the {% assign %} lines used to compute the active section
    t = re.sub(r"\{%\s*assign.*?%\}\s*", "", t)

    t = re.sub(r"\{%\s*if\s+page\.noindex\s*%\}(.*?)\{%\s*endif\s*%\}",
               (lambda m: m.group(1)) if noindex else (lambda m: ""), t, flags=re.S)

    # evaluate block conditionals, e.g. the home-page-only banner
    def block(m):
        op, want = m.group(1), m.group(2)
        have = "/" if section == "" else "/%s/" % section
        keep = (want == have) if op == "==" else (want != have)
        return m.group(3) if keep else ""
    t = re.sub(r'\{%\s*if\s+page\.url\s*(==|!=)\s*"([^"]*)"\s*%\}(.*?)\{%\s*endif\s*%\}',
               block, t, flags=re.S)

    # resolve the nav active-state conditionals
    def active(m):
        cond = m.group(1)
        want = re.search(r'==\s*"([^"]*)"', cond).group(1)
        if "page.url" in cond:
            have = "/" if section == "" else "/%s/" % section
        else:
            have = section
        return 'class="is-active" aria-current="page"' if want == have else ""
    t = re.sub(r'\{%\s*if\s+(.*?)\s*%\}class="is-active" aria-current="page"\{%\s*endif\s*%\}', active, t)

    t = t.replace("{{ content }}", content)

    return t


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets", "img"))

    with io.open(os.path.join(ROOT, "_layouts", "default.html"), encoding="utf-8") as f:
        template = f.read()

    with io.open(os.path.join(ROOT, "assets", "css", "style.scss"), encoding="utf-8") as f:
        css = strip_front_matter(f.read())
    with io.open(os.path.join(OUT, "style.css"), "w", encoding="utf-8") as f:
        f.write(css)

    img_src = os.path.join(ROOT, "assets", "img")
    for name in os.listdir(img_src):
        shutil.copy(os.path.join(img_src, name), os.path.join(OUT, "assets", "img", name))

    for name in os.listdir(ROOT):
        if name.startswith("favicon") or name.startswith("apple-touch"):
            shutil.copy(os.path.join(ROOT, name), os.path.join(OUT, name))
    os.makedirs(os.path.join(OUT, "projects"), exist_ok=True)
    for name in os.listdir(os.path.join(ROOT, "projects")):
        if name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg")):
            shutil.copy(os.path.join(ROOT, "projects", name), os.path.join(OUT, "projects", name))

    for entry in PAGES:
        src, dst, section, title = entry[:4]
        noindex = len(entry) > 4 and entry[4]
        content = md_to_html(os.path.join(ROOT, src))
        page = render(template, section, title, content, noindex)
        dest = os.path.join(OUT, dst)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with io.open(dest, "w", encoding="utf-8") as f:
            f.write(page)
        print("built preview/%s" % dst)

    print("\nServe it with:  python3 tools/serve.py")


if __name__ == "__main__":
    main()

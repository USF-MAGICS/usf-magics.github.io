#!/usr/bin/env python3
"""Render the site to a single PDF for review.

Each web page becomes exactly one PDF page. Heights are measured rather than
guessed: a throwaway measuring page loads each URL in a same-origin iframe at
the target width and reports its natural height, and that height becomes the
@page size for that page's print run.

Requires tools/serve.py to be running (default port 4321).
"""
import os, shutil, subprocess, sys, tempfile, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PREVIEW = os.path.join(ROOT, "preview")
CSS = os.path.join(PREVIEW, "style.css")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE = "http://127.0.0.1:4321"
WIDTH = 1280

PAGES = [
    ("/",              "1-home"),
    ("/meetings/",     "2-meetings"),
    ("/projects/",     "3-research-projects"),
    ("/publications/", "4-publications"),
    ("/people/",       "5-lab-members"),
    ("/recordings/",   "6-recorded-meetings-hidden"),
]

MEASURER = """<!doctype html><meta charset="utf-8"><title>measure</title>
<body style="margin:0">
<div id="out">pending</div>
<script>
var target = new URLSearchParams(location.search).get('p') || '/';
var f = document.createElement('iframe');
f.style.cssText = 'position:absolute;left:-9999px;top:0;width:%dpx;height:600px;border:0';
f.onload = function () {
  var d = f.contentDocument;
  d.body.style.minHeight = '0';              // matches the print stylesheet
  // Images and webfonts change layout height, so wait for them before
  // measuring - otherwise a page with photographs measures short and spills
  // onto a second, nearly empty PDF page.
  var imgs = Array.prototype.slice.call(d.images);
  var waits = imgs.map(function (i) {
    return i.complete ? Promise.resolve() : new Promise(function (r) { i.onload = i.onerror = r; });
  });
  if (d.fonts && d.fonts.ready) waits.push(d.fonts.ready);
  Promise.all(waits).then(function () {
    setTimeout(function () {
      var h = Math.ceil(d.body.getBoundingClientRect().height);
      document.getElementById('out').textContent = 'HEIGHT=' + h;
    }, 500);
  });
};
f.src = target;
document.body.appendChild(f);
</script>
""" % WIDTH


def print_css(height):
    return """
/* --- appended only while exporting the PDF --- */
@page { size: %dpx %dpx; margin: 0; }
html { width: %dpx; }
body { width: %dpx; min-height: 0 !important; }   /* 100vh would force a blank overflow page */
*, *::before, *::after {
  -webkit-print-color-adjust: exact !important;
  print-color-adjust: exact !important;
}
.skip-link { display: none !important; }
""" % (WIDTH, height, WIDTH, WIDTH)


PROFILE = None


COMMON = ["--headless", "--disable-gpu", "--no-sandbox", "--no-first-run",
          "--no-default-browser-check", "--disable-extensions",
          "--disable-background-networking", "--disable-sync"]


def chrome(args, timeout=45, done_file=None):
    """Run Chrome headless.

    Chrome routinely hangs after it has finished the work, so rather than
    waiting out the timeout, poll for the file it was asked to produce and
    terminate it the moment that file is complete.
    """
    args = args[:1] + ["--user-data-dir=" + PROFILE] + args[1:]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            break
        if done_file and os.path.exists(done_file) and os.path.getsize(done_file) > 1000:
            size = os.path.getsize(done_file)
            time.sleep(0.7)                       # let the write settle
            if os.path.getsize(done_file) == size:
                proc.terminate()
                break
        time.sleep(0.3)
    else:
        proc.terminate()
    try:
        out, _ = proc.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, _ = proc.communicate()
    return out or b""


def page_count(pdf):
    out = subprocess.run(["pdfinfo", pdf], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL).stdout.decode()
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return 1


def measure(path):
    url = "%s/_measure.html?p=%s" % (BASE, path)
    dom = chrome([CHROME] + COMMON + ["--virtual-time-budget=8000", "--dump-dom", url], timeout=45)
    text = dom.decode("utf-8", "replace")
    if "HEIGHT=" not in text:
        return None
    return int(text.split("HEIGHT=")[1].split("<")[0].strip())


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(ROOT)
    out_pdf = os.path.join(out_dir, "MAGICS Lab Website Draft.pdf")

    subprocess.run([sys.executable, os.path.join(HERE, "preview.py")], check=True)

    try:
        urllib.request.urlopen(BASE + "/", timeout=5).read(1)
    except Exception:
        sys.exit("The preview server is not running. Start it first:\n"
                 "    python3 tools/serve.py")

    original = open(CSS, encoding="utf-8").read()
    measurer = os.path.join(PREVIEW, "_measure.html")
    with open(measurer, "w", encoding="utf-8") as f:
        f.write(MEASURER)

    global PROFILE
    tmp = tempfile.mkdtemp(prefix="magics-pdf-")
    PROFILE = os.path.join(tmp, "chrome-profile")
    parts = []
    try:
        for path, name in PAGES:
            height = measure(path)
            if not height:
                height = 2400
                note = "(measurement failed, using fallback)"
            else:
                note = ""
            dest = os.path.join(tmp, name + ".pdf")
            # Print layout can run a little taller than the measurement (floated
            # images especially), so verify the result is a single page and grow
            # the page if it is not, rather than guessing at a fixed margin.
            attempt_h = height + 6
            for attempt in range(4):
                if os.path.exists(dest):
                    os.remove(dest)
                with open(CSS, "w", encoding="utf-8") as f:
                    f.write(original + print_css(attempt_h))
                chrome([CHROME] + COMMON + ["--no-pdf-header-footer",
                        "--virtual-time-budget=10000", "--print-to-pdf=" + dest, BASE + path],
                       done_file=dest)
                for _ in range(20):
                    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
                        break
                    time.sleep(0.5)
                if not os.path.exists(dest):
                    sys.exit("Chrome did not produce a PDF for " + path)
                n = page_count(dest)
                if n <= 1:
                    break
                attempt_h = int(attempt_h * 1.06) + 20
            print("  %-16s %dx%dpx  %d page  %6.1f KB %s"
                  % (path, WIDTH, attempt_h, page_count(dest),
                     os.path.getsize(dest) / 1024.0, note))
            parts.append(dest)

        subprocess.run(["pdfunite"] + parts + [out_pdf], check=True)
        pages = subprocess.run(["pdfinfo", out_pdf], stdout=subprocess.PIPE).stdout.decode()
        count = [l for l in pages.splitlines() if l.startswith("Pages:")]
        print("\nWrote: %s" % out_pdf)
        print("  %.1f KB, %s" % (os.path.getsize(out_pdf) / 1024.0,
                                 count[0] if count else "page count unknown"))
    finally:
        with open(CSS, "w", encoding="utf-8") as f:
            f.write(original)
        if os.path.exists(measurer):
            os.remove(measurer)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()

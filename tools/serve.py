#!/usr/bin/env python3
"""Rebuild the preview and serve it exactly as a visitor would see the site.

Real URLs (/, /meetings/, /projects/ ...) and no-cache headers, so a reload
always shows the current CSS instead of a stale cached copy.
"""
import functools, http.server, os, subprocess, sys, threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "preview")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4321


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


def main():
    subprocess.run([sys.executable, os.path.join(HERE, "preview.py")], check=True)
    # Threaded: a browser holds keep-alive connections open, and a
    # single-threaded server wedges behind them and stops answering.
    class Server(http.server.ThreadingHTTPServer):
        allow_reuse_address = True
        daemon_threads = True

    with Server(("127.0.0.1", PORT), functools.partial(Handler, directory=OUT)) as httpd:
        print("\nServing the site at http://127.0.0.1:%d/" % PORT)
        print("Pages:  /   /meetings/   /projects/   /publications/   /people/")
        print("Caching is disabled, so a plain reload always shows the latest build.")
        print("Press Ctrl+C to stop.\n")
        httpd.serve_forever()


if __name__ == "__main__":
    main()

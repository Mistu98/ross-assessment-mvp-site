#!/usr/bin/env python3
"""Mirror the already-built, public Netlify MVP preview for GitHub Pages.

This script copies only the static browser-delivered HTML, JS, CSS, assets
and reviewed concepts JSON. It never downloads the private GitHub repository,
its history, KNIME archive, or non-web research files.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

SOURCE = "https://deploy-preview-10--timely-bunny-9be542.netlify.app"
PAGES_PREFIX = "/ross-assessment-mvp-site/"
TARGET = pathlib.Path("site")
MAX_FILES = 100
MAX_BYTES = 25 * 1024 * 1024

class PageAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.resources = set()

    def handle_starttag(self, tag, attributes):
        attr = dict(attributes)
        if tag in ("script", "link", "img", "source"):
            for key in ("src", "href"):
                value = attr.get(key, "")
                if isinstance(value, str) and (
                    value.startswith("/assets/")
                    or value.startswith("/vite.svg")
                    or value.startswith("/favicon")
                ):
                    self.resources.add(urllib.parse.urlsplit(value).path.lstrip("/"))

def download(path):
    if not path or path.startswith("/") or ".." in pathlib.PurePosixPath(path).parts:
        raise RuntimeError("Disallowed remote file path")
    url = SOURCE + "/" + path
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "RossMVP-Static-Publisher/1.0",
            "Accept": "*/*",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            if response.geturl().split("/")[2] != urllib.parse.urlsplit(SOURCE).netloc:
                raise RuntimeError("Unexpected redirect host; check Netlify visitor access")
            payload = response.read(MAX_BYTES + 1)
            content_type = response.headers.get("Content-Type", "")
            if len(payload) > MAX_BYTES:
                raise RuntimeError("Static resource exceeds safety size limit")
            if response.status != 200:
                raise RuntimeError("Unexpected HTTP status")
            print(f"GET /{path} -> HTTP {response.status} ({len(payload)} bytes; {content_type})")
            return payload, content_type
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Cannot download Netlify resource /{path}: {exc}") from exc

def save(path, payload):
    destination = TARGET / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)

def main():
    TARGET.mkdir(parents=True, exist_ok=True)
    html_bytes, content_type = download("index.html")
    html = html_bytes.decode("utf-8")
    if '<div id="root"' not in html or not re.search(r"<script[^>]+/assets/[^>]+>", html):
        raise RuntimeError("Source is not the expected Vite application; check access or source URL")

    parsed = PageAssets()
    parsed.feed(html)
    resources = sorted(parsed.resources | {"data/concepts.json"})
    seen = set()
    while resources:
        resource = resources.pop(0)
        if resource in seen:
            continue
        if len(seen) >= MAX_FILES:
            raise RuntimeError("Too many browser assets to mirror safely")
        seen.add(resource)
        body, content_type = download(resource)
        if resource.endswith(".json"):
            parsed_json = json.loads(body)
            if not isinstance(parsed_json, dict) or len(parsed_json.get("concepts", [])) != 15:
                raise RuntimeError("Concepts JSON is missing or does not match 15 approved concepts")
            if parsed_json.get("version") != "report-2026-11-22-provisional":
                raise RuntimeError("Netlify preview does not contain the latest approved report baseline")
        if resource.endswith(".js"):
            js = body.decode("utf-8")
            if "report-2026-11-22-provisional" not in js:
                print("Note: This JS chunk has no report version marker; check other bundle chunks")
            # Vite asset files are ordinarily referenced from index.html. If a
            # split chunk refers to another /assets item, include it too.
            for path in re.findall(r"/assets/[A-Za-z0-9_./-]+\.(?:js|css|svg|png|jpe?g|webp|woff2?)", js):
                candidate = path.lstrip("/")
                if candidate not in seen and candidate not in resources:
                    resources.append(candidate)
        if resource.endswith(".css"):
            css = body.decode("utf-8")
            for path in re.findall(r"/assets/[A-Za-z0-9_./-]+\.(?:svg|png|jpe?g|webp|woff2?|ttf)", css):
                candidate = path.lstrip("/")
                if candidate not in seen and candidate not in resources:
                    resources.append(candidate)
            css = css.replace("url(/assets/", "url(" + PAGES_PREFIX + "assets/")
            css = css.replace('url("/assets/', 'url("' + PAGES_PREFIX + "assets/")
            css = css.replace("url('/assets/", "url('" + PAGES_PREFIX + "assets/")
            body = css.encode("utf-8")
        save(resource, body)

    # Vite was built with Netlify's root path (/). Rewrite the browser-visible
    # assets and redirect its single root-absolute data fetch to Pages prefix.
    html = html.replace('src="/assets/', 'src="' + PAGES_PREFIX + "assets/")
    html = html.replace('href="/assets/', 'href="' + PAGES_PREFIX + "assets/")
    html = html.replace('href="/vite.svg', 'href="' + PAGES_PREFIX + "vite.svg")
    html = html.replace('href="/favicon', 'href="' + PAGES_PREFIX + "favicon")
    shim = """<script>
(function () {
  const originalFetch = window.fetch.bind(window);
  const prefix = "/ross-assessment-mvp-site";
  window.fetch = function (resource, options) {
    if (typeof resource === "string" &&
        (resource === "/data/concepts.json" ||
         resource.startsWith("/data/concepts.json?"))) {
      resource = prefix + resource;
    }
    return originalFetch(resource, options);
  };
})();
</script>"""
    if "</head>" not in html:
        raise RuntimeError("Invalid Vite HTML: no closing head")
    html = html.replace("</head>", shim + "\n</head>", 1)
    save("index.html", html.encode("utf-8"))
    save(".nojekyll", b"")
    print(f"Prepared {len(seen)} browser-delivered static assets with GitHub Pages base path")
    print("No private repository source code or Git history was copied.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

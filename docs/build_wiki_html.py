#!/usr/bin/env python
"""Generate the HTML mirror of the Markdown wiki.

``docs/wiki/*.md`` is the source of truth for the platform documentation. The
application serves it twice:

* ``/dashboard/wiki/<page>/``  renders the Markdown directly (any signed-in user);
* ``/dashboard/guide/<page>/`` serves ``docs/wiki_html/<page>.html`` (superusers,
  except ``end_user`` which everyone may read).

This script keeps the second copy in step with the first. Run it after editing
any page under ``docs/wiki/``::

    python docs/build_wiki_html.py

Only the pages listed in :data:`MIRRORED_PAGES` are generated. The numbered
developer guides (``01_project_overview`` … ``13_testing``) are hand-written
HTML and are never touched.

The only third-party requirement is ``markdown``, which is already a project
dependency (``requirements/base.txt``).
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:  # pragma: no cover - dependency guard
    sys.exit("The 'markdown' package is required: pip install markdown")

DOCS_DIR = Path(__file__).resolve().parent
MD_DIR = DOCS_DIR / "wiki"
HTML_DIR = DOCS_DIR / "wiki_html"
CSS_FILE = DOCS_DIR / "wiki_assets" / "wiki.css"

SITE_NAME = "BMA Documentation"
SITE_VERSION = "BMA — NFE Sector · UNICEF Lebanon"
FOOTER = "BMA — NFE Sector Platform &nbsp;|&nbsp; UNICEF Lebanon NFE Sector"

#: Pages generated from Markdown: ``slug -> nav label``.
MIRRORED_PAGES = {
    "index": "Home",
    "end_user": "End User Manual",
    "admin": "Administration Guide",
    "developer": "Developer Guide",
    "system_details": "System Overview",
}

#: Hand-written developer guides, listed in the sidebar but never regenerated.
STATIC_PAGES = [
    ("01_project_overview", "1. Project Overview"),
    ("02_setup", "2. Setup &amp; Installation"),
    ("03_architecture", "3. Architecture &amp; Tech Stack"),
    ("04_database_schema", "4. Database Schema &amp; Models"),
    ("05_django_apps", "5. Django Apps Reference"),
    ("06_api_urls", "6. API &amp; URL Reference"),
    ("07_auth_permissions", "7. Authentication &amp; Permissions"),
    ("08_admin_portal", "8. Admin Portal Guide"),
    ("09_celery_tasks", "9. Background Tasks (Celery)"),
    ("10_frontend", "10. Frontend Guide"),
    ("11_environment_variables", "11. Environment Variables"),
    ("12_deployment", "12. Deployment Guide"),
    ("13_testing", "13. Testing Guide"),
]

MARKDOWN_EXTENSIONS = ["extra", "toc"]

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — BMA Wiki</title>
  <style>
{css}
</style>
</head>
<body>

<aside id="sidebar">
  <div id="sidebar-header">
    <div class="logo">{site_name}</div>
    <div class="version">{site_version}</div>
  </div>
  <nav>
{nav}
  </nav>
</aside>

<div id="main">
  <div id="topbar">
    <span class="breadcrumb">BMA Wiki &rsaquo; <span>{title}</span></span>
  </div>
  <div id="content">
{content}
  </div>
  <div id="footer">
    {footer}
  </div>
</div>

</body>
</html>
"""


def build_nav(active: str) -> str:
    """Render the sidebar for ``active``, matching ``WIKI_HTML_PAGES`` order."""

    def link(slug: str, label: str) -> str:
        cls = ' class="active"' if slug == active else ""
        return f'    <a href="{slug}.html"{cls}>{label}</a>'

    lines = [
        '    <div class="section-label">Navigation</div>',
        link("index", "🏠 Home"),
        link("end_user", "📖 End User Manual"),
        '    <div class="section-label">Additional Guides</div>',
        link("admin", "Administration Guide"),
        link("developer", "Developer Guide"),
        link("system_details", "System Overview"),
        '    <div class="section-label">Developer Guides</div>',
    ]
    lines += [link(slug, label) for slug, label in STATIC_PAGES]
    return "\n".join(lines)


def resolve_links(body: str) -> str:
    """Point Markdown links at their HTML equivalents.

    ``other_page.md`` becomes ``other_page.html``. Links that reach outside the
    wiki directory (``../ACCESS_CONTROL.md``) cannot be served by the in-app
    guide view, so the anchor is unwrapped and the path is shown as code.
    """

    body = re.sub(r'href="([\w\-]+)\.md(#[^"]*)?"', r'href="\1.html\2"', body)

    def unwrap(match: re.Match) -> str:
        target, text = match.group(1), match.group(2)
        if "<" in text:  # already contains markup such as <code>
            return f"{text} <span class=\"muted\">({html.escape(target)})</span>"
        return f"<code>{html.escape(target)}</code>"

    return re.sub(r'<a href="([^"]*\.md(?:#[^"]*)?)">(.*?)</a>', unwrap, body, flags=re.S)


def page_title(md_text: str, slug: str) -> str:
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return MIRRORED_PAGES.get(slug, slug)


def render(slug: str, css: str) -> str:
    md_text = (MD_DIR / f"{slug}.md").read_text(encoding="utf-8")
    body = markdown.markdown(md_text, extensions=MARKDOWN_EXTENSIONS)
    body = resolve_links(body)
    return PAGE_TEMPLATE.format(
        title=html.escape(page_title(md_text, slug)),
        css=css,
        site_name=SITE_NAME,
        site_version=SITE_VERSION,
        nav=build_nav(slug),
        content=body,
        footer=FOOTER,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if any generated page differs from the file on disk",
    )
    args = parser.parse_args()

    css = CSS_FILE.read_text(encoding="utf-8").rstrip("\n")
    HTML_DIR.mkdir(parents=True, exist_ok=True)

    stale = []
    for slug in MIRRORED_PAGES:
        source = MD_DIR / f"{slug}.md"
        if not source.exists():
            print(f"skipping {slug}: {source} is missing")
            continue

        target = HTML_DIR / f"{slug}.html"
        output = render(slug, css)
        current = target.read_text(encoding="utf-8") if target.exists() else None

        if args.check:
            if current != output:
                stale.append(target.name)
            continue

        if current == output:
            print(f"unchanged  {target.relative_to(DOCS_DIR.parent)}")
        else:
            target.write_text(output, encoding="utf-8")
            print(f"written    {target.relative_to(DOCS_DIR.parent)}")

    if args.check and stale:
        print("out of date: " + ", ".join(stale))
        print("run: python docs/build_wiki_html.py")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

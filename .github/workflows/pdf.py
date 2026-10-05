"""Merge the built documentation pages into one document and render it to PDF.

Run from the repository root, after `npm run build`: the pages are read from
`dist/`, in the order of the `sidebar` array in `astro.config.ts`. The merged
document is rendered from memory; pass `--html-out` to keep a copy of it.
"""

import argparse
import html
import os
import re
from pathlib import Path

import lxml.etree as etree
from lxml import html as lhtml

DIST = Path.cwd() / "dist"
ASTRO_CONFIG = Path.cwd() / "astro.config.ts"

# A revision of the documentation is built under a base path, which `astro.config.ts`
# computes from `UTN_REVISION`; the pages carry it on every link and asset URL. The build
# writes `dist/` flat, without that path, so the pages have to be told the same value here
# for a URL to be read as a file. The workflow passes the variable through.
UTN_REVISION = os.environ.get("UTN_REVISION")
BASE = f"/notes/tn57/utn57-mong-{UTN_REVISION}/" if UTN_REVISION else "/"


def site_path(url_path: str) -> str:
    """A site URL path with the base path taken off, so that it names a file in `dist/`."""
    if BASE != "/" and url_path.startswith(BASE):
        return "/" + url_path[len(BASE) :]
    return url_path


def site_file(url_path: str) -> Path:
    """The file the build wrote for a site URL path."""
    return (DIST / site_path(url_path).lstrip("/")).resolve()


def parse_site_title() -> str:
    text = ASTRO_CONFIG.read_text(encoding="utf-8")
    m = re.search(r'title:\s*"([^"]+)"', text)
    return m.group(1) if m else "Encoding and Shaping of the Mongolian Script"


def parse_sidebar_slugs() -> list[str]:
    """Return the doc slugs in the order of the Starlight `sidebar` array."""
    text = ASTRO_CONFIG.read_text(encoding="utf-8")
    m = re.search(r"sidebar\s*:\s*\[", text)
    if not m:
        raise SystemExit("could not find `sidebar: [` in astro.config.ts")
    start = m.end() - 1  # the index of '['
    depth = 0
    end = None
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        raise SystemExit("unbalanced `sidebar` array in astro.config.ts")
    block = text[start : end + 1]
    slugs: list[str] = []
    for mm in re.finditer(r'"((?:[^"\\]|\\.)*)"', block):
        prefix = block[: mm.start()].rstrip()
        if re.search(r"\b(?:label|icon|text|link|href)\s*:\s*$", prefix):
            continue  # an object key, not a page slug
        slugs.append(mm.group(1))
    return slugs


def page_html_path(slug: str) -> Path:
    return DIST / "index.html" if slug == "index" else DIST / slug / "index.html"


CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(/[^'\")\s]+)\1\s*\)")


def rewrite_css_url(m: re.Match) -> str:
    quote, path = m.group(1), m.group(2)
    return f"url({quote}{site_file(path).as_uri()}{quote})"


def collect_css(doc, seen: dict) -> None:
    """Inline the page's stylesheets and <style> blocks into a deduped dict."""
    root = doc.getroot()
    for link in root.xpath('//link[@rel="stylesheet"]'):
        href = link.get("href", "")
        if href.startswith(("http://", "https://", "data:", "mailto:")):
            continue
        fp = site_file(href)
        if href not in seen and fp.is_file():
            css = fp.read_text(encoding="utf-8")
            seen[href] = CSS_URL_RE.sub(rewrite_css_url, css)
    for style in root.xpath("//style"):
        text = style.text_content() or ""
        if text.strip():
            seen.setdefault(f"inline:{hash(text)}", text)


def first_with_class(node, class_name: str):
    """Return the first descendant of *node* carrying the CSS class."""
    found = node.xpath(
        f".//*[contains(concat(' ', normalize-space(@class), ' '), ' {class_name} ')]"
    )
    return found[0] if found else None


def extract_page(doc):
    """Return (title, body_html) for a page, taking its markdown content."""
    root = doc.getroot()
    h1s = root.xpath("//h1")
    title = " ".join(h1s[0].itertext()).strip() if h1s else ""
    content = first_with_class(root, "sl-markdown-content")
    body = ""
    if content is not None:
        body = etree.tostring(content, method="html", encoding="unicode")
    return title, body


def process_content(slug: str, body_html: str):
    """Namespace ids and links per page and return (body_html, headings)."""
    if not body_html.strip():
        return "", []

    frag = lhtml.fromstring(body_html)

    for el in frag.xpath(".//style | .//script | .//link"):
        parent = el.getparent()
        if parent is not None:
            parent.remove(el)

    idmap: dict = {}
    used: set = set()
    for el in frag.xpath("//*[@id]"):
        old = el.get("id")
        base = f"{slug}-{old}"
        new, n = base, 1
        while new in used:
            n += 1
            new = f"{base}-{n}"
        used.add(new)
        el.set("id", new)
        idmap[old] = new

    for a in frag.xpath("//a[@href]"):
        href = site_path(a.get("href") or "")
        if href.startswith("#"):
            anchor = href[1:]
            a.set("href", f"#{idmap.get(anchor, slug + '-' + anchor)}")
        elif href == "/":
            a.set("href", "#index-top")
        elif href.startswith("/#"):
            a.set("href", f"#index-{href[2:]}")
        elif href.startswith("/"):
            m = re.match(r"^/([^/#]+)/?(?:#(.+))?$", href)
            if m:
                target_slug, anchor = m.group(1), m.group(2)
                target = f"#{target_slug}-{anchor}" if anchor else f"#{target_slug}-top"
                a.set("href", target)

    for el in frag.xpath("//img[@src] | //source[@src]"):
        src = el.get("src") or ""
        if src.startswith("/"):
            el.set("src", site_file(src).as_uri())

    headings = []
    for h in frag.xpath(".//h2 | .//h3 | .//h4 | .//h5 | .//h6"):
        text = " ".join(h.itertext()).strip()
        hid = h.get("id")
        if text and hid:
            headings.append((int(h.tag[1]), hid, text))

    return etree.tostring(frag, method="html", encoding="unicode"), headings


def build_document(slugs: list, site_title: str):
    seen_css: dict = {}
    pages = []  # (slug, title, body_html)
    headings_by_slug: dict = {}

    for slug in slugs:
        path = page_html_path(slug)
        if not path.is_file():
            raise SystemExit(f"missing built page: {path} — run `npm run build` first")
        doc = lhtml.parse(str(path))
        collect_css(doc, seen_css)
        title, body_html = extract_page(doc)
        body_html, headings = process_content(slug, body_html)
        pages.append((slug, title, body_html))
        headings_by_slug[slug] = headings

    all_levels = [lv for hs in headings_by_slug.values() for lv, _, _ in hs]
    min_level = min(all_levels) if all_levels else 2

    toc_items: list[str] = []
    for slug, title, _ in pages:
        item = f'<li class="toc-l0"><a href="#{slug}-top">{html.escape(title)}</a></li>'
        toc_items.append(item)
        for level, hid, text in headings_by_slug[slug]:
            depth = level - min_level + 1
            toc_items.append(
                f'<li class="toc-l{depth}"><a href="#{hid}">{html.escape(text)}</a></li>'
            )

    sections: list[str] = []
    for slug, title, body_html in pages:
        sections.append(
            f'<section class="print-page" id="{slug}">'
            f'<h1 class="page-title" id="{slug}-top">{html.escape(title)}</h1>'
            f'<div class="page-body">{body_html}</div>'
            f"</section>"
        )

    css_blocks = "\n".join(f"<style>{css}</style>" for css in seen_css.values())
    # The cover names the document, not the copy of it — the wording `docs/index.mdx` uses
    # on the site: only a build that is a revision of the UTN says that it is one.
    subtitle = (
        f"Unicode Technical Note #57, revision {UTN_REVISION}"
        if UTN_REVISION
        else "Documentation of the Mongolian script"
    )

    doc_html = "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="en" data-theme="light">',
            "<head>",
            '<meta charset="utf-8"/>',
            f"<title>{html.escape(site_title)} — Documentation</title>",
            css_blocks,
            "</head>",
            "<body>",
            '<section class="doc-front">',
            '  <div class="doc-title">',
            f"    <h1>{html.escape(site_title)}</h1>",
            f'    <p class="doc-subtitle">{subtitle}</p>',
            "  </div>",
            '  <nav class="toc">',
            '    <h2 class="toc-title">Contents</h2>',
            f"    <ul>{''.join(toc_items)}</ul>",
            "  </nav>",
            "</section>",
            *sections,
            "</body>",
            "</html>",
        ]
    )

    return doc_html, len(pages)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render the docs site into one PDF.")
    ap.add_argument("--out", type=Path, default=Path("temp/mongolian-utn.pdf"))
    ap.add_argument("--html-out", type=Path, help="also write the merged HTML here")
    args = ap.parse_args()

    if not DIST.is_dir():
        raise SystemExit(f"{DIST} not found — run `npm run build` first")

    slugs = parse_sidebar_slugs()
    print("sidebar order:", " ".join(slugs))
    site_title = parse_site_title()
    doc_html, page_count = build_document(slugs, site_title)
    print(f"merged {page_count} pages")

    if args.html_out:
        args.html_out.parent.mkdir(parents=True, exist_ok=True)
        args.html_out.write_text(doc_html, encoding="utf-8")
        print(f"wrote {args.html_out}")

    # Imported here so that the merge itself runs without WeasyPrint present.
    from weasyprint import HTML

    args.out.parent.mkdir(parents=True, exist_ok=True)
    document = HTML(string=doc_html, base_url=str(DIST)).render()
    print(f"rendered {len(document.pages)} PDF pages")
    document.write_pdf(str(args.out))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()

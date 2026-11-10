#!/usr/bin/env python3
"""Lightweight site smoke checks: content, links and provenance labelling."""
import html.parser
import sys
from pathlib import Path


class Parser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a":
            self.links.append(values.get("href", ""))
        if tag == "img":
            self.images.append(values.get("src", ""))


def check(site, commit):
    homepage = site / "index.html"
    assert homepage.is_file()
    assert (site / "results.css").is_file()
    cheatsheet = site / "cheatsheet" / "index.html"
    assert cheatsheet.is_file()
    guide = cheatsheet.read_text(encoding="utf-8")
    for term in ("Rectangle2D", "Circle2D", "Cylinder(d=", "extrude", "issue #5"):
        assert term in guide, term

    text = homepage.read_text(encoding="utf-8")
    assert commit in text, "site must identify its source commit"
    assert 'href="cheatsheet/"' in text
    assert "SCPF" in text and "SCRF" not in text
    for slug in ("plate", "csg-cube", "bracket", "corner-bracket", "sample-plate", "plastic-enclosure"):
        model = site / "models" / slug
        assert (model / "index.html").is_file(), slug
        assert (model / "model.py").is_file(), slug
        assert (model / "solidcraft.json").is_file(), slug
        page = (model / "index.html").read_text(encoding="utf-8")
        assert "Native SolidCraft command sequence" in page
        assert "Show exact command and parameters" not in page
        assert "<details>" not in page
        assert "&quot;command&quot;" in page and "&quot;params&quot;" in page
        assert "Construction stages" in page
        assert "Native SolidCraft image" not in page or (model / "native.png").is_file()
        assert "Schematic drawing only" not in page or "not a SolidCraft geometry render" in page
        if "Previously verified render from main" in page:
            assert (model / "native.png").is_file()
            assert "not yet native-verified" in page
        parser = Parser()
        parser.feed(page)
        for href in parser.links:
            if href.startswith(("http://", "https://", "#", "mailto:")):
                continue
            resolved = (model / href).resolve()
            if href.endswith("/") or href in ("../../",):
                assert resolved.is_dir(), (slug, href)
            else:
                assert resolved.exists(), (slug, href)
        for src in parser.images:
            assert (model / src).is_file(), (slug, src)
    print("Static CAD results site passed smoke checks")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: test-results.py <output/site> <git-sha>")
    check(Path(sys.argv[1]), sys.argv[2])

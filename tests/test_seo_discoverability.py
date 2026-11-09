"""REQ-015: the public page and its discovery files are crawler-ready.

The public demo at https://drive.naindev.com/ is the Vite build of ``NainDrive.Client``.
Vite copies ``public/`` verbatim to the site root, so the checks run against ``index.html``
and ``public/``.
"""
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

import pytest

CLIENT = Path(__file__).resolve().parent.parent / "NainDrive.Client"
CANONICAL = "https://drive.naindev.com/"
AUTHOR_ID = "https://www.naindev.com/#person"
REPOSITORY = "https://github.com/Nain9Dev/NainDrive"


class _Head(HTMLParser):
    """Collects the head tags the SEO baseline cares about."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self.metas: list[dict[str, str]] = []
        self.json_ld: list[str] = []
        self._in_json_ld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if tag == "link":
            self.links.append(values)
        elif tag == "meta":
            self.metas.append(values)
        elif tag == "script" and values.get("type") == "application/ld+json":
            self._in_json_ld = True
            self.json_ld.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self._in_json_ld:
            self.json_ld[-1] += data


@pytest.fixture(scope="module")
def head() -> _Head:
    parser = _Head()
    parser.feed((CLIENT / "index.html").read_text(encoding="utf-8"))
    return parser


def _meta(head: _Head, attribute: str, key: str) -> str:
    values = [m.get("content", "") for m in head.metas if m.get(attribute) == key]
    assert len(values) == 1, f"expected exactly one meta {attribute}={key!r}, found {len(values)}"
    return values[0]


def test_one_canonical_link_equal_to_the_host_root(head: _Head) -> None:
    canonicals = [link for link in head.links if link.get("rel") == "canonical"]
    assert [link["href"] for link in canonicals] == [CANONICAL]


def test_description_is_one_tag_of_70_to_160_characters(head: _Head) -> None:
    assert 70 <= len(_meta(head, "name", "description")) <= 160


def test_open_graph_and_twitter_cards_agree_with_the_canonical_url(head: _Head) -> None:
    assert _meta(head, "property", "og:type") == "website"
    assert _meta(head, "property", "og:site_name") == "NainDrive"
    assert _meta(head, "property", "og:title")
    assert _meta(head, "property", "og:description")
    assert _meta(head, "property", "og:url") == CANONICAL
    image = _meta(head, "property", "og:image")
    assert image.startswith("https://")
    assert _meta(head, "property", "og:image:width") == "1200"
    assert _meta(head, "property", "og:image:height") == "630"

    assert _meta(head, "name", "twitter:card") == "summary_large_image"
    assert _meta(head, "name", "twitter:title")
    assert _meta(head, "name", "twitter:description")
    assert _meta(head, "name", "twitter:image") == image


def test_author_is_linked(head: _Head) -> None:
    authors = [link["href"] for link in head.links if link.get("rel") == "author"]
    assert authors == ["https://www.naindev.com/"]


def test_json_ld_describes_the_application_and_names_the_author_by_id(head: _Head) -> None:
    assert len(head.json_ld) == 1
    data = json.loads(head.json_ld[0])

    assert data["@type"] == "SoftwareApplication"
    assert data["name"] == "NainDrive"
    assert data["url"] == CANONICAL
    assert data["operatingSystem"] == "Web"
    assert data["isAccessibleForFree"] is True
    assert data["description"] == _meta(head, "name", "description")
    assert data["author"]["@id"] == AUTHOR_ID
    assert REPOSITORY in data["sameAs"]


def test_robots_advertises_the_sitemap_and_blocks_nothing() -> None:
    robots = (CLIENT / "public" / "robots.txt").read_text(encoding="utf-8")

    assert "User-agent: *" in robots
    assert "Allow: /" in robots
    assert "Disallow: /" not in robots
    assert f"Sitemap: {CANONICAL}sitemap.xml" in robots


def test_sitemap_lists_the_canonical_url() -> None:
    root = ET.fromstring((CLIENT / "public" / "sitemap.xml").read_text(encoding="utf-8"))
    locations = [element.text for element in root.iter() if element.tag.endswith("}loc")]

    assert locations == [CANONICAL]


def test_llms_txt_starts_with_an_h1_and_links_the_repository_and_main_site() -> None:
    llms = (CLIENT / "public" / "llms.txt").read_text(encoding="utf-8")

    assert re.match(r"# NainDrive\n", llms)
    assert REPOSITORY in llms
    assert "https://www.naindev.com/" in llms

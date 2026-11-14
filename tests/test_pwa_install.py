"""REQ-016: the public page is installable on Android Chrome and iOS Safari.

Vite copies ``NainDrive.Client/public/`` verbatim to the site root, so the checks run against
``index.html`` and ``public/``. No service worker is involved: installability needs none.
"""
import json
import re
import struct
import zlib
from html.parser import HTMLParser
from pathlib import Path

import pytest

CLIENT = Path(__file__).resolve().parent.parent / "NainDrive.Client"
PUBLIC = CLIENT / "public"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
COLOR = re.compile(r"^#[0-9a-f]{6}$")


class _Head(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("link", "meta"):
            self.tags.append((tag, {name: value or "" for name, value in attrs}))


@pytest.fixture(scope="module")
def head() -> _Head:
    parser = _Head()
    parser.feed((CLIENT / "index.html").read_text(encoding="utf-8"))
    return parser


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads((PUBLIC / "manifest.webmanifest").read_text(encoding="utf-8"))


def _metas(head: _Head, name: str) -> list[str]:
    return [a.get("content", "") for t, a in head.tags if t == "meta" and a.get("name") == name]


def _links(head: _Head, rel: str) -> list[dict[str, str]]:
    return [a for t, a in head.tags if t == "link" and a.get("rel") == rel]


def _png_size(path: Path) -> tuple[int, int, int]:
    """Return (width, height, colour type) read from the IHDR chunk."""
    data = path.read_bytes()[:26]
    assert data[:8] == PNG_SIGNATURE, f"{path.name} is not a PNG file"
    width, height = struct.unpack(">II", data[16:24])
    return width, height, data[25]


def test_manifest_names_the_app_and_opens_it_standalone(manifest: dict, head: _Head) -> None:
    assert manifest["name"] == "NainDrive · Autoescuela"
    assert manifest["short_name"] == "NainDrive"
    assert manifest["description"] == _metas(head, "description")[0]
    assert manifest["lang"] == "es"
    assert manifest["dir"] == "ltr"
    assert manifest["id"] == manifest["start_url"] == manifest["scope"] == "./"
    assert manifest["display"] == "standalone"
    assert manifest["theme_color"] == manifest["background_color"] == _metas(head, "theme-color")[0]
    assert COLOR.match(manifest["theme_color"])
    assert "prefer_related_applications" not in manifest


def test_manifest_icons_exist_at_their_declared_size(manifest: dict) -> None:
    declared = [(i["src"], i["sizes"], i["type"], i["purpose"]) for i in manifest["icons"]]
    assert declared == [
        ("./icons/icon-192.png", "192x192", "image/png", "any"),
        ("./icons/icon-512.png", "512x512", "image/png", "any"),
        ("./icons/icon-maskable-512.png", "512x512", "image/png", "maskable"),
    ]
    for src, sizes, _, _ in declared:
        width, height, _ = _png_size(PUBLIC / src.removeprefix("./"))
        assert f"{width}x{height}" == sizes, f"{src} must measure what the manifest declares"


def _min_alpha(path: Path) -> int:
    """Smallest alpha of an 8-bit non-interlaced RGB or RGBA PNG (255 when it has no alpha channel)."""
    data = path.read_bytes()
    width, height, depth, colour_type, _, _, interlace = struct.unpack(">IIBBBBB", data[16:29])
    assert (depth, interlace) == (8, 0) and colour_type in (2, 6), f"{path.name}: unsupported PNG layout"
    if colour_type == 2:
        return 255
    idat, at = b"", 8
    while at < len(data):
        length, kind = struct.unpack(">I4s", data[at : at + 8])
        if kind == b"IDAT":
            idat += data[at + 8 : at + 8 + length]
        at += 12 + length
    raw, stride, bpp = zlib.decompress(idat), width * 4, 4
    previous, lowest = bytearray(stride), 255
    for row in range(height):
        filter_type, line = raw[row * (stride + 1)], bytearray(raw[row * (stride + 1) + 1 : (row + 1) * (stride + 1)])
        for i in range(stride):
            left = line[i - bpp] if i >= bpp else 0
            up, up_left = previous[i], (previous[i - bpp] if i >= bpp else 0)
            if filter_type == 1:
                line[i] = (line[i] + left) & 255
            elif filter_type == 2:
                line[i] = (line[i] + up) & 255
            elif filter_type == 3:
                line[i] = (line[i] + (left + up) // 2) & 255
            elif filter_type == 4:
                p = left + up - up_left
                nearest = min((abs(p - left), left), (abs(p - up), up), (abs(p - up_left), up_left))[1]
                line[i] = (line[i] + nearest) & 255
        lowest = min(lowest, min(line[3::4]))
        previous = line
    return lowest


def test_install_icons_for_launchers_are_opaque() -> None:
    for name, side in (("icon-maskable-512.png", 512), ("apple-touch-icon.png", 180)):
        path = PUBLIC / "icons" / name
        assert _png_size(path)[:2] == (side, side)
        assert _min_alpha(path) == 255, f"{name} must be opaque edge to edge"


def test_page_links_the_manifest_and_the_ios_tags(head: _Head, manifest: dict) -> None:
    assert [a["href"] for a in _links(head, "manifest")] == ["./manifest.webmanifest"]
    assert [a["href"] for a in _links(head, "apple-touch-icon")] == ["./icons/apple-touch-icon.png"]
    assert _metas(head, "mobile-web-app-capable") == ["yes"]
    assert _metas(head, "apple-mobile-web-app-capable") == ["yes"]
    assert _metas(head, "apple-mobile-web-app-title") == [manifest["short_name"]]
    # The page is dark, so the iOS status bar is black.
    assert _metas(head, "apple-mobile-web-app-status-bar-style") == ["black"]
    assert len(_metas(head, "theme-color")) == 1


def test_no_service_worker_is_registered() -> None:
    sources = [CLIENT / "index.html", *(CLIENT / "src").rglob("*.ts"), *(CLIENT / "src").rglob("*.vue")]
    for path in sources:
        assert "serviceWorker" not in path.read_text(encoding="utf-8"), path.name

"""The code on the documentation pages and in the README runs.

Each page's ``python`` blocks run in order in one namespace, as a reader would type
them, in a directory holding the images the pages name (copies of libphash's fixtures).
A failure names the page and the block (``loading.md[2]``) in its traceback. A block
included from ``examples/`` is left to tests/test_examples.py.
"""

from __future__ import annotations

import importlib.util
import io
import os
import re
import shlex
import shutil
import sys
from pathlib import Path

import pytest
from conftest import data, needs_libjpeg_turbo

from libphash._cli import main

ROOT = Path(__file__).resolve().parents[1]
PAGES = [*sorted((ROOT / "docs").rglob("*.md")), ROOT / "README.md"]
BLOCK = re.compile(r"^```python\n(.*?)^```", re.MULTILINE | re.DOTALL)

#: The file names the pages use, and the fixture each one is a copy of.
IMAGES = {
    "photo.jpg": "photo.jpeg",
    "photo_copy.jpg": "photo_copy.jpeg",
    "photo_rotated.jpg": "photo_rotated_90.jpeg",
    "photo.png": "photo.png",
    "broken.jpg": "corrupted.jpg",
}


def blocks(page: Path) -> list[str]:
    text = page.read_text(encoding="utf-8")
    return [b for b in BLOCK.findall(text) if "--8<--" not in b]


def test_pages_have_code() -> None:
    assert sum(len(blocks(p)) for p in PAGES) > 20


@pytest.mark.parametrize(
    "page",
    [p for p in PAGES if blocks(p)],
    ids=lambda p: p.relative_to(ROOT).as_posix(),
)
def test_page_code_runs(
    page: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    code = blocks(page)
    for module in ("numpy", "PIL"):
        used = any(f"import {module}" in b or f"from {module}" in b for b in code)
        if used and importlib.util.find_spec(module) is None:
            pytest.skip(f"{page.name} needs {module}")
    for name, fixture in IMAGES.items():
        shutil.copy(data(fixture), tmp_path / name)
    monkeypatch.chdir(tmp_path)
    namespace: dict[str, object] = {"__name__": "__docs__"}
    for i, block in enumerate(code):
        # The documentation's own code, run as a reader would.
        exec(compile(block, f"{page.name}[{i}]", "exec"), namespace)  # noqa: S102


CONSOLE = re.compile(r"^```console\n(.*?)^```", re.MULTILINE | re.DOTALL)


def commands(page: Path) -> list[tuple[str, str]]:
    """Each ``$ libphash …`` line of the page's console blocks, and its output."""
    found: list[tuple[str, str]] = []
    for block in CONSOLE.findall(page.read_text(encoding="utf-8")):
        for command in re.split(r"^\$ ", block, flags=re.MULTILINE)[1:]:
            line, _, output = command.partition("\n")
            found.append((line, output))
    return found


@pytest.mark.parametrize(
    ("line", "output"),
    commands(ROOT / "docs" / "guide" / "cli.md"),
    ids=lambda v: v.split("\n")[0][:40],
)
def test_command_line_prints_what_the_page_shows(
    line: str,
    output: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    needs_libjpeg_turbo("the page shows the hashes of libjpeg-turbo's decode")
    for name, fixture in IMAGES.items():
        shutil.copy(data(fixture), tmp_path / name)
    (tmp_path / "album").mkdir()
    for name in ("photo.jpg", "photo_copy.jpg", "photo.png"):
        shutil.copy(tmp_path / name, tmp_path / "album" / name)
    monkeypatch.chdir(tmp_path)
    # Standard output and error in one stream, in the order the command writes them.
    stream = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stream)
    monkeypatch.setattr(sys, "stderr", stream)
    program, *argv = shlex.split(line)
    assert program == "libphash"
    main(argv)
    # The page writes paths with "/", the command with the platform's separator.
    assert stream.getvalue() == output.replace("album/", "album" + os.sep)


FRONT_MATTER = re.compile(r"\A---\n(.*?)^---\n", re.MULTILINE | re.DOTALL)
SITE_PAGES = sorted((ROOT / "docs").rglob("*.md"))


def front_matter(page: Path) -> dict[str, str]:
    """Return the page's ``key: "value"`` lines of front matter."""
    found = FRONT_MATTER.match(page.read_text(encoding="utf-8"))
    assert found, f"{page.name} has no front matter"
    return dict(re.findall(r'^(\w+): "(.*)"$', found.group(1), re.MULTILINE))


@pytest.mark.parametrize(
    "page", SITE_PAGES, ids=lambda p: p.relative_to(ROOT / "docs").as_posix()
)
def test_page_has_a_title_and_description_for_search(page: Path) -> None:
    # The title is the page's whole <title>, which a search result cuts at about 60
    # characters; the description is its snippet, cut at about 160 and thin under 120.
    meta = front_matter(page)
    assert 10 <= len(meta.get("title", "")) <= 60
    assert 120 <= len(meta.get("description", "")) <= 160


def test_titles_and_descriptions_are_each_one_page_s() -> None:
    # Two pages with one title or one snippet compete for one search, and one loses.
    metas = [front_matter(p) for p in SITE_PAGES]
    for key in ("title", "description"):
        values = [m[key] for m in metas]
        assert len(set(values)) == len(values), key


def test_preview_image_is_the_size_cards_show() -> None:
    # PNG's IHDR: width and height, big-endian, at bytes 16 to 24.
    head = (ROOT / "docs" / "assets" / "social.png").read_bytes()[:24]
    assert head[:8] == b"\x89PNG\r\n\x1a\n"
    assert (int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")) == (
        1200,
        630,
    )

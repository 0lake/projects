from pathlib import Path

import pytest

from goat_scraper.images import download_images, slugify
from goat_scraper.parse import absolute_url, parse_breeds
from goat_scraper.report import to_dataframe, to_html

HTML = (Path(__file__).parent / "fixtures" / "goat_breeds_sample.html").read_text(encoding="utf-8")


def test_parses_rows_and_skips_empty():
    breeds = parse_breeds(HTML)
    assert [b.name for b in breeds] == ["Anglo-Nubian", "Angora", "Appenzell"]


def test_image_urls_are_absolute():
    breeds = parse_breeds(HTML)
    assert breeds[0].image_url == "https://upload.wikimedia.org/thumb/anglo.jpg"
    assert breeds[1].image_url == "https://en.wikipedia.org/w/images/angora.jpg"
    assert breeds[2].image_url == ""


def test_text_fields_are_cleaned():
    b = parse_breeds(HTML)
    assert b[0].other_names == "Nubian" and b[0].references == ""
    assert b[1].references == ""  # footnote marker [2] is stripped
    assert b[2].other_names == "Chèvre d'Appenzell, Appenzellerziege"
    assert b[0].purpose == "meat, milk"


def test_column_order_does_not_matter():
    swapped = HTML.replace("<th>Origin</th><th>Purpose</th>", "<th>Purpose</th><th>Origin</th>")
    swapped = swapped.replace("<td>meat, milk</td>", "<td>@@PURPOSE@@</td>", 1)
    first = parse_breeds(swapped)[0]
    # header says Purpose is now column 4, so the cell under it is read as purpose
    assert first.purpose == "Great Britain" and first.origin == "@@PURPOSE@@"


def test_missing_table_raises():
    with pytest.raises(ValueError):
        parse_breeds("<html><table class='wikitable'><tr><th>X</th></tr></table></html>")


def test_slugify_and_absolute_url():
    assert slugify("Chèvre d'Appenzell!", "x") == "ch_vre_d_appenzell"
    assert slugify("!!!", "fallback") == "fallback"
    assert absolute_url("//a.org/x.jpg") == "https://a.org/x.jpg"


class FakeResponse:
    content = b"jpgdata"
    def raise_for_status(self): pass


class FakeSession:
    def __init__(self): self.calls = []
    def get(self, url, timeout=0):
        self.calls.append(url)
        return FakeResponse()


def test_download_images_skips_missing_and_existing(tmp_path):
    breeds = parse_breeds(HTML)
    session = FakeSession()
    first = download_images(breeds, tmp_path, session, delay=0)
    assert len(session.calls) == 2 and first["Appenzell"] == ""
    again = download_images(breeds, tmp_path, session, delay=0)
    assert len(session.calls) == 2 and again["Anglo-Nubian"].endswith("anglo_nubian.jpg")


def test_report_and_html_are_escaped(tmp_path):
    breeds = parse_breeds(HTML)
    breeds[0].name = "<script>alert(1)</script>"
    df = to_dataframe(breeds)
    out = tmp_path / "g.html"
    to_html(df, out)
    text = out.read_text(encoding="utf-8")
    assert "<script>alert" not in text and "&lt;script&gt;" in text
    assert list(df.columns)[:2] == ["name", "image"]

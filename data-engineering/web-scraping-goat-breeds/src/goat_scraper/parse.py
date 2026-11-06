"""Parse the breeds table. Columns are detected by header text, so a changed column
order or an extra column on the page does not break the parser."""
import re
from dataclasses import dataclass, asdict
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

BASE = "https://en.wikipedia.org"

FIELD_RULES = [  # (field, substrings of the lower-cased header)
    ("image", ("image", "picture", "photo")),
    ("other_names", ("other name", "also known", "alternative", "synonym")),
    ("origin", ("origin", "country", "region")),
    ("purpose", ("purpose", "use")),
    ("references", ("ref", "note")),
    ("name", ("breed", "name")),
]


@dataclass
class Breed:
    name: str = ""
    image_url: str = ""
    other_names: str = ""
    origin: str = ""
    purpose: str = ""
    references: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def absolute_url(src: str, base: str = BASE) -> str:
    """Wikipedia uses protocol-relative (//upload...) and root-relative (/w/...) image links."""
    return urljoin(base, src) if src else ""


def _clean(text: str) -> str:
    text = re.sub(r"\[\s*\d+\s*\]", "", text)      # footnote markers like [1]
    return re.sub(r"\s+", " ", text).strip()


def _cell_text(cell: Tag) -> str:
    for sup in cell.find_all("sup"):
        sup.decompose()
    links = [a.get_text(" ", strip=True) for a in cell.find_all("a") if a.get_text(strip=True)]
    return _clean(", ".join(links) if links else cell.get_text(" ", strip=True))


def _find_table(soup: BeautifulSoup) -> Tag:
    for table in soup.find_all("table", class_="wikitable"):
        header = " ".join(th.get_text(" ", strip=True).lower() for th in table.find_all("th"))
        if "breed" in header or "origin" in header:
            return table
    raise ValueError("breeds table not found on the page")


def _column_fields(table: Tag) -> list[str | None]:
    header_cells = table.find("tr").find_all(["th", "td"])
    fields: list[str | None] = []
    for cell in header_cells:
        text = cell.get_text(" ", strip=True).lower()
        field = next((f for f, keys in FIELD_RULES if any(k in text for k in keys)), None)
        fields.append(field)
    return fields


def parse_breeds(html: str) -> list[Breed]:
    soup = BeautifulSoup(html, "html.parser")
    table = _find_table(soup)
    fields = _column_fields(table)
    breeds: list[Breed] = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all(["th", "td"])
        if not cells:
            continue
        breed = Breed()
        for field, cell in zip(fields, cells):
            if field == "image":
                img = cell.find("img")
                breed.image_url = absolute_url(img["src"]) if img and img.get("src") else ""
            elif field:
                setattr(breed, field, _cell_text(cell))
        if breed.name:
            breeds.append(breed)
    return breeds

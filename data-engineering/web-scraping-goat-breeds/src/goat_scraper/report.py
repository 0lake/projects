"""CSV and a standalone HTML gallery."""
import html
from pathlib import Path

import pandas as pd

from .parse import Breed

COLUMNS = ["name", "image", "other_names", "origin", "purpose", "references"]


def to_dataframe(breeds: list[Breed], local_images: dict | None = None) -> pd.DataFrame:
    rows = []
    for b in breeds:
        row = b.as_dict()
        row["image"] = (local_images or {}).get(b.name) or b.image_url
        rows.append(row)
    return pd.DataFrame(rows).reindex(columns=COLUMNS)


def to_html(df: pd.DataFrame, path: Path, title: str = "Goat breeds") -> None:
    def cell(value) -> str:
        return html.escape("" if pd.isna(value) else str(value))

    def image(src) -> str:
        src = "" if pd.isna(src) else str(src)
        if not src:
            return '<span class="none">no image</span>'
        return f'<img src="{html.escape(src)}" alt="" loading="lazy">'

    body = "\n".join(
        "<tr>" + f"<td><b>{cell(r['name'])}</b></td><td>{image(r['image'])}</td>"
        + "".join(f"<td>{cell(r[c])}</td>" for c in COLUMNS[2:]) + "</tr>"
        for _, r in df.iterrows()
    )
    head = "".join(f"<th>{c.replace('_', ' ').title()}</th>" for c in COLUMNS)
    path.write_text(f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
body{{font:15px/1.5 system-ui,sans-serif;margin:2rem;background:#fafafa;color:#222}}
table{{border-collapse:collapse;width:100%;background:#fff}}
th,td{{padding:.6rem .8rem;border-bottom:1px solid #e5e5e5;text-align:left;vertical-align:middle}}
th{{background:#f0f0f0;position:sticky;top:0}} img{{max-height:110px;max-width:140px;border-radius:6px}}
.none{{color:#999}}
</style><h1>{html.escape(title)}</h1><table><thead><tr>{head}</tr></thead><tbody>
{body}
</tbody></table></html>""", encoding="utf-8")

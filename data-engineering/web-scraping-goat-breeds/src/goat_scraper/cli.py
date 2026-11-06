"""goat-scraper --out output [--no-images] [--limit N]"""
import argparse
from pathlib import Path

from .fetch import URL, fetch_html, make_session
from .images import download_images
from .parse import parse_breeds
from .report import to_dataframe, to_html


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=URL)
    ap.add_argument("--out", type=Path, default=Path("output"))
    ap.add_argument("--no-images", action="store_true", help="do not download images")
    ap.add_argument("--limit", type=int, default=None, help="process only the first N breeds")
    args = ap.parse_args(argv)

    session = make_session()
    breeds = parse_breeds(fetch_html(args.url, session))[: args.limit]
    print(f"parsed {len(breeds)} breeds")

    args.out.mkdir(parents=True, exist_ok=True)
    local = {} if args.no_images else download_images(breeds, args.out / "images", session)
    df = to_dataframe(breeds, {k: str(Path(v).relative_to(args.out)) for k, v in local.items() if v})
    df.to_csv(args.out / "goat_breeds.csv", index=False)
    to_html(df, args.out / "goat_breeds.html")
    print(f"saved {args.out / 'goat_breeds.csv'} and {args.out / 'goat_breeds.html'}")


if __name__ == "__main__":
    main()

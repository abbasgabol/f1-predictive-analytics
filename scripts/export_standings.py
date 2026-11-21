"""Build the website's historical standings from Formula 1's results archive."""

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://www.formula1.com/en/results"


class StandingsTable(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.in_table = False
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.row = []
        elif self.row is not None and tag in ("td", "th"):
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None and data.strip():
            self.cell.append(data.strip())

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None
        elif tag == "table":
            self.in_table = False


def read_standings(year, kind, html_dir):
    if html_dir:
        html = (html_dir / f"standings-{year}-{kind}.html").read_text(encoding="utf-8")
    else:
        request = Request(f"{SOURCE}/{year}/{kind}", headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=25) as response:
            html = response.read().decode("utf-8")

    table = StandingsTable()
    table.feed(html)
    driver_table = kind == "drivers"
    expected = ["Pos.", "Driver", "Nationality", "Team", "Pts."] if driver_table else ["Pos.", "Team", "Pts."]
    if not table.rows or [" ".join(cell) for cell in table.rows[0]] != expected:
        raise ValueError(f"Unexpected standings columns for {year} {kind}")

    results = []
    for cells in table.rows[1:]:
        if len(cells) != len(expected):
            raise ValueError(f"Incomplete standings row for {year} {kind}: {cells}")
        values = [" ".join(cell) for cell in cells]
        if driver_table:
            position, _, _, team, points = values
            name = " ".join(cells[1][:-1])  # Formula 1 appends the three-letter abbreviation.
            results.append([position, name, points, team])
        else:
            position, team, points = values
            results.append([position, team, points])
    if len(results) < (18 if driver_table else 9) or results[0][0] != "1":
        raise ValueError(f"Incomplete standings for {year} {kind}")
    return year, "drivers" if driver_table else "constructors", results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html-dir", type=Path, help="Use previously downloaded season pages")
    args = parser.parse_args()
    years = range(2016, 2026)
    archive = {year: {} for year in years}
    jobs = [(year, kind, args.html_dir) for year in years for kind in ("drivers", "team")]
    with ThreadPoolExecutor(max_workers=5) as pool:
        for year, kind, rows in pool.map(lambda job: read_standings(*job), jobs):
            archive[year][kind] = rows

    output = json.dumps(archive, ensure_ascii=False, separators=(",", ":")) + "\n"
    (ROOT / "website" / "standings.json").write_text(output, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()

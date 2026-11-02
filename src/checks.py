"""P5 verification — reopen the database and the Excel file and check them.

Checks: 74 leads; niche split 25/25/24; every row has a name, an
address and an OSM link; no two rows share an OSM link (dedupe by
object); same-name rows sit at different coordinates (branches, not
dupes); phone/website counts match the fetch log (5/4); the Excel
file holds the same 74 rows and its Summary totals are formulas.
"""
import sqlite3
import sys
from pathlib import Path

from openpyxl import load_workbook

BASE = Path(__file__).resolve().parents[1]
DB = BASE / "data" / "processed" / "leads.db"
XLSX = BASE / "outputs" / "leads_SAMPLE.xlsx"

fails = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name} {detail}")
    if not cond:
        fails.append(name)


con = sqlite3.connect(DB)
rows = con.execute("SELECT * FROM leads").fetchall()
check("lead count = 74", len(rows) == 74, f"got {len(rows)}")
split = dict(con.execute(
    "SELECT niche, COUNT(*) FROM leads GROUP BY niche").fetchall())
check("niche split 25/25/24",
      split == {"bakery": 25, "cafe": 25, "restaurant": 24}, str(split))
check("all rows have name + address + OSM link",
      all(r[1] and r[5] and r[10] for r in rows))
check("no duplicate OSM links",
      len({r[10] for r in rows}) == len(rows))
check("all ratings honestly n/a", all(r[9] == "n/a" for r in rows))
check("phones = 5", sum(1 for r in rows if r[3]) == 5)
check("websites = 4", sum(1 for r in rows if r[4]) == 4)
dups = con.execute(
    """SELECT lower(business_name), COUNT(DISTINCT latitude || ',' || longitude)
       FROM leads GROUP BY lower(business_name) HAVING COUNT(*) > 1""").fetchall()
check("same-name rows are separate branches",
      all(n == c for _, n, c in
          [(d[0], con.execute("SELECT COUNT(*) FROM leads WHERE lower(business_name)=?",
                              (d[0],)).fetchone()[0], d[1]) for d in dups]),
      str(dups))
con.close()

wb = load_workbook(XLSX)
ws = wb["Leads"]
xrows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] is not None]
check("excel rows = 74", len(xrows) == 74, f"got {len(xrows)}")
check("excel names match database",
      {r[0] for r in xrows} == {r[1] for r in rows})
sm = wb["Summary"]
check("summary totals are formulas",
      all(str(sm.cell(row=5, column=c).value).startswith("=") for c in (2, 3, 4)))

print(f"\n{len(fails)} failures" if fails else "\nALL CHECKS PASS")
sys.exit(1 if fails else 0)

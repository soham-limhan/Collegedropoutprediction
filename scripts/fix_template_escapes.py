"""Fix \\\" sequences in extracted templates to proper quotes."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1] / "templates"
for p in ROOT.glob("*.html"):
    t = p.read_text(encoding="utf-8")
    t2 = t.replace('\\"', '"')
    if t2 != t:
        p.write_text(t2, encoding="utf-8")
        print("Fixed", p.name)

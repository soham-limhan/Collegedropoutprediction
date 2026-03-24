"""One-off: extract HOME_HTML etc. from app.py into templates/."""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
text = (ROOT / "app.py").read_text(encoding="utf-8")
mapping = {
    "HOME_HTML": "home.html",
    "DASHBOARD_HTML": "dashboard.html",
    "STUDENTS_VIEW_HTML": "students_view.html",
    "PRINT_REPORT_HTML": "print_report.html",
}
(ROOT / "templates").mkdir(exist_ok=True)
for var, fname in mapping.items():
    m = re.search(var + r' = """(.*?)"""', text, re.DOTALL)
    if not m:
        raise SystemExit(f"Missing {var}")
    (ROOT / "templates" / fname).write_text(m.group(1), encoding="utf-8")
    print(f"Wrote {fname} ({len(m.group(1))} chars)")

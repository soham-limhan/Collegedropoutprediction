"""Remove inline HTML string constants from app.py (templates moved to templates/)."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
text = (ROOT / "app.py").read_text(encoding="utf-8")
for name in ["HOME_HTML", "DASHBOARD_HTML", "STUDENTS_VIEW_HTML", "PRINT_REPORT_HTML"]:
    pattern = name + r' = """(.*?)"""\s*\n'
    text, n = re.subn(pattern, "", text, count=1, flags=re.DOTALL)
    if n != 1:
        raise SystemExit(f"Expected to remove {name} once, got {n}")
(ROOT / "app.py").write_text(text, encoding="utf-8")
print("Stripped inline HTML blocks from app.py")

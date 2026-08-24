"""Deterministic structural verifier for Batch 3's independent project."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "second_project"
required = {"index.html", "style.css", "app.js"}
actual = {p.name for p in ROOT.iterdir() if p.is_file()}
missing = required - actual
if missing:
    raise SystemExit(f"missing files: {sorted(missing)}")
html = (ROOT / "index.html").read_text()
js = (ROOT / "app.js").read_text()
checks = {
    "form": "task-form" in html and "task-input" in html,
    "render": "function render" in js,
    "persistence": "localStorage" in js,
    "blank_guard": "if (!text) return" in js,
    "toggle": "task.done = !task.done" in js,
    "delete": "tasks = tasks.filter(t => t.id !== task.id)" in js,
    "clear_completed": "tasks = tasks.filter(t => !t.done)" in js,
    "safe_json": "catch (_)" in js,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit(f"failed checks: {failed}")
print("BATCH3_STRUCTURAL_VERIFY_OK", len(checks))

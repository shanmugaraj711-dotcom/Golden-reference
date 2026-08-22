from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(os.environ.get("FACTORY_WORKSPACE", "generated-project"))


def main() -> int:
    if not ROOT.exists():
        raise SystemExit("generated workspace missing")
    files = [p for p in ROOT.rglob("*") if p.is_file()]
    if not files:
        raise SystemExit("generated project is empty")
    names = {p.name.lower() for p in files}
    if "index.html" in names:
        index = next(p for p in files if p.name.lower() == "index.html")
        text = index.read_text(encoding="utf-8", errors="replace").lower()
        if "<html" not in text or "</html>" not in text:
            raise SystemExit("index.html failed basic HTML gate")
        if "<script" in text:
            # Syntax-check inline JavaScript blocks when Node is available.
            import re
            scripts = re.findall(r"<script[^>]*>(.*?)</script>", text, flags=re.S)
            for i, script in enumerate(scripts):
                if script.strip():
                    probe = ROOT / f".factory-js-{i}.js"
                    probe.write_text(script, encoding="utf-8")
                    try:
                        subprocess.run(["node", "--check", str(probe)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    finally:
                        probe.unlink(missing_ok=True)
    print(f"PROJECT_GATE_OK files={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

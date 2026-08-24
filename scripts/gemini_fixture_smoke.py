import json
import os
import sys
import urllib.error
import urllib.request

instruction = sys.argv[1] if len(sys.argv) > 1 else "Inspect the fixture and report exactly what changed."
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEY is not configured")

fixture = os.path.join("fixtures", "codex")
if not os.path.isdir(fixture):
    raise SystemExit("fixture directory not found: " + fixture)

files = []
for root, _, names in os.walk(fixture):
    for name in sorted(names):
        path = os.path.join(root, name)
        files.append(os.path.relpath(path, fixture))

prompt = (
    "You are running a controlled Project Factory smoke test. "
    "Do not request, expose, or use secrets. "
    "Return concise JSON with keys status, instruction, files, summary.\n"
    f"Instruction: {instruction}\nFiles: {files}"
)

# Use the current model explicitly returned by the API for this account.
model = "gemini-3.5-flash-lite"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
payload = {"contents": [{"parts": [{"text": prompt}]}]}
req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.load(response)
except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", errors="replace")
    raise SystemExit(f"Gemini API HTTP {exc.code}: {body}")

text = data["candidates"][0]["content"]["parts"][0]["text"]
print("GEMINI_FIXTURE_SMOKE_OK")
print(json.dumps({"status": "passed", "files": files, "response": text}, ensure_ascii=False))

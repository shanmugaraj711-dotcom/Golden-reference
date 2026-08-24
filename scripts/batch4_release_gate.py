#!/usr/bin/env python3
"""Deterministic Batch 4 release gate.

This verifier is intentionally offline: it validates the replay contract and
acceptance evidence without starting a workflow, calling a model, or deploying.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "schemas" / "replay-contract.json"
FIXTURES = ROOT / "fixtures"
REQUIRED_PROJECTS = ["sample_project", "second_project"]
EXPECTED = list(range(1, 11))

def fail(message):
    print(f"RELEASE_GATE_FAIL: {message}")
    raise SystemExit(1)

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
required = {"contractVersion", "projectId", "fixture", "request", "expectedStages", "determinism"}
if set(contract) != required:
    fail("contract keys drifted")
if contract["contractVersion"] != "1.0":
    fail("unsupported contract version")
if contract["expectedStages"] != EXPECTED:
    fail("stage coverage must be exactly 1..10")
if contract["determinism"] != {
    "sameInputSamePlan": True,
    "noHiddenNetworkDependency": True,
    "boundedRetries": True,
}:
    fail("determinism guarantees are incomplete")

for project in REQUIRED_PROJECTS:
    directory = FIXTURES / project
    if not (directory / "index.html").is_file():
        fail(f"{project}: index.html missing")
    if not (directory / "app.js").is_file():
        fail(f"{project}: app.js missing")
    if not (directory / "style.css").is_file():
        fail(f"{project}: style.css missing")

print("RELEASE_GATE_OK")
print("projects=sample_project,second_project")
print("stages=1..10")
print("network=none")

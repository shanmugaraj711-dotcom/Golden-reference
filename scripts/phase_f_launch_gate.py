#!/usr/bin/env python3
"""Phase F launch-readiness gate.

Fails closed: environment-dependent launch evidence is never inferred from
unit tests or deployment status alone. The gate can be run locally/CI with
observable evidence supplied as JSON.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED = (
    "model_runtime_provisioned",
    "local_model_health",
    "coding_agent_smoke",
    "second_project_e2e",
    "vercel_delivery",
    "cost_quality_measurement",
)


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, help="JSON evidence file")
    args = parser.parse_args()
    evidence = load(args.evidence)
    failed = [key for key in REQUIRED if evidence.get(key) is not True]
    for key in REQUIRED:
        print(("PASS" if key not in failed else "FAIL") + f"  {key}")
    if failed:
        print("RESULT NOT_READY: missing observable launch evidence")
        return 1
    print("RESULT READY_FOR_LAUNCH")
    return 0


if __name__ == "__main__":
    sys.exit(main())

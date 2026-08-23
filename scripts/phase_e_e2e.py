#!/usr/bin/env python3
"""Phase E production E2E acceptance runner.

This runner deliberately separates read-only production smoke checks from any
mutation. It validates the live Project Factory surface, delivery-model
contracts, and (when supplied) a persisted project record. Full Deploy/Managed
acceptance still requires a fresh external destination and its observable
health/deployment evidence; this script never fabricates that evidence.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from src.project_factory.delivery import DeliveryRequest, plan_delivery


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def fetch_json(url: str) -> tuple[int, Any]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body)


def check_contracts() -> list[Check]:
    checks: list[Check] = []
    cases = [
        ("transfer", "none", True, False, True, False),
        ("deploy", "vercel", True, True, False, False),
        ("managed", "vercel", True, True, False, True),
    ]
    for mode, target, repo, vercel, handoff, maintenance in cases:
        plan = plan_delivery(DeliveryRequest("phase-e", mode, "artifact", target))
        actual = (
            plan.repository_required,
            plan.vercel_required,
            plan.handoff_required,
            plan.maintenance_expected,
        )
        expected = (repo, vercel, handoff, maintenance)
        checks.append(Check(f"delivery-contract:{mode}", actual == expected, f"actual={actual} expected={expected}"))
    return checks


def check_live(base_url: str, project_id: str = "") -> list[Check]:
    base = base_url.rstrip("/")
    checks: list[Check] = []
    status, payload = fetch_json(f"{base}/api")
    checks.append(Check("live-api", status == 200 and payload.get("status") == "ok", f"HTTP {status}; {payload}"))

    project_url = f"{base}/api/projects"
    if project_id:
        project_url += "?id=" + urllib.parse.quote(project_id, safe="")
    status, payload = fetch_json(project_url)
    project = payload.get("project") if isinstance(payload, dict) else None
    shape_ok = isinstance(project, dict) and all(
        key in project for key in ("projectId", "customerId", "lifecycleState", "verification", "ownership", "deliveryEvidence")
    )
    checks.append(Check("project-read", status == 200 and payload.get("status") == "ok" and shape_ok, f"HTTP {status}; shape={shape_ok}"))

    dashboard = urllib.request.urlopen(urllib.request.Request(f"{base}/", headers={"Accept": "text/html"}), timeout=15).read().decode("utf-8")
    checks.append(Check("dashboard", "Customer Delivery" in dashboard and "PROJECT FACTORY" in dashboard, "dashboard markers present"))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", help="Live Project Factory URL")
    parser.add_argument("--project-id", default="", help="Optional persisted Firestore project id")
    args = parser.parse_args()

    checks = check_contracts()
    if args.base_url:
        try:
            checks.extend(check_live(args.base_url, args.project_id))
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            checks.append(Check("live-smoke", False, repr(exc)))

    failed = [check for check in checks if not check.passed]
    for check in checks:
        print(("PASS" if check.passed else "FAIL") + f"  {check.name}  {check.detail}")

    if not args.base_url:
        print("INFO  live-smoke  skipped: pass --base-url for production evidence")
    if failed:
        print(f"RESULT FAIL ({len(failed)} failed)")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

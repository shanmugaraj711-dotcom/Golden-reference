"""Deterministic Vercel failure classification and safe recovery planning.

This module intentionally does not auto-edit arbitrary application code. It turns
known deployment failures into bounded repair plans that an operator/deployer can
execute safely and records why a repair was selected.
"""
from __future__ import annotations
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class RecoveryPlan:
    category: str
    action: str
    confidence: str
    retryable: bool
    reason: str

_PATTERNS = [
    ("runtime_config", re.compile(r"Function Runtimes must have a valid version|invalid runtime", re.I),
     "validate/remove stale runtime configuration and redeploy", "high"),
    ("missing_dependency", re.compile(r"ModuleNotFoundError|Cannot find module|No module named", re.I),
     "synchronize the deployment dependency manifest and redeploy", "high"),
    ("function_import", re.compile(r"could not import .*api/|ImportError|SyntaxError", re.I),
     "run the application import/compile check, repair the failing import, then redeploy", "high"),
    ("environment", re.compile(r"environment variable|missing.*env|FIREBASE_.*not configured", re.I),
     "verify required deployment environment configuration without exposing secret values", "medium"),
    ("function_invocation", re.compile(r"FUNCTION_INVOCATION_FAILED|Function Invocation Failed", re.I),
     "inspect the function exception, run the endpoint smoke test, then redeploy only after the root cause is fixed", "medium"),
]

def classify_failure(log: str) -> RecoveryPlan:
    text = log or ""
    for category, pattern, action, confidence in _PATTERNS:
        if pattern.search(text):
            return RecoveryPlan(category, action, confidence, True, f"matched known deployment failure: {category}")
    return RecoveryPlan("unknown", "quarantine deployment, preserve logs, and require diagnosis before retry", "low", False, "no safe deterministic repair matched")

def recovery_event(log: str, attempt: int = 1) -> dict:
    plan = classify_failure(log)
    return {"attempt": max(1, int(attempt)), "category": plan.category, "action": plan.action,
            "confidence": plan.confidence, "retryable": plan.retryable, "reason": plan.reason}

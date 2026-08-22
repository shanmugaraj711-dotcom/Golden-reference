"""Safe, deterministic deployment-recovery execution state machine.

This module never edits production source automatically. It records a bounded
recovery attempt and returns an explicit action for an external deployer.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

MAX_ATTEMPTS = 3

@dataclass
class RecoveryAction:
    classification: str
    action: str
    attempt: int
    terminal: bool
    reason: str
    created_at: str


def classify(message: str) -> str:
    text = (message or "").lower()
    if "function runtimes must have a valid version" in text:
        return "invalid_runtime"
    if "modulenotfounderror" in text or "no module named" in text:
        return "missing_dependency"
    if "could not import" in text or "importerror" in text:
        return "import_failure"
    if "missing" in text and ("environment" in text or "env" in text or "secret" in text):
        return "missing_configuration"
    if "function_invocation_failed" in text:
        return "function_failure"
    return "unknown"


def plan(message: str, attempt: int = 1) -> RecoveryAction:
    classification = classify(message)
    now = datetime.now(timezone.utc).isoformat()
    if attempt < 1:
        attempt = 1
    if attempt > MAX_ATTEMPTS:
        return RecoveryAction(classification, "quarantine", attempt, True,
                              "recovery attempt limit exceeded", now)
    actions = {
        "invalid_runtime": "validate_vercel_runtime_config",
        "missing_dependency": "validate_dependency_manifest",
        "import_failure": "validate_python_import_graph",
        "missing_configuration": "validate_required_environment_configuration",
        "function_failure": "run_function_health_check",
        "unknown": "manual_review",
    }
    action = actions[classification]
    terminal = classification == "unknown" or attempt >= MAX_ATTEMPTS
    reason = "safe automated validation before redeploy"
    if terminal and classification == "unknown":
        reason = "unknown failure is quarantined; no blind production mutation"
    return RecoveryAction(classification, action, attempt, terminal, reason, now)


def next_action(message: str, attempt: int = 1) -> dict:
    return asdict(plan(message, attempt))

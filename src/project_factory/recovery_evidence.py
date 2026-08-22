"""Persistable deployment recovery evidence helpers."""
from __future__ import annotations
from datetime import datetime, timezone

VALID_STAGES={"FAILED","DIAGNOSING","REPAIRING","REDEPLOYING","VERIFYING","RECOVERED","QUARANTINED"}

def event(stage:str, classification:str, action:str, attempt:int, message:str=""):
    stage=stage.upper()
    if stage not in VALID_STAGES: raise ValueError("invalid recovery stage")
    return {
        "stage":stage,
        "classification":classification,
        "action":action,
        "attempt":attempt,
        "message":message[:1000],
        "createdAt":datetime.now(timezone.utc).isoformat(),
    }

def append(history, item, limit=50):
    history=list(history or [])
    history.append(item)
    return history[-limit:]

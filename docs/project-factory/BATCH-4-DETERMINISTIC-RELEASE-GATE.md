# Batch 4 — Deterministic replay & release gate

## Goal

Batch 4 closes the generalization loop without adding another automated job. The factory now has a small, offline release gate that can prove the two independent fixtures still satisfy the same 10-stage contract.

## What is protected

1. The replay contract has a pinned version and exact stage coverage (1–10).
2. Determinism requirements are explicit: same input produces the same plan, the gate has no hidden network dependency, and retries are bounded.
3. Both `sample_project` and `second_project` must contain the same structural entry points: `index.html`, `style.css`, and `app.js`.
4. The gate is deterministic and offline; it does not call Gemini, Codex, GitHub Actions, or a deployment target.

## Operator rule

Run `python scripts/batch4_release_gate.py` before accepting a future batch. A non-zero exit means the batch is not ready. A zero exit prints `RELEASE_GATE_OK`.

## Scope boundary

This batch deliberately does **not** enable any workflow or production autonomy. Runtime/model smoke tests remain manual controls. Deployment remains downstream of explicit destination configuration and health verification.

## Completion evidence

Batch 4 is complete when the release gate passes on `main`, the two fixtures remain present, and no new workflow is enabled.

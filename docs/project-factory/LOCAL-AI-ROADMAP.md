# Local-First AI Roadmap

## Goal

Reduce dependence on paid model APIs without pretending that a proprietary frontier model can be copied. The factory owns the orchestration, routing, evaluation, memory, evidence, security, and product experience.

## Architecture

```text
Customer request
      ↓
Project Factory
      ↓
Model Router
  ↙    ↓     ↘
local  external  future-in-house
  ↓      ↓          ↓
      response
         ↓
planning → coding → testing → verification
```

## Stage A — provider independence

All model calls use the `ModelProvider` contract. No factory component should depend directly on one vendor SDK.

## Stage B — local inference

Add an approved open-weight local provider behind the same interface. Start with a small coding-capable model that can run on available infrastructure. Measure quality, latency, memory/VRAM requirements and cost per successful task before expanding.

## Stage C — routing

Prefer local inference when quality meets the task threshold and cost policy. Fall back to external providers only when allowed and beneficial. Every decision should be observable through evidence and cost telemetry.

## Stage D — specialization

Use accumulated evaluation data to build task-specific components: planner, code editor, debugger, verifier and security reviewer. Fine-tune or distill only when measured gains justify the complexity.

## Stage E — owned intelligence

Only after the evaluation corpus and economics justify it should the project train or fine-tune an in-house model. The target is not a copy of Claude, Gemini or Codex; it is an owned engineering model optimized for Project Factory tasks.

## Zero-cost claim

Local inference can remove per-request API fees, but it is not literally free: hardware, electricity, storage, maintenance and engineering have costs. The business target is **near-zero marginal model API cost for suitable workloads**, not zero total cost.

## Non-negotiable evaluation

A local model replaces an external model only when it passes the same acceptance/evaluation gates. Cheaper output that produces more failures is not cheaper at the product level.

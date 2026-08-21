# Project Factory AI Strategy

## The decision

We should **not clone proprietary Claude, Gemini, or Codex models**. Their weights, training systems, and proprietary services are not ours to reproduce.

We should instead build our own **AI Engineering OS** and make the underlying model replaceable.

The customer buys the outcome: a working project. They do not buy access to a particular model.

## Product promise

> **Tell us what you want built. We build it, test it, fix it, verify it, and deliver it. One project price. No separate model subscription required from the customer.**

The exact price must be determined from project scope and our measured infrastructure cost; a low-cost entry package such as ₹499 can be offered only for a tightly bounded scope.

## Architecture

```text
Customer
   |
   v
Project Factory
   |
   +--> Planner
   +--> Model Router
   |      +--> local/open-weight model
   |      +--> approved external model
   |      +--> future in-house model
   |
   +--> Coding Worker
   +--> Test Worker
   +--> Debug Worker
   +--> Verification Worker
   +--> Security Worker
   |
   v
Evidence + Checkpoint
   |
   v
Working Project
```

## Local-first strategy

We should build a **Local Model Provider** interface now, but not pretend that local inference is free.

A local/open-weight model can remove per-token API charges, but it still has costs:

- GPU/CPU hardware
- RAM/VRAM
- electricity
- hosting
- storage
- model downloads
- inference latency
- maintenance and upgrades

Therefore the economic target is **lower marginal cost and model independence**, not zero cost.

## Provider abstraction

The factory should depend on a provider contract rather than a vendor SDK:

```text
ModelProvider
  - plan()
  - code()
  - debug()
  - review()
  - summarize()
```

Providers can then be implemented independently:

- `ExternalProvider` — approved third-party API
- `LocalProvider` — self-hosted/open-weight model server
- `FutureInHouseProvider` — our own trained/specialized model

The factory remains unchanged when a provider changes.

## Build our moat, not a clone

Our proprietary assets should be:

1. Project orchestration
2. Task decomposition
3. Persistent project memory
4. Tool/workspace control
5. Evidence model
6. Automated verification
7. Failure diagnosis and repair loops
8. Model routing and cost optimization
9. Project templates and reusable engineering knowledge
10. Evaluation datasets generated from real build outcomes

This is the part that becomes increasingly difficult to copy as usage grows.

## Model ownership roadmap

### Stage A — now
Use approved external models where they provide the best quality. Keep them behind our provider interface.

### Stage B
Add a self-hosted open-weight model for selected tasks where quality/cost is acceptable.

### Stage C
Route each task to the cheapest provider that meets its quality threshold.

### Stage D
Use our accumulated, legally usable task/evaluation data to fine-tune or train specialized models for planning, coding, debugging, and verification.

### Stage E
Move more workloads to our own inference stack as economics justify it.

## Important business rule

Do not market the product as "no AI cost" or "unlimited projects for ₹499" until measured economics prove it.

Market the customer benefit instead:

> **No separate AI subscriptions. One simple project price. We handle the AI engineering infrastructure.**

Internally, optimize cost aggressively.

## Success metric

The long-term goal is not to eliminate every external model. It is to make the customer product independent of any single model vendor while continuously lowering cost per successfully delivered project.

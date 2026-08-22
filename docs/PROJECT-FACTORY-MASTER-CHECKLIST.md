# Project Factory — Master Completion Checklist

## Product
- [x] Customer-first product definition
- [x] Package/scope concept
- [x] Model-independent architecture
- [x] Local-first strategy
- [x] External fallback strategy

## Factory core
- [x] Deterministic orchestration
- [x] Task state
- [x] Evidence model
- [x] Bounded repair loop
- [x] Checkpoint/resume
- [x] Release gate
- [x] Project adapter
- [x] Coding-agent boundary
- [x] Factory runner

## Verification
- [x] Happy-path fixture
- [x] Failure fixture
- [x] Repair fixture
- [x] Exception fixture
- [x] Repair-budget fixture
- [x] Resume fixture
- [x] Input validation fixture
- [x] Agent adapter tests
- [x] Runner integration test
- [x] CI workflow

## AI independence
- [x] Vendor-neutral provider contract
- [x] Model router architecture
- [x] Local model target
- [x] External model fallback
- [x] Future in-house model boundary
- [ ] Live model runtime: requires operator-selected infrastructure/configuration
- [ ] Production-scale inference: requires measured workload and infrastructure budget

## Product delivery
- [x] GitHub as source/control plane
- [x] Vercel deployment target documented
- [x] Customer does not need local development tools
- [x] Second-project proof definition
- [ ] Live second-project execution: requires configured model runtime

## Hard truth

The software architecture is implemented as far as possible without choosing and provisioning paid/physical inference infrastructure. A Git repository cannot execute an LLM by itself. The remaining unchecked items are infrastructure-dependent, not missing design work.

## Definition of complete for this repository milestone

The repository is complete when the architecture, contracts, deterministic gates, adapters, safety boundaries, and reproducible test suite are present. Live model execution is an environment configuration step and must be verified with real runtime evidence before claiming production autonomy.

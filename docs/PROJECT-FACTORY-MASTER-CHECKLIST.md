# Project Factory — Master Completion Checklist

## Product
- [x] Customer-first product definition
- [x] Package/scope concept
- [x] Model-independent architecture
- [x] Local-first strategy
- [x] External fallback strategy
- [x] Customer promise: finished project, not model access

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
- [x] Local-provider contract tests
- [x] Cost-ceiling routing tests
- [x] CI workflow
- [x] Non-negotiable quality gates

## AI independence
- [x] Vendor-neutral provider contract
- [x] Model router architecture
- [x] Self-hosted OpenAI-compatible local provider
- [x] Local model target
- [x] External model fallback
- [x] Future in-house model boundary
- [x] Zero-cost-first policy: paid fallback disabled by default
- [ ] Live model runtime: requires operator-selected infrastructure/configuration
- [ ] Production-scale inference: requires measured workload and infrastructure budget

## Product delivery
- [x] GitHub as source/control plane
- [x] Vercel deployment target documented
- [x] Customer does not need local development tools
- [x] Second-project proof definition
- [x] Launch gate documented
- [ ] Live second-project execution: requires configured model runtime

## Infrastructure handoff — USER SIDE, LAST
- [ ] Select compute environment
- [ ] Install/pin approved open-weight coding model
- [ ] Expose private OpenAI-compatible endpoint
- [ ] Configure model endpoint in runtime environment
- [ ] Run local-model smoke test
- [ ] Run second-project end-to-end proof
- [ ] Measure real variable delivery cost

## Non-negotiable business rules

- **Spend ₹0 before revenue unless the owner explicitly approves otherwise.**
- **Zero-cost-first does not mean low quality.** Build, test, security, UX, verification, regression and evidence gates remain mandatory.
- Never claim a live model or project is working without observable execution evidence.
- Model choice is an implementation detail; the customer buys the finished project.

## Hard truth

Repository-side engineering is complete for the current milestone. The remaining unchecked items require an actual inference runtime and real execution evidence. GitHub alone cannot execute an LLM.

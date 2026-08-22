# Quality Gates

Zero-cost-first does **not** mean lower quality.

A project is deliverable only when every applicable gate passes:

1. **Scope** — requested package and acceptance criteria are explicit.
2. **Build** — project builds successfully.
3. **Tests** — automated tests pass.
4. **Security** — no obvious credential or unsafe execution violation is introduced.
5. **UI/UX** — customer-facing flow is usable and understandable.
6. **Verification** — acceptance criteria are independently checked.
7. **Regression** — existing protected behavior remains green.
8. **Evidence** — results are recorded in the project checkpoint.

Cost optimization may choose a cheaper capable model/provider, but it must never lower a required acceptance gate.

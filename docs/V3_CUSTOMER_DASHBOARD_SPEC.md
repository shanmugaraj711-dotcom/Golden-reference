# V3 Customer Dashboard Contract

## Overview
The dashboard is the single customer-facing view of a Factory project. It must expose state and evidence, not internal implementation details.

## Sections
- Project: name, brief, delivery model, version.
- Progress: current lifecycle state and next customer action.
- Preview: preview URL and approval/change-request controls.
- Delivery: repository, hosting target, production URL and deployment status.
- Verification: quality gate, deployment and live health-check evidence.
- Ownership: repository/hosting ownership and handoff status.
- Maintenance: managed support status, current version and recent changes.

## Allowed states
INTAKE, PLANNING, GENERATING, REVIEW, APPROVED, DELIVERING, VERIFYING, LIVE, HANDED_OFF, MANAGED, BLOCKED_AUTHORIZATION, GENERATION_FAILED, QUALITY_FAILED, DELIVERY_FAILED, HEALTHCHECK_FAILED.

## Customer actions
- Approve preview
- Request changes
- Confirm delivery destination
- View live project
- View handoff information
- View maintenance status

## Safety
Customers must never see Gemini keys, deployment tokens, internal provider errors containing secrets, or internal PromptStudio infrastructure credentials.

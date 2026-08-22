from __future__ import annotations

from dataclasses import dataclass
import re

from .delivery import DeliveryPlan

_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


@dataclass(frozen=True)
class GitHubDeliveryPlan:
    repository: str
    branch: str
    commit_message: str
    create_pull_request: bool


def plan_github_delivery(
    plan: DeliveryPlan,
    repository: str,
    branch: str = "factory/delivery",
) -> GitHubDeliveryPlan:
    if not _REPO.fullmatch(repository.strip()):
        raise ValueError("repository must use owner/name format")
    branch = branch.strip()
    if not branch or branch in {"main", "master"}:
        raise ValueError("delivery must use a non-default branch")

    return GitHubDeliveryPlan(
        repository=repository.strip(),
        branch=branch,
        commit_message=f"factory: deliver {plan.project_name}",
        create_pull_request=True,
    )

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class VercelDeploymentTarget:
    project_name: str
    production_url: str


def validate_vercel_target(target: VercelDeploymentTarget) -> VercelDeploymentTarget:
    name = target.project_name.strip()
    url = target.production_url.strip()
    parsed = urlparse(url)
    if not name:
        raise ValueError("project_name is required")
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("production_url must be an HTTPS URL")
    return VercelDeploymentTarget(name, url)

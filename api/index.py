"""Vercel entrypoint for Project Factory.

This intentionally starts as a dependency-free health endpoint. The factory
engine remains in src/project_factory; AI provider wiring will be added behind
server-side environment secrets after the deployment gate is green.
"""

import json


def handler(request):
    """Return a small deployment-safe health response."""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "service": "project-factory",
                "status": "ok",
                "engine": "project_factory",
            }
        ),
    }

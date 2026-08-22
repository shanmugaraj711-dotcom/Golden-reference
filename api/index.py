"""Vercel entrypoint for Project Factory.

Minimal dependency-free deployment health endpoint. The factory engine stays
in the repository and provider wiring will be added after this deployment gate.
"""

import json


def app(request):
    """Return a deployment-safe health response."""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "service": "project-factory",
            "status": "ok",
            "engine": "project_factory",
        }),
    }


# Keep the conventional Vercel handler name available as well.
handler = app

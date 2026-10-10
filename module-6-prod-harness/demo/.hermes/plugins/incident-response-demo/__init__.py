"""Load the repository-owned incident-response plugin implementation."""

import os
from pathlib import Path
import sys


def register(ctx):
    configured = os.environ.get("INCIDENT_DEMO_DIR", "").strip()
    demo_dir = (
        Path(configured).resolve()
        if configured
        else Path(__file__).resolve().parents[3]
    )
    demo_path = str(demo_dir)
    while demo_path in sys.path:
        sys.path.remove(demo_path)
    sys.path.insert(0, demo_path)
    if configured:
        from plugin_impl import register as register_implementation
    else:
        from plugin_impl import register_for_validation

        def register_implementation(context):
            register_for_validation(context, demo_dir)

    register_implementation(ctx)

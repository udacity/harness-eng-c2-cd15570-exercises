"""Load the exercise implementation from its repository-owned source."""

from __future__ import annotations

import os
from pathlib import Path
import sys


def register(ctx):
    exercise_dir = Path(os.environ["XYZ_HERMES_EXERCISE_DIR"]).resolve()
    solution_dir = exercise_dir.parent
    if str(solution_dir) not in sys.path:
        sys.path.insert(0, str(solution_dir))

    if os.environ.get("XYZ_HERMES_MODE") == "smoke":
        from hermes.baseline_plugin import register as register_implementation
    else:
        from hermes.configured_plugin import register as register_implementation

    register_implementation(ctx)

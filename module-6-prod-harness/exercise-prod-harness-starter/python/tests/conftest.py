"""Make the solution package importable regardless of pytest's working directory."""

from pathlib import Path
import sys


SOLUTION_DIR = Path(__file__).resolve().parents[2]
if str(SOLUTION_DIR) not in sys.path:
    sys.path.insert(0, str(SOLUTION_DIR))

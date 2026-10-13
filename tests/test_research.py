"""Bridge test runner for research record tests under tests/."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from scripts.tests.test_research import ResearchRecordTests

__all__ = ["ResearchRecordTests"]

"""
Pytest configuration for fprime-xtce tests.
"""
import sys
from pathlib import Path

# Add src directory to Python path so tests can import fprime_xtce module
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import the analyzer module with pybind11
try:
    # This is the correct way to import the C++ function through pybind11
    from .default_analyzer import compute_analysis
except ImportError as e:
    import os
    import sys
    print(f"Error importing default_analyzer: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    raise

# Import the Python components
from .analyzer_agent import atk_analyzer

__all__ = ["compute_analysis", "atk_analyzer"]
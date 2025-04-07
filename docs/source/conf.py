# At the top after imports
import os
import sys
import sphinx


html_theme = "sphinx_rtd_theme"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# Add this debugging code
package_path = os.path.abspath('../..')
print(f"Package path: {package_path}")
print(f"Python path: {sys.path}")
print(f"Sphinx version: {sphinx.__version__}")

sys.path.insert(0, os.path.abspath('../..'))


# Try to import your module to verify it works
try:
    import amaceing_toolkit
    print(f"Successfully imported amaceing_toolkit: {amaceing_toolkit.__file__}")
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import platform
import sys
import os

# Read requirements.txt
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if not line.startswith("//")]

# Set compiler flags for OpenMP and optimization
extra_compile_args = []
extra_link_args = []

if platform.system() == "Linux":
    print("Linux detected")
    extra_compile_args.extend(['-fopenmp', '-O3']) 
    extra_link_args.append('-fopenmp')
elif platform.system() == "Darwin": # macOS
    extra_compile_args.extend(['-Xpreprocessor', '-fopenmp', '-O3']) 
    extra_link_args.extend(['-lomp'])
elif platform.system() == "Windows":
    extra_compile_args.extend(['/openmp', '/O2'])

print("Current directory:", os.getcwd())
print("Include directories:", ["src/amaceing_toolkit/trajec_ana"])
print("Source files exist:", 
      os.path.exists("src/amaceing_toolkit/trajec_ana/default_analyzer_bindings.cpp"), 
      os.path.exists("src/amaceing_toolkit/trajec_ana/default_analyzer.cpp"))

ext_modules = [
    Pybind11Extension(
        "amaceing_toolkit.trajec_ana.default_analyzer",
        ["src/amaceing_toolkit/trajec_ana/default_analyzer_bindings.cpp", 
         "src/amaceing_toolkit/trajec_ana/default_analyzer.cpp"],
        include_dirs=["src/amaceing_toolkit/trajec_ana"],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
]

setup(
    ext_modules=ext_modules,
    install_requires=requirements,
    cmdclass={"build_ext": build_ext},
)
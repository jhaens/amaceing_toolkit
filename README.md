# aMACEing_toolkit

![GitHub Release](https://img.shields.io/github/v/release/jhaens/amaceing_toolkit)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/jhaens/amaceing_toolkit)
[![Documentation Status](https://app.readthedocs.org/projects/amaceing-toolkit/badge/)](https://amaceing-toolkit.readthedocs.io/en/latest/)
[![Presentation](https://img.shields.io/badge/Presentation-PDF-green)](https://cloud.tu-ilmenau.de/s/oYzns2qkKNYLS3L)
<!--- [![arXiv](https://img.shields.io/badge/arXiv-<INDEX>-<COLOR>.svg)](https://arxiv.org/abs/<INDEX>) -->


## Table of Contents
- [Description](#description)
- [Supported Simulation Engines](#supported-simulation-engines)
- [Installation](#installation)
  - [(i) Installation from source](#i-installation-from-source)
  - [(ii) Installation via pip](#ii-installation-via-pip)
- [Usage](#usage)
  - [Command line interface](#command-line-interface)
  - [Python API](#python-api)
- [Documentation](#documentation)
- [Examples](#examples)
- [Citation](#citation)
- [License](#license)


## Description
aMACEing_toolkit is a scientific software package that facilitates the creation, execution, and analysis of molecular dynamics simulations using multiple simulation engines. It provides a unified workflow for quantum-mechanical calculations with CP2K and machine-learned interatomic potentials (MLIPs) including MACE, MatterSim, SevenNet, ORB and Grace.

The toolkit offers:

1. **Input Generation**: Easy-to-use interactive interfaces and API functions for creating input files for multiple simulation engines
2. **Workflow Management**: Consistent workflow across different software packages
3. **Trajectory Analysis**: Fast tools for analyzing simulation outputs (RDF, MSD, SMSD, vector autocorrelation)
4. **Model Evaluation**: Utilities to assess and compare MLIP performance against reference data
5. **Run Logging**: Tracking and documentation of simulation runs and fine-tuned models

## Supported Simulation Engines

| Engine | Simulation Types | File Formats |
| ------ | --------------- | ----------- |
| CP2K | GEO_OPT, CELL_OPT, MD, REFTRAJ, ENERGY | Input files |
| MACE | GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC, FINETUNE, FINETUNE_MULTIHEAD | ASE, LAMMPS |
| MatterSim | GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC, FINETUNE | ASE |
| SevenNet | GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC, FINETUNE | ASE, LAMMPS |
| ORB | GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC, FINETUNE | ASE |
| Grace | GEO_OPT, CELL_OPT, MD, MULTI_MD, RECALC, FINETUNE | ASE, LAMMPS |

## Installation


### (i) Installation from source (recommended)

1. Create a virtual environment:
   ```bash
   conda create -n atk python=3.12
   conda activate atk
   ```

2. Install PyTorch:
   ```bash
   pip install torch torchvision torchaudio
   ```
   For CPU-only systems:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

3. Install aMACEing_toolkit:
   ```bash
   git clone https://github.com/jhaens/amaceing_toolkit.git
   cd amaceing_toolkit
   pip install -r requirements.txt
   pip install .
   ```

4. (Optional) For accelerated MACE performance on CUDA systems:
   ```bash
   # CUDA 11
   pip install cuequivariance cuequivariance-torch cuequivariance-ops-torch-cu11
   # CUDA 12
   pip install cuequivariance cuequivariance-torch cuequivariance-ops-torch-cu12
   # Older Mace Versions (< 0.3.11):
   pip install cuequivariance==0.1.0 cuequivariance-torch==0.1.0 cuequivariance-ops-torch-cu12==0.1.0
   ```

5. (Optional) For MatterSim and SevenNet, create a separate environment:
   ```bash
   conda create -n atk_ms7n python=3.9
   conda activate atk_ms7n
   pip install torch torchvision torchaudio
   pip install mattersim==1.1.2 sevenn==0.11.2
   ```

6. (Optional) For ORB models, create a separate environment:
   ```bash
   conda create -n atk_orb python=3.10
   conda activate atk_orb
   git clone https://github.com/orbital-materials/orb-models.git
   cd orb-models
   pip install .
   ```

7. (Optional) For Grace models, create a separate environment:
   ```bash
   conda create -n atk_grace python=3.11
   conda activate atk_grace
   pip install tensorpotential
   ```

### (ii) Installation via pip

```bash
conda create -n atk python=3.12
conda activate atk
pip install torch torchvision torchaudio
pip install amaceing_toolkit
```

**Note**: The pip installation does not support running MatterSim and SevenNet simulations directly through the toolkit (only input file creation).

## Usage

### Command line interface

Each functionality can be accessed through dedicated command line tools:

```bash
# Access through interactive Q&A sessions
amaceing_cp2k           # CP2K input creation
amaceing_mace           # MACE input creation
amaceing_mattersim      # MatterSim input creation
amaceing_sevennet       # SevenNet input creation
amaceing_orb            # ORB model input creation
amaceing_grace          # Grace model input creation
amaceing_ana            # Trajectory analysis
amaceing_utils          # Utility functions

# Or with direct arguments for non-interactive use
amaceing_cp2k -rt="GEO_OPT" -c="{'project_name': 'test', 'coord_file': 'system.xyz', 'pbc_list': [10 0 0 0 10 0 0 0 10]}"
```

### Python API

```python
from amaceing_toolkit.workflow import cp2k_api

# Example: Generate a CP2K geometry optimization input
config = {
    'project_name': 'system_geoopt',
    'coord_file': 'system.xyz',
    'pbc_list': [14.2, 0, 0, 0, 14.2, 0, 0, 0, 14.2],
    'max_iter': 10,
    'xc_functional': 'BLYP',
}
cp2k_api(run_type='GEO_OPT', config=config)
```

### Logger
The package includes a run and model logger to track simulation runs and fine-tuned models. This ensures reproducibility and easy access to past runs. 

```bash
amaceing_utils --logger=run         # Get an overview of runs
amaceing_utils --logger=runexport   # Export run logger to PDF
amaceing_utils --logger=model       # Get an overview of models
```

## Documentation

Complete documentation is available at [ReadTheDocs](https://amaceing-toolkit.readthedocs.io/en/latest/).

The documentation provides:
- Comprehensive installation instructions
- Detailed API reference (now consolidated into a single page for easier reference)
- User guides for all supported simulation engines
- Configuration guides
- Example workflows
- Tutorials for common use cases: 
  - **NEW: Getting Started with aMACEing_toolkit** [Introduction to aMACEing_toolkit](https://colab.research.google.com/drive/1brd82x-yWesVKbeUJTC6kR8wx2YIYSKG?usp=sharing)
  - [Tutorial A](https://colab.research.google.com/drive/17sz84cj8PTPJPxAjs4IHuFamNq2g5mBM?usp=sharing)
  - [Tutorial B](https://colab.research.google.com/drive/1laGokzPIKxsPjj3GXn383Cu22Fq_ihb2?usp=sharing)


## Examples

Example systems and scripts are provided in the `examples/` directory:
- `4KOH_92H2O_333K` - Potassium hydroxide in water
- `CsH2PO4` - Cesium dihydrogen phosphate
- `analyzer` - Trajectory analysis examples
- `api_examples` - Python API usage examples

## Citation

If you use aMACEing_toolkit in your research, please cite:

```
[soon]
```

## Roadmap

- [x] The MACE module will be updated to support the latest features in the next release.

## License

This project is licensed under the MIT License (Non-Commercial Use Only).
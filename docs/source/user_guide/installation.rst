Installation Guide
==================

The package is available on GitHub and can be installed via pip.

Installation from Source
------------------------

**We recommend using the installation from source for maximum flexibility.**

1. **Create a virtual environment**:

   .. code-block:: bash

       conda create -n atk python=3.9          # create the environment
       conda activate atk                      # activate the environment

2. **Install PyTorch**:
   
   - For CUDA 12.4:
   
     .. code-block:: bash
     
         pip install torch torchvision torchaudio
   
   - For CPU-only systems:
   
     .. code-block:: bash
     
         pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

3. **Ensure OpenMPI is installed**:

   .. code-block:: bash
   
       mpirun --version
   
   If not installed:
   
   .. code-block:: bash
   
       conda install conda-forge::openmpi

4. **Clone and install the package**:

   .. code-block:: bash
   
       git clone https://github.com/jhaens/amaceing_toolkit.git
       cd amaceing_toolkit
       pip install -r requirements.txt
       pip install .

5. **Optional: Install additional packages for faster MACE**:

   .. code-block:: bash
   
       pip install cuequivariance==0.1.0 cuequivariance-torch==0.1.0 cuequivariance-ops-torch-cu12==0.1.0

6. **Create a second environment for MatterSim and SevenNet**:

   .. code-block:: bash
   
       conda create -n atk_ms7n python=3.9
       conda activate atk_ms7n
       pip install mattersim==1.1.2 sevenn==0.11.0

Installation via pip
--------------------

This is the easiest way to install the package but has limitations (e.g., no direct MatterSim/SevenNet support).

1. **Create a virtual environment**:

   .. code-block:: bash
   
       conda create -n atk python=3.9
       conda activate atk

2. **Install PyTorch**:
   
   - For CUDA 12.4:
   
     .. code-block:: bash
     
         pip install torch torchvision torchaudio
   
   - For CPU-only systems:
   
     .. code-block:: bash
     
         pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

3. **Install the package**:

   .. code-block:: bash
   
       pip install amaceing_toolkit

After installation, verify with:

.. code-block:: bash

    amaceing_cp2k --help
    pip show mace-torch

4. **Optional: Install MatterSim and SevenNet**:

    If you want to use the pip-package with MatterSim and SevenNet, install them in a separate environment:
    
    .. code-block:: bash

        conda create -n atk_ms7n python=3.9
        conda activate atk_ms7n
        # Install PyTorch for CUDA 12.4
        pip install torch torchvision torchaudio
        # Or for CPU-only systems
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
        # Install the packages
        pip install mattersim==1.1.2 sevenn==0.11.0
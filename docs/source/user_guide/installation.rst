Installation
============

Installation from Source
------------------------

**We recommend using the installation from source for maximum flexibility.**

1. **Create a virtual environment**:

   .. code-block:: bash

       conda create -n atk python=3.12         # create the environment
       conda activate atk                      # activate the environment

2. **Install PyTorch**:

   Find the appropriate installation command for your system at the `PyTorch website <https://pytorch.org/get-started/locally/>`_.
   
   For CUDA-enabled systems:
   
   .. code-block:: bash
     
       pip install torch torchvision torchaudio
   
   For CPU-only systems:
   
   .. code-block:: bash
     
       pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

3. **Clone and install the package**:

   .. code-block:: bash
   
       git clone https://github.com/jhaens/amaceing_toolkit.git
       cd amaceing_toolkit
       pip install -r requirements.txt
       pip install .

   Verify installation with:

   .. code-block:: bash
   
       amaceing_cp2k --help
       pip show mace-torch

4. **Optional: Install additional packages for accelerated MACE performance**:

   For CUDA-enabled systems:

   .. code-block:: bash
       # CUDA 11
       pip install cuequivariance cuequivariance-torch cuequivariance-ops-torch-cu11
       # CUDA 12
       pip install cuequivariance cuequivariance-torch cuequivariance-ops-torch-cu12
       # Older MACE Versions (< 0.3.11):
       pip install cuequivariance==0.1.0 cuequivariance-torch==0.1.0 cuequivariance-ops-torch-cu12==0.1.0

5. **Create a separate environment for MatterSim and SevenNet**:

   Due to conflicting dependencies (e3nn version differences), a separate environment is needed:

   .. code-block:: bash
   
       conda create -n atk_ms7n python=3.9
       conda activate atk_ms7n
       pip install torch torchvision torchaudio
       pip install mattersim==1.1.2 sevenn==0.11.2

6. **Create a separate environment for ORB**:

   ORB models require Python 3.10:

   .. code-block:: bash
    
       conda create -n atk_orb python=3.10
       conda activate atk_orb
       git clone https://github.com/orbital-materials/orb-models.git
       cd orb-models
       pip install .

7. **Create a separate environment for Grace**:

   Grace models requires Python 3.11 and Tensorflow will be installed automatically:

   .. code-block:: bash
   
       conda create -n atk_grace python=3.11
       conda activate atk_grace
       pip install tensorpotential

Installation via pip
--------------------

If you only need to create input files (not directly execute MatterSim/SevenNet simulations):

1. **Create a virtual environment**:

   .. code-block:: bash
   
       conda create -n atk python=3.9
       conda activate atk

2. **Install PyTorch**:

   For CUDA-enabled systems:
   
   .. code-block:: bash
   
       pip install torch torchvision torchaudio
   
   For CPU-only systems:
   
   .. code-block:: bash
   
       pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

3. **Install the package**:

   .. code-block:: bash
   
       pip install amaceing_toolkit

   Verify installation with:

   .. code-block:: bash
   
       amaceing_cp2k --help
       pip show mace-torch

Environment Configuration
-------------------------

The toolkit will automatically detect and use the appropriate environment for each model type. By default, it assumes the environment names are:

- Main environment: ``atk``
- MatterSim/SevenNet environment: ``atk_ms7n``  
- ORB environment: ``atk_orb``
- Grace environment: ``atk_grace``

If you use different environment names, you'll need to update them in the runscript templates after your first run, located at:
``/amaceing_toolkit/src/amaceing_toolkit/default_config/runscript_templates``

Verification
------------

To verify successful installation, run any of these commands:

.. code-block:: bash

    amaceing_cp2k --help
    amaceing_mace --help
    amaceing_mattersim --help
    amaceing_sevennet --help  
    amaceing_orb --help
    amaceing_grace --help
    amaceing_ana --help
    amaceing_utils --help


Installation MLIP-supported LAMMPS 
----------------------------------

- Install LAMMPS compatible with MACE: `GPU Tutorial <https://mace-docs.readthedocs.io/en/latest/guide/lammps.html#instructions-for-gpu>`_, `CPU Tutorial <https://mace-docs.readthedocs.io/en/latest/guide/lammps.html#instructions-for-cpu>`_

- Install LAMMPS compatible with SevenNet: `Tutorial <https://github.com/MDIL-SNU/SevenNet?tab=readme-ov-file#md-simulation-with-lammps>`_

- Install LAMMPS compatible with Grace: `Help <https://gracemaker.readthedocs.io/en/latest/gracemaker/install/#lammps-with-grace>`_
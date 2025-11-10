Tutorials
=========

.. image:: https://img.shields.io/badge/Beginners-4c1
   :alt: Beginners Tutorial
   :target: https://colab.research.google.com/drive/1brd82x-yWesVKbeUJTC6kR8wx2YIYSKG

.. image:: https://img.shields.io/badge/Basic-f5f116
   :alt: Basic Tutorial
   :target: https://colab.research.google.com/drive/17sz84cj8PTPJPxAjs4IHuFamNq2g5mBM

.. image:: https://img.shields.io/badge/Advanced-f27a24
   :alt: Advanced Tutorial
   :target: https://colab.research.google.com/drive/1laGokzPIKxsPjj3GXn383Cu22Fq_ihb2


Beginners Notebook
------------------

We recommend starting with our interactive beginner's notebook to familiarize yourself with the toolkit. This notebook offers a clear, step-by-step introduction to the essential features of the aMACEing_toolkit, guiding you through fundamental operations and workflows.
Accessible via Google Colab, the notebook requires no local installation, making it easy to start immediately. The standalone GitHub repository is also available for those who prefer to download and explore offline.

Access the beginner's notebook here: `Getting Started with aMACEing_toolkit <https://colab.research.google.com/drive/1brd82x-yWesVKbeUJTC6kR8wx2YIYSKG>`_ and find the corresponding `GitHub Repository <https://github.com/jhaens/atk_intro>`_.

In this notebook, you will learn how to fine-tune the MACE-MP-0 model using a quantum chemical reference dataset of bulk water.

Content: 
  - Pseudo-Generation of training data (using CP2K)
  - Fine-tuning of MACE-MP-0
  - Evaluation of fine-tuned foundation model
  - Evaluation of foundation model
  - Molecular dynamics simulation with fine-tuned model
  - Analysis

Basic and Advanced Notebooks
----------------------------

For users interested in exploring the full capabilities of the aMACEing_toolkit, we offer two additional interactive notebooks: a Basic Tutorial and an Advanced Tutorial. These provide more in-depth workflows and advanced features.

- `Basic Notebook <https://colab.research.google.com/drive/17sz84cj8PTPJPxAjs4IHuFamNq2g5mBM>`_: 
  
  - CP2K Input Files: Geometry Optimization (GEO_OPT)
  - MACE Input Files: Molecular Dynamics (MD)
  - MACE Input Files: Fine-tuning
  - MatterSim Input Files: MD and Fine-tuning
  - SevenNet Input Files: MD and Fine-tuning
  - Recalculating reference trajectories with MACE


- `Advanced Notebook <https://colab.research.google.com/drive/1laGokzPIKxsPjj3GXn383Cu22Fq_ihb2>`_: 

  - Benchmarking MACE, MatterSim, and SevenNet models
  - Analyzing simulation trajectories
  - Preparing for error evaluation
  - Evaluating errors in the fine-tuned model
  - Obtaining citations for MACE runs


These notebooks can also be found in the `/tutorials/` directory of the `aMACEing_toolkit GitHub Repository <https://github.com/jhaens/amaceing_toolkit/tree/main/tutorials>`_.
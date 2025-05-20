API Reference
============

This section provides detailed API reference documentation for the aMACEing toolkit.

.. note::

   **Special handling of list parameters:**
   
   When using the API functions, you can pass Python lists normally in the configuration dictionaries. 
   The API will automatically format them correctly for the command-line tools, which require a special 
   format without commas (e.g., ``[10.0 0 0 0 10.0 0 0 0 10.0]``).
   
   Example::
   
       # This works in the API
       config = {
           'pbc_list': [14.0, 0, 0, 0, 14.0, 0, 0, 0 14.0],  # Will be automatically formatted correctly
           'foundation_model': ['model1', 'model2', 'model3']  # For MULTI_MD configs
       }
       
       # The API converts this to the special format needed by the command-line tool
       # where lists use spaces instead of commas: [14.0 0 0 0 14.0 0 0 0 14.0]

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   cp2k
   mace
   utils
   mattersim
   sevennet
   analyzer

Welcome to the documentation of the soilpulse software!
=======================================================

The soilpulse software shall help you to make your data easier reusable for other researchers (and the future yourself).
We experienced, that most data is stored in tables (at least in the soil process domain).
Reusability of tabular data requires then a machine readable metadata format - described there:

.. toctree::
   :maxdepth: 1

   data_reusability.md

Assuming reusability we see it important to give some examples, how one can benefit from reuability:

.. toctree::
   :maxdepth: 1

   application_examples

Those examples show how we made use of our soilpulse software to fairify some datasets - which is an ongoing task:

.. toctree::
   :maxdepth: 1

   tutorials

To apply soilpulse yourself you can install the soilpulse core package by:

``pip install -i https://test.pypi.org/simple/ soilpulsecore``


And for the brave or deeply interested programers, this documentation gives the full overview on the soilpulsecore package:

.. toctree::
   :maxdepth: 1

   soilpulsecore


You can contribute to or raise issues on the python package on `our github repo <https://github.com/SoilPulse/MetadataGenerator>`_.

History
-------

The soilpulse software was initiated within our `NFDI4Earth Pilot project SoilPulse <https://www.nfdi4earth.de/2participate/pilots>`_.
In this pilot we explored how soil process data can be made better reusable for other scientists and for automated workflows.
We defined a five steped workflow for our `FAIR <https://www.go-fair.org/fair-principles/>`_ ification:

#. Data ingestion to our software
#. Converting data structures into machine-readable formats
#. Defining variables of the dataset by standardized vocabulary covering parameters/concepts (e.g. bulk density, infiltration rate), units, and measurement methods
#. Automated assessment of data reusability using FAIR metrics
#. Preparation of FAIRified datasets for publication and exchange between research groups

And realized steps 1 to 3 with the soilpulsecore package.

You can find the full project report of the SoilPulse pilot at `zenodo <https://doi.org/10.5281/zenodo.13911635>`_.

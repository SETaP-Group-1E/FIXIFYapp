Read the Docs deployment
========================

The documentation is configured for Read the Docs using the official Sphinx
project layout from the tutorial.

Live documentation
------------------

The published project documentation is available at
https://fixifyapp.readthedocs.io/.

Repository files
----------------

The important documentation files are:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - File
     - Purpose
   * - ``.readthedocs.yaml``
     - Read the Docs configuration at the repository root.
   * - ``code-documentation/docs/source/conf.py``
     - Sphinx configuration.
   * - ``code-documentation/docs/source/index.rst``
     - Main documentation page and table of contents.
   * - ``code-documentation/docs/requirements.txt``
     - Python packages installed by Read the Docs before building.
   * - ``code-documentation/docs/source/*.rst``
     - Documentation source pages.

Read the Docs build settings
----------------------------

The root ``.readthedocs.yaml`` tells Read the Docs to:

* Use Ubuntu 22.04.
* Use Python 3.11.
* Install packages from ``code-documentation/docs/requirements.txt``.
* Build Sphinx using ``code-documentation/docs/source/conf.py``.

Main branch
-----------

The docs should be built from the Fixify repository's ``main`` branch. The
``code-documentation`` folder is now part of the main project instead of being a
separate nested Git repository.

Local verification
------------------

Before pushing documentation changes, run:

.. code-block:: console

   (venv) $ sphinx-build -W -b html code-documentation/docs/source code-documentation/docs/build/html

If this command succeeds, the same Sphinx source is ready for Read the Docs.

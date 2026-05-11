Fixify code documentation
=========================

This folder contains the Sphinx documentation for the Fixify Flask coursework
application.

The documentation is configured for Read the Docs using the repository-level
``.readthedocs.yaml`` file in the Fixify project root. The Sphinx source files
live in ``code-documentation/docs/source``.

To build locally:

.. code-block:: console

   sphinx-build -b html code-documentation/docs/source code-documentation/docs/build/html

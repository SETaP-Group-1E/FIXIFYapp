Fixify documentation
====================

**Fixify** is a Flask web application for connecting homeowners with
contractors. Homeowners can post repair jobs, contractors can submit bids,
accepted bids can move into quick chat, and completed jobs can collect reviews.

This documentation follows the Read the Docs Sphinx tutorial structure while
describing the actual Fixify application instead of the tutorial sample project.

.. note::

   The application currently uses a coursework/demo role flow. The user chooses
   homeowner or contractor from the home page before entering the relevant
   dashboard.

Documentation contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: User and project guide

   overview
   usage
   setup
   workflows
   routes
   database
   deployment

.. toctree::
   :maxdepth: 2
   :caption: Developer reference

   api

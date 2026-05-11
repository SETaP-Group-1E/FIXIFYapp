Installation and setup
======================

This page explains how to prepare the Fixify project locally and how the Read
the Docs configuration is connected to the repository.

Local environment
-----------------

From the project root:

.. code-block:: console

   $ cd /Users/essam/Desktop/FIXIFYapp
   $ python -m venv venv
   $ source venv/bin/activate

Install the Flask application dependencies:

.. code-block:: console

   (venv) $ pip install Flask Flask-SQLAlchemy Flask-WTF WTForms email-validator pytest Flask-Testing

Install the documentation dependencies:

.. code-block:: console

   (venv) $ pip install -r code-documentation/docs/requirements.txt

Running the Flask app
---------------------

Start the app with:

.. code-block:: console

   (venv) $ python main.py

The terminal normally shows a local URL such as ``http://127.0.0.1:5000``.

Database setup
--------------

The app uses SQLite through Flask-SQLAlchemy. The database URI defaults to
``sqlite:///jobs.db`` unless ``FIXIFY_DATABASE_URI`` is set in the environment.

The ``create_tables`` before-request hook calls ``ensure_database_schema`` so
the expected tables and columns are created or upgraded when the app receives a
request.

Read the Docs setup
-------------------

Read the Docs looks for ``.readthedocs.yaml`` in the repository root. In this
project the root config points to:

* Sphinx config: ``code-documentation/docs/source/conf.py``
* Requirements file: ``code-documentation/docs/requirements.txt``
* Documentation source folder: ``code-documentation/docs/source/``

The documentation should be built from the repository's ``main`` branch.

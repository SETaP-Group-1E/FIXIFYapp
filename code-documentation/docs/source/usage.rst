Quick start
===========

.. _installation:

Installation
------------

Create and activate a virtual environment from the project root:

.. code-block:: console

   $ python -m venv venv
   $ source venv/bin/activate

Install the application and documentation dependencies:

.. code-block:: console

   (venv) $ pip install Flask Flask-SQLAlchemy Flask-WTF WTForms email-validator pytest Flask-Testing
   (venv) $ pip install -r code-documentation/docs/requirements.txt

Running the app
---------------

Start the Flask app from the project root:

.. code-block:: console

   (venv) $ python main.py

Then open the local address shown in the terminal, normally
``http://127.0.0.1:5000``.

Main user roles
---------------

Fixify starts on a public home page. From there, the demo user chooses one of
two roles:

* ``homeowner``: post jobs, edit or delete posted jobs, review bids, accept or
  reject bids, ask for clarification, mark accepted jobs as completed, and leave
  reviews after both sides complete the job.
* ``contractor``: view available jobs, submit bids, respond to clarification
  requests, track pending/accepted/completed bids, use quick chat after a bid is
  accepted, and leave reviews after completion.

Short bidding workflow
----------------------

The main bidding flow is:

1. A homeowner posts a job with title, category, urgency, location, budget, and
   optional description/photo.
2. A contractor views available jobs and submits a bid with amount, timeline,
   and optional explanation.
3. The homeowner reviews received bids and chooses ``Accept``, ``Reject``, or
   ``Clarify``.
4. If clarification is requested, the contractor replies from the contractor
   bids page.
5. Once accepted, the job leaves the public available jobs list and appears in
   the contractor's accepted jobs area.
6. Quick chat becomes available only after acceptance.
7. Both homeowner and contractor must mark the accepted job completed before
   review links appear.

Building the documentation locally
----------------------------------

From the project root, run:

.. code-block:: console

   (venv) $ sphinx-build -b html code-documentation/docs/source code-documentation/docs/build/html

The generated HTML will be written to
``code-documentation/docs/build/html``.

Running tests quickly
---------------------

Run the full pytest suite from the project root:

.. code-block:: console

   (venv) $ python -m pytest tests

The bidding tests use Flask's test client and an isolated test database
configuration instead of manually clicking through the website.

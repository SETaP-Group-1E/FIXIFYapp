Database design
===============

Fixify uses Flask-SQLAlchemy models in ``main.py``. SQLite is used by default
through the URI ``sqlite:///jobs.db``.

Job model
---------

The ``Job`` table stores homeowner job information.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Field
     - Purpose
   * - ``id``
     - Primary key.
   * - ``title``
     - Job title entered by the homeowner.
   * - ``description``
     - Optional job description.
   * - ``location``
     - Job location.
   * - ``category``
     - Job category such as plumbing, electrical, gardening, or custom other
       category.
   * - ``urgency``
     - Urgency level used by contractor timeline choices.
   * - ``timing_window``
     - Preferred timing window.
   * - ``budget``
     - Homeowner budget as a float.
   * - ``is_negotiable``
     - Whether the budget can be negotiated.
   * - ``photo_filename``
     - Optional uploaded job photo filename.
   * - ``status``
     - Job status, normally ``pending`` or ``completed``.

Bid model
---------

The ``Bid`` table stores contractor offers linked to jobs.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Field
     - Purpose
   * - ``job_id``
     - Database job reference.
   * - ``bid_id``
     - Bid number used inside the job's bid list.
   * - ``contractor_id``
     - Contractor identifier.
   * - ``contractor_name``
     - Contractor display name at the time of bidding.
   * - ``rating``
     - Contractor rating shown to the homeowner.
   * - ``amount``
     - Contractor bid amount.
   * - ``timeline``
     - Contractor estimated timeline.
   * - ``explanation``
     - Optional explanation from the contractor.
   * - ``status``
     - Pending, Accepted, Rejected, Clarification Requested, or Clarification
       Provided.
   * - ``clarification_response``
     - Contractor response when clarification is requested.
   * - ``homeowner_completed`` and ``contractor_completed``
     - Completion confirmation flags.
   * - ``completion_status``
     - Human-readable completion status.

Profile model
-------------

The ``Profile`` table stores setup details for homeowner and contractor roles.
Contractor profiles include specialty and portfolio text. Homeowner profiles do
not use portfolio.

Review model
------------

The ``Review`` table stores homeowner and contractor reviews for completed jobs.
Reviews include rating fields, optional comments, optional photos, and a
``created_at`` timestamp. The ``can_edit`` property allows editing only during
the short edit window.

Schema upgrade helper
---------------------

``ensure_database_schema`` creates tables and adds missing columns for older
SQLite databases. This lets the app keep existing local data while still adding
new columns introduced during development.

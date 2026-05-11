Project overview
================

Fixify is a Flask coursework application that connects homeowners with
contractors. It is centred around a realistic service workflow: homeowners post
jobs, contractors submit bids, the homeowner chooses how to respond, and both
sides can communicate, complete the work, and leave reviews.

Main features
-------------

The current application supports the full journey from posting a job through to
reviewing a completed accepted job:

* A public home page where the demo user chooses ``homeowner`` or
  ``contractor``.
* Homeowner job posting with category, urgency, location, budget, negotiable
  status, optional description, and optional job photo.
* Contractor job browsing and bid submission.
* Homeowner bid management with accept, reject, and clarification options.
* Contractor bid history for pending, accepted, rejected, and clarification
  states.
* Quick chat that only opens after a bid is accepted.
* Completion confirmation by both sides before reviews become available.
* Database-backed profiles, jobs, bids, and reviews.

How the app is organised
------------------------

Fixify uses a small demo-style role system so the coursework can focus on the
homeowner and contractor workflows instead of a full authentication system.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Area
     - Summary
   * - Home page
     - Lets the demo user choose ``homeowner`` or ``contractor``.
   * - Homeowner side
     - Posting jobs, managing posted jobs, reviewing bids, accepting/rejecting
       bids, asking for clarification, confirming completion, and reviewing.
   * - Contractor side
     - Browsing open jobs, submitting bids, tracking bid outcomes, clarifying
       bids, using quick chat after acceptance, confirming completion, and
       reviewing.
   * - Shared logic
     - Database syncing, file uploads, profile display, review display, and
       quick chat notifications.

Code structure
--------------

Most of the application logic currently lives in ``main.py``. The project also
uses template files in ``templates/`` for the web pages and static files in
``static/`` for uploaded images and styling.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Path
     - Purpose
   * - ``main.py``
     - Flask app setup, route handlers, database models, bidding helpers, review
       helpers, and profile helpers.
   * - ``forms.py``
     - WTForms classes for the original login and register forms.
   * - ``templates/``
     - Jinja HTML templates for home, dashboards, jobs, bids, chat, profiles,
       and reviews.
   * - ``static/uploads/``
     - Uploaded job and review photos.
   * - ``tests/``
     - Pytest and Flask test client tests.
   * - ``code-documentation/docs/source/``
     - Sphinx ``.rst`` source files used by Read the Docs.

Important design notes
----------------------

The app uses a simple demo role selection instead of a full account login
system. This keeps the coursework flow focused on the homeowner and contractor
journeys. The selected role is stored in the Flask session and controls which
dashboard and navigation links are shown.

The bidding workflow still uses the shared in-memory ``all_jobs`` list for the
live demo screens, but the important entities are also synchronised to SQLite so
jobs, bids, profiles, and reviews can be stored more permanently.

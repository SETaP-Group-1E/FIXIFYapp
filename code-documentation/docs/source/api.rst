Developer reference
===================

This page is a readable developer reference for the important code in
``main.py``. It avoids listing every inherited Flask or SQLAlchemy detail and
focuses on the methods that explain how the app works.

Application setup
-----------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Method or object
     - Purpose
   * - ``app = Flask(__name__)``
     - Creates the Flask application.
   * - ``db = SQLAlchemy(app)``
     - Connects SQLAlchemy to the Flask app.
   * - ``create_app(testing=False)``
     - Returns the Flask app and switches to an in-memory database when tests
       ask for testing mode.
   * - ``create_tables()``
     - Runs before requests and keeps the SQLite schema available.
   * - ``should_use_database()``
     - Prevents simple tests from writing to the real ``jobs.db`` file.
   * - ``ensure_database_schema()``
     - Creates tables and adds missing columns for older local databases.

Database models
---------------

The full table fields are explained on :doc:`database`.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Model
     - Purpose
   * - ``Job``
     - Stores homeowner job data such as title, description, category, urgency,
       budget, location, photo, and status.
   * - ``Bid``
     - Stores contractor bid data such as amount, timeline, explanation,
       status, clarification response, and completion flags.
   * - ``Profile``
     - Stores homeowner and contractor profile details.
   * - ``Review``
     - Stores review ratings, comments, optional review photos, and the edit
       time window through ``can_edit``.

Route handlers
--------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Function
     - What it controls
   * - ``home()``
     - Public landing page and role selection.
   * - ``login_as(role)``
     - Saves the selected demo role in the session.
   * - ``homeowner_dashboard()``
     - Shows homeowner jobs, bid counts, notifications, completion controls,
       and review actions.
   * - ``contractor_dashboard()``
     - Shows available jobs that contractors can bid on.
   * - ``contractor_bids()``
     - Shows the contractor's bid history, accepted jobs, completion status,
       clarification forms, reviews, and quick chat alerts.
   * - ``post()``
     - Creates a homeowner job.
   * - ``edit_job(job_id)``
     - Updates an existing homeowner job.
   * - ``delete_job(job_id)``
     - Removes a posted job.
   * - ``submit_bid()``
     - Validates contractor bid input and creates a new bid.
   * - ``view_job_bids(job_id)``
     - Shows the homeowner all bids for one job.
   * - ``update_bid_status()``
     - Accepts, rejects, or requests clarification for a bid.
   * - ``submit_clarification()``
     - Saves the contractor's clarification response.
   * - ``quick_chat(job_id, bid_id)``
     - Shows and sends chat messages after acceptance.
   * - ``complete_job(job_id, bid_id)``
     - Records homeowner or contractor completion confirmation.
   * - ``submit_review(job_id, bid_id)``
     - Saves homeowner or contractor review data for a completed accepted job.
   * - ``contractor_profile(contractor_id)``
     - Shows contractor profile, portfolio, and reviews.
   * - ``homeowner_profile(homeowner_id)``
     - Shows homeowner profile and reviews.

Bidding helpers
---------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Helper
     - Purpose
   * - ``next_job_id()``
     - Generates the next job ID even after jobs have been deleted.
   * - ``budget_to_float(value)``
     - Safely converts budget text to a database-friendly number.
   * - ``find_job_and_bid(job_id, bid_id)``
     - Finds the matching job and bid pair used by bid actions, completion, and
       quick chat.
   * - ``get_available_jobs()``
     - Returns jobs that are still open for contractor bidding.
   * - ``get_accepted_bid(job)``
     - Returns the accepted bid for a homeowner job when one exists.
   * - ``ensure_bid_completion_fields(bid)``
     - Adds missing completion fields to older bid dictionaries.
   * - ``is_bid_completed(bid)``
     - Checks whether both homeowner and contractor have confirmed completion.
   * - ``sync_job_to_db(job, status=None)``
     - Creates or updates the database ``Job`` row from the live job dictionary.
   * - ``sync_bid_to_db(job, bid)``
     - Creates or updates the database ``Bid`` row from the live bid dictionary.
   * - ``delete_job_from_db(job_id)``
     - Removes a job from the database.

Profiles and reviews
--------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Helper
     - Purpose
   * - ``profile_user_id(role)``
     - Returns the demo user ID for the selected role.
   * - ``default_profile(role, user_id=None)``
     - Provides fallback profile data when a database profile does not exist.
   * - ``load_profile(role, user_id=None)``
     - Loads a saved profile from the database.
   * - ``profile_needs_setup(role)``
     - Decides whether a role should be sent to profile setup.
   * - ``sync_contractor_profile(profile)``
     - Keeps contractor display data aligned with the saved profile.
   * - ``portfolio_items_for(profile)``
     - Splits contractor portfolio text into displayable items.
   * - ``save_review_to_db(job, reviewer_type, review_data, bid=None)``
     - Saves or updates review data in SQLite.
   * - ``get_review_for_bid(job, bid, reviewer_type)``
     - Finds the review linked to an accepted bid.
   * - ``average_review_score(reviews)``
     - Calculates the displayed profile average rating.
   * - ``can_edit_review(review)``
     - Checks whether a review is still inside the edit window.

Quick chat and clarification
----------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Helper
     - Purpose
   * - ``contractor_has_open_clarification(contractor_id)``
     - Checks whether the contractor needs to reply to a clarification request.
   * - ``get_quick_chat_notifications(target_role, contractor_id=None)``
     - Collects unread chat messages for dashboard notifications.
   * - ``mark_quick_chat_notifications_read(bid, target_role)``
     - Clears unread markers once the relevant user opens quick chat.

Why this page is manual
-----------------------

The app uses Flask and SQLAlchemy, which expose a lot of inherited methods that
are not useful for understanding the coursework. A manual developer reference
keeps the important method names visible while avoiding noisy framework
internals.

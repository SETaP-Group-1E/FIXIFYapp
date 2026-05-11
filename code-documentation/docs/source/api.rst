API reference
=============

This page documents the main Fixify Flask module and the helper methods used by
the bidding, completion, quick chat, profile, and review workflows.

Application setup
-----------------

.. automodule:: main

.. autofunction:: main.create_app

.. autofunction:: main.should_use_database

.. autofunction:: main.ensure_database_schema

Database models
---------------

.. autoclass:: main.Job
   :members:

.. autoclass:: main.Bid
   :members:

.. autoclass:: main.Profile
   :members:

.. autoclass:: main.Review
   :members:

Bidding helpers
---------------

.. autofunction:: main.next_job_id

.. autofunction:: main.allowed_file

.. autofunction:: main.save_uploaded_photo

.. autofunction:: main.budget_to_float

.. autofunction:: main.sync_job_to_db

.. autofunction:: main.delete_job_from_db

.. autofunction:: main.get_bid_from_db

.. autofunction:: main.sync_bid_to_db

.. autofunction:: main.find_job_and_bid

.. autofunction:: main.ensure_bid_completion_fields

.. autofunction:: main.is_bid_completed

.. autofunction:: main.get_accepted_bid

.. autofunction:: main.get_available_jobs

Profiles and reviews
--------------------

.. autofunction:: main.profile_user_id

.. autofunction:: main.default_profile

.. autofunction:: main.load_profile

.. autofunction:: main.get_profile

.. autofunction:: main.profile_needs_setup

.. autofunction:: main.sync_contractor_profile

.. autofunction:: main.portfolio_items_for

.. autofunction:: main.review_score

.. autofunction:: main.average_review_score

.. autofunction:: main.get_profile_reviews

.. autofunction:: main.save_review_to_db

.. autofunction:: main.get_review_from_db

.. autofunction:: main.get_review_for_bid

.. autofunction:: main.can_edit_review

Quick chat and clarification
----------------------------

.. autofunction:: main.contractor_has_open_clarification

.. autofunction:: main.get_quick_chat_notifications

.. autofunction:: main.mark_quick_chat_notifications_read

Routes and pages
================

This page summarises the main Flask routes in ``main.py``.

Public and role routes
----------------------

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Route
     - Method
     - Purpose
   * - ``/`` and ``/home``
     - ``GET``
     - Shows the public home page and role selection cards.
   * - ``/login/<role>``
     - ``GET``
     - Stores the selected demo role in the session and redirects to the
       matching area.
   * - ``/logout``
     - ``GET``
     - Clears the selected role and returns to the public home page.
   * - ``/login``
     - ``GET``
     - Keeps the original login page route available.
   * - ``/register``
     - ``GET`` and ``POST``
     - Keeps the original registration page route available.

Dashboard routes
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Route
     - Method
     - Purpose
   * - ``/homeowner-dashboard``
     - ``GET``
     - Shows posted jobs, bid counts, latest notifications, accepted bid status,
       edit/delete actions, completion actions, and review links.
   * - ``/contractor-dashboard``
     - ``GET``
     - Shows jobs that are still available for bidding.
   * - ``/contractor-bids``
     - ``GET``
     - Shows accepted jobs, pending bids, rejected bids, clarification requests,
       completion controls, reviews, and quick chat links.

Job and bid routes
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Route
     - Method
     - Purpose
   * - ``/post``
     - ``GET`` and ``POST``
     - Lets the homeowner create a job.
   * - ``/job/<job_id>/edit``
     - ``GET`` and ``POST``
     - Lets the homeowner edit an existing job.
   * - ``/job/<job_id>/delete``
     - ``POST``
     - Deletes a posted job from the in-memory list and database.
   * - ``/submit_bid``
     - ``POST``
     - Validates contractor bid input and creates a bid.
   * - ``/job/<job_id>``
     - ``GET``
     - Shows bids received for one homeowner job.
   * - ``/update_bid_status``
     - ``POST``
     - Accepts, rejects, or requests clarification for a bid.
   * - ``/submit-clarification``
     - ``POST``
     - Saves the contractor clarification response.
   * - ``/complete-job/<job_id>/<bid_id>``
     - ``POST``
     - Marks completion from the homeowner or contractor side.
   * - ``/quick-chat/<job_id>/<bid_id>``
     - ``GET`` and ``POST``
     - Opens the accepted bid chat and sends chat messages.

Profile and review routes
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Route
     - Method
     - Purpose
   * - ``/profile``
     - ``GET``
     - Sends the current role to the matching profile page.
   * - ``/profile/setup/<role>``
     - ``GET`` and ``POST``
     - Creates or updates the homeowner or contractor demo profile.
   * - ``/contractor/<contractor_id>``
     - ``GET``
     - Shows contractor profile details, portfolio, and reviews.
   * - ``/homeowner/<homeowner_id>``
     - ``GET``
     - Shows homeowner profile details and reviews.
   * - ``/review/<job_id>/<bid_id>``
     - ``GET`` and ``POST``
     - Creates or edits a review for a completed accepted job.
   * - ``/report-review/<review_id>``
     - ``GET``
     - Shows the report-review flash flow for a saved review.
   * - ``/uploads/<filename>``
     - ``GET``
     - Serves uploaded job and review files from the upload folder.

Features
========

This page summarises the important features in the Fixify app without going too
deep into code details.

Homeowner features
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Feature
     - What it does
   * - Role selection
     - The homeowner enters through ``Login as Homeowner`` on the public home
       page.
   * - Profile setup
     - The homeowner can create a basic profile with name, contact details,
       location, and bio.
   * - Post job
     - The homeowner can post a job with title, category, urgency, location,
       budget, negotiable status, optional description, and optional image.
   * - Edit/delete job
     - Posted jobs can be updated or removed from the homeowner dashboard.
   * - View bids
     - Each posted job shows the number of received bids and links to the bid
       review page.
   * - Bid decision
     - The homeowner can accept, reject, or ask the contractor for
       clarification.
   * - Completion
     - The homeowner must confirm completion before the job can be fully marked
       completed.
   * - Reviews
     - After both sides confirm completion, the homeowner can review the
       contractor.

Contractor features
-------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Feature
     - What it does
   * - Role selection
     - The contractor enters through ``Login as Contractor`` on the public home
       page.
   * - Profile setup
     - The contractor can create a profile with name, specialty, contact
       details, bio, and portfolio text.
   * - Browse jobs
     - The contractor dashboard shows homeowner jobs that are still open for
       bidding.
   * - Submit bid
     - A contractor bid includes amount, timeline, and optional explanation.
   * - Track bids
     - The ``My Bids`` page groups pending, accepted, completed, and
       clarification-related bids. Rejected bids are removed from the active
       contractor view.
   * - Clarification response
     - If the homeowner asks for more detail, the contractor can reply from the
       bid history page.
   * - Quick chat
     - Quick chat only becomes available after a bid has been accepted.
   * - Completion
     - The contractor must also confirm completion before reviews are unlocked.

Shared behaviour
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Behaviour
     - Reason
   * - Accepted jobs leave available jobs
     - Once a bid is accepted, the job should no longer appear as open work for
       other contractor bids.
   * - Quick chat is acceptance-only
     - Chat is restricted until the homeowner chooses a contractor.
   * - Two-sided completion
     - A job is only fully completed once both homeowner and contractor confirm
       it.
   * - Review timing
     - Reviews are linked to completed jobs and include a short edit window.
   * - Image upload validation
     - Uploaded job and review photos are limited to common image file types.
   * - Notifications
     - Dashboards show important updates, including new bids, clarification
       responses, and unread quick chat messages.

Input rules
-----------

The app keeps the user input simple and controlled:

* Job category and urgency are selected from form options, with an ``Other``
  text box for custom categories.
* Contractor timelines are selected from dropdown options based on homeowner
  urgency.
* Bid amount must be a positive number.
* Bid explanation is optional.
* Job description is optional.
* Review comments are optional, but the required star ratings must be selected.
* Quick chat messages and clarification responses cannot be empty.

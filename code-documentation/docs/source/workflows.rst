Application workflows
=====================

Homeowner workflow
------------------

The homeowner journey starts from the public home page:

1. Choose ``Login as Homeowner``.
2. Create or confirm the homeowner profile if required.
3. Open the homeowner dashboard.
4. Post a job from ``Post Job``.
5. View the job under ``My Jobs``.
6. Open ``View Bids`` to inspect contractor bids.
7. Accept, reject, or ask for clarification.
8. If a bid is accepted, use quick chat and completion controls.
9. After both sides mark the job completed, leave a review.

Contractor workflow
-------------------

The contractor journey is:

1. Choose ``Login as Contractor``.
2. Create or confirm the contractor profile if required.
3. Browse open jobs on the contractor dashboard.
4. Submit a bid with amount, timeline, and optional explanation.
5. Track the bid in ``My Bids``.
6. Respond if the homeowner asks for clarification.
7. If accepted, open quick chat and later mark the job completed.
8. Leave a review after both sides confirm completion.

Bidding status flow
-------------------

Bid status is used to control what each side can do.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Status
     - Meaning
   * - ``Pending``
     - The contractor submitted the bid and the homeowner has not decided yet.
   * - ``Accepted``
     - The homeowner accepted the bid. Quick chat and completion controls are
       available.
   * - ``Rejected``
     - The homeowner rejected the bid. It is removed from the active homeowner
       and contractor bid screens.
   * - ``Clarification Requested``
     - The homeowner asked the contractor to explain the bid further.
   * - ``Clarification Provided``
     - The contractor sent clarification back to the homeowner.

Completion workflow
-------------------

Completion belongs to the accepted job/bid pair. A job is not fully completed
until both sides confirm it:

* Homeowner presses ``Mark Completed as Homeowner``.
* Contractor presses ``Mark Completed as Contractor``.
* If only one side has confirmed, the status remains ``Job not completed``.
* Once both have confirmed, the bid completion status becomes ``Completed`` and
  reviews are unlocked.

Quick chat workflow
-------------------

Quick chat is intentionally locked until a bid is accepted. This prevents a
contractor and homeowner from using chat before the homeowner has chosen the
contractor.

Messages are stored on the accepted bid as ``chat_messages``. Each message
contains a sender, message text, and unread target role. The dashboards show a
``New quick chat message`` alert for the side that has not read the message yet.

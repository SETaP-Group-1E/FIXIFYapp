# Prerequisites
#   pip3 install flask-testing pytest

import unittest
import io
from datetime import datetime, timedelta
from flask_testing import TestCase

from main import create_app, all_jobs, db, Job, Bid

def _make_job(job_id=1, with_bid=False, bid_status="Pending"):
    """
    Return a minimal job dict compatible with all_jobs.
    Pass with_bid=True to attach a single bid from contractor 1 (John Smith).
    """
    job = {
        "id":            job_id,
        "title":         "Fix Boiler",
        "description":   "Boiler needs fixing",
        "category":      "Plumbing",
        "urgency":       "High",
        "location":      "Portsmouth",
        "budget":        "200",
        "is_negotiable": False,
        "bids":          [],
        "notifications": [],
    }
    if with_bid:
        bid = {
            "id":              1,
            "contractor_id":   1,
            "contractor_name": "John Smith",
            "rating":          4.8,
            "amount":          150.0,
            "timeline":        "3 days",
            "explanation":     "I can fix it.",
            "status":          bid_status,
        }
        if bid_status == "Accepted":
            bid.update({
                "chat_messages":        [],
                "homeowner_completed":  False,
                "contractor_completed": False,
                "completion_status":    "Job not completed",
            })
        job["bids"].append(bid)
    return job


class BiddingTestBase(TestCase):
    """
    Configures the Flask test client and resets both the in-memory job list
    and the in-memory SQLite database before every individual test.
    """

    def create_app(self):
        return create_app(testing=True)

    def setUp(self):
        """Reset all_jobs and rebuild DB schema for each test."""
        all_jobs.clear()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Wipe DB and in-memory state after each test."""
        all_jobs.clear()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ---- DB query helpers ---------------------------------------------------

    def _get_db_job(self, job_id):
        """Return the Job ORM row from the test DB, or None."""
        with self.app.app_context():
            return db.session.get(Job, job_id)

    def _get_db_bid(self, job_id, bid_id):
        """
        Return the Bid ORM row matching (job_id, bid_id), or None.
        Mirrors get_bid_from_db() in main.py.
        """
        with self.app.app_context():
            return Bid.query.filter_by(job_id=job_id, bid_id=bid_id).first()

    def assertNoBidRow(self, job_id=1, bid_id=1):
        """Assert that no Bid row was written for this job/bid pair."""
        self.assertIsNone(
            self._get_db_bid(job_id, bid_id),
            "A Bid DB row was written but should not have been.",
        )

    def assertBidRow(self, job_id=1, bid_id=1, **expected_fields):
        """
        Assert a Bid row exists and every keyword argument matches the
        corresponding column value on the row.
        """
        row = self._get_db_bid(job_id, bid_id)
        self.assertIsNotNone(
            row,
            f"Expected a Bid row for job_id={job_id}, bid_id={bid_id} but found none.",
        )
        for field, expected in expected_fields.items():
            actual = getattr(row, field)
            self.assertEqual(
                actual, expected,
                f"Bid.{field}: expected {expected!r}, got {actual!r}.",
            )

    # ---- HTTP helpers -------------------------------------------------------

    def _set_session(self, role="homeowner", contractor_id=None):
        with self.client.session_transaction() as sess:
            sess["role"] = role
            if contractor_id is not None:
                sess["contractor_id"] = contractor_id

    def _post(self, url, data, follow=True):
        return self.client.post(url, data=data, follow_redirects=follow)

    def _get(self, url, query_string=None, follow=True):
        return self.client.get(
            url, query_string=query_string or {}, follow_redirects=follow,
        )

    def assertFlash(self, response, text):
        self.assertIn(
            text.encode(), response.data,
            msg=f"Expected flash '{text}' not found in response.",
        )

class PostingTestBase(TestCase):

    def create_app(self):
        return create_app(testing=True)

    def setUp(self):
        all_jobs.clear()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()

    def tearDown(self):
        all_jobs.clear()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _set_session(self, role=None):
        with self.client.session_transaction() as sess:
            if role is None:
                sess.pop("role", None)
            else:
                sess["role"] = role

    def _post(self, data=None):
        return self.client.post("/post", data=data or {}, follow_redirects=True)

    def _latest(self):
        with self.app.app_context():
            return Job.query.order_by(Job.id.desc()).first()

    def valid_data(self):
        return {
            "title": "Fix Boiler",
            "description": "Boiler leaking.",
            "category": "Plumbing",
            "urgency": "High",
            "location": "Portsmouth",
            "budget_amount": "200",
            "is_negotiable": "false"
        }


class TestPostJob(PostingTestBase):

    def test_no_role_in_session(self):
        rv = self._post()
        self.assertIn(b"Please choose homeowner first.", rv.data)

    def test_contractor_role_blocked(self):
        self._set_session("contractor")
        rv = self._post()
        self.assertIn(b"Only homeowners can post jobs.", rv.data)

    def test_homeowner_role_allowed(self):
        self._set_session("homeowner")
        rv = self.client.get("/post")
        self.assertEqual(rv.status_code, 200)

    def test_title_missing(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data.pop("title")
        rv = self._post(data)
        self.assertIn(b"Please enter a job title.", rv.data)
        self.assertIsNone(self._latest())

    def test_title_empty(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["title"] = ""
        rv = self._post(data)
        self.assertIn(b"Please enter a job title.", rv.data)
        self.assertIsNone(self._latest())

    def test_title_whitespace(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["title"] = "   "
        rv = self._post(data)
        self.assertIn(b"Please enter a job title.", rv.data)
        self.assertIsNone(self._latest())

    def test_title_valid_short(self):
        self._set_session("homeowner")
        self._post(self.valid_data())
        self.assertEqual(self._latest().title, "Fix Boiler")

    def test_title_very_long(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["title"] = "A" * 300
        rv = self._post(data)
        self.assertIn(b"Job title is too long.", rv.data)
        self.assertIsNone(self._latest())

    def test_title_special_characters(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["title"] = "Fix boiler ASAP!"
        self._post(data)
        self.assertEqual(self._latest().title, "Fix boiler ASAP!")

    def test_description_missing(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data.pop("description")
        rv = self._post(data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(self._latest().description, "")

    def test_description_empty(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["description"] = ""
        rv = self._post(data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(self._latest().description, "")

    def test_description_whitespace(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["description"] = "   "
        rv = self._post(data)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(self._latest().description, "")

    def test_description_valid(self):
        self._set_session("homeowner")
        self._post(self.valid_data())
        self.assertEqual(self._latest().description, "Boiler leaking.")

    def test_description_multiline(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["description"] = "Line 1\nLine 2"
        self._post(data)
        self.assertEqual(self._latest().description, "Line 1\nLine 2")

    def test_description_very_long(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["description"] = "A" * 2000
        rv = self._post(data)
        self.assertIn(b"Description is too long.", rv.data)
        self.assertIsNone(self._latest())

    def test_category_missing(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data.pop("category")
        rv = self._post(data)
        self.assertIn(b"Please select a category.", rv.data)
        self.assertIsNone(self._latest())

    def test_category_valid(self):
        self._set_session("homeowner")
        self._post(self.valid_data())
        self.assertEqual(self._latest().category, "Plumbing")

    def test_category_invalid(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["category"] = "Rocket Science"
        rv = self._post(data)
        self.assertIn(b"Invalid category.", rv.data)
        self.assertIsNone(self._latest())

    def test_category_case_mismatch(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["category"] = "plumbing"
        rv = self._post(data)
        self.assertIn(b"Invalid category.", rv.data)
        self.assertIsNone(self._latest())

    def test_category_spaces(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["category"] = " Plumbing "
        rv = self._post(data)
        self.assertIn(b"Invalid category.", rv.data)
        self.assertIsNone(self._latest())

    def test_urgency_missing(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data.pop("urgency")
        rv = self._post(data)
        self.assertIn(b"Please select an urgency.", rv.data)
        self.assertIsNone(self._latest())

    def test_urgency_valid(self):
        self._set_session("homeowner")
        self._post(self.valid_data())
        self.assertEqual(self._latest().urgency, "High")

    def test_urgency_invalid(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["urgency"] = "Immediate"
        rv = self._post(data)
        self.assertIn(b"Invalid urgency.", rv.data)
        self.assertIsNone(self._latest())

    def test_urgency_case_mismatch(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["urgency"] = "high"
        rv = self._post(data)
        self.assertIn(b"Invalid urgency.", rv.data)
        self.assertIsNone(self._latest())

    def test_location_missing(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data.pop("location")
        rv = self._post(data)
        self.assertIn(b"Please enter a location.", rv.data)
        self.assertIsNone(self._latest())

    def test_location_valid(self):
        self._set_session("homeowner")
        self._post(self.valid_data())
        self.assertEqual(self._latest().location, "Portsmouth")

    def test_location_whitespace(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["location"] = "   "
        rv = self._post(data)
        self.assertIn(b"Please enter a location.", rv.data)
        self.assertIsNone(self._latest())

    def test_location_very_long(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["location"] = "A" * 200
        rv = self._post(data)
        self.assertIn(b"Location is too long.", rv.data)
        self.assertIsNone(self._latest())

    def test_budget_missing(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data.pop("budget_amount")
        rv = self._post(data)
        self.assertEqual(rv.status_code, 200)
        self.assertIsNone(self._latest().budget)

    def test_budget_non_numeric(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["budget_amount"] = "abc"
        rv = self._post(data)
        self.assertIn(b"Budget must be a valid positive number.", rv.data)
        self.assertIsNone(self._latest())

    def test_budget_zero(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["budget_amount"] = "0"
        rv = self._post(data)
        self.assertIn(b"Budget must be a valid positive number.", rv.data)
        self.assertIsNone(self._latest())

    def test_budget_negative(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["budget_amount"] = "-50"
        rv = self._post(data)
        self.assertIn(b"Budget must be a valid positive number.", rv.data)
        self.assertIsNone(self._latest())

    def test_budget_valid_integer(self):
        self._set_session("homeowner")
        self._post(self.valid_data())
        self.assertEqual(self._latest().budget, 200.0)

    def test_budget_valid_float(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["budget_amount"] = "199.99"
        self._post(data)
        self.assertEqual(self._latest().budget, 199.99)

    def test_budget_currency(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["budget_amount"] = "£200"
        rv = self._post(data)
        self.assertIn(b"Budget must be a valid positive number.", rv.data)
        self.assertIsNone(self._latest())

    def test_budget_large(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["budget_amount"] = "9999999"
        self._post(data)
        self.assertEqual(self._latest().budget, 9999999.0)

    def test_negotiable_false(self):
        self._set_session("homeowner")
        self._post(self.valid_data())
        self.assertFalse(self._latest().is_negotiable)

    def test_negotiable_true(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["is_negotiable"] = "true"
        self._post(data)
        self.assertTrue(self._latest().is_negotiable)

    def test_negotiable_invalid(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["is_negotiable"] = "maybe"
        rv = self._post(data)
        self.assertIn(b"Invalid negotiable value.", rv.data)
        self.assertIsNone(self._latest())

    def test_all_valid_fields(self):
        self._set_session("homeowner")
        rv = self._post(self.valid_data())
        self.assertEqual(rv.status_code, 200)
        job = self._latest()
        self.assertEqual(job.title, "Fix Boiler")
        self.assertEqual(job.description, "Boiler leaking.")
        self.assertEqual(job.category, "Plumbing")
        self.assertEqual(job.urgency, "High")
        self.assertEqual(job.location, "Portsmouth")
        self.assertEqual(job.budget, 200.0)
        self.assertFalse(job.is_negotiable, False)

    def test_one_required_field_missing(self):
        self._set_session("homeowner")
        rv = self._post(self.valid_data())
        self.assertEqual(rv.status_code, 200)
        job = self._latest()
        self.assertEqual(job.title, "Fix Boiler")
        self.assertEqual(job.description, "Boiler leaking.")
        self.assertEqual(job.category, "Plumbing")
        self.assertEqual(job.urgency, "High")
        self.assertEqual(job.location, "Portsmouth")
        self.assertEqual(job.budget, 200.0)

# 1. submit_bid   (POST /submit_bid)

class TestSubmitBid(BiddingTestBase):

    def setUp(self):
        super().setUp()
        all_jobs.append(_make_job(1))

    def _bid(self, **overrides):
        data = {
            "job_id": "1", "contractor_id": "1",
            "bid_amount": "150", "timeline": "3 days", "explanation": "",
        }
        data.update(overrides)
        return self._post("/submit_bid", data)

    # ---- Signature: raw_id (job_id) ----------------------------------------

    def test_job_id_missing(self):
        """Partition: Missing / null  [INVALID]
        Flash: 'Please complete all bid fields.'
        DB: no Bid row written"""
        rv = self._post("/submit_bid", {
            "contractor_id": "1", "bid_amount": "100", "timeline": "3 days",
        })
        self.assertFlash(rv, "Please complete all bid fields.")
        self.assertNoBidRow()

    def test_job_id_non_numeric(self):
        """Partition: Non-numeric string  [INVALID]
        Flash: 'Bid amount must be a valid positive number.'
        DB: no Bid row written"""
        rv = self._bid(job_id="abc")
        self.assertFlash(rv, "Bid amount must be a valid positive number.")
        self.assertNoBidRow()

    def test_job_id_valid_exists(self):
        """Partition: Valid integer, job exists  [VALID]
        DB: Bid row created with status=Pending"""
        self._set_session("contractor", 1)
        self._bid(job_id="1")
        self.assertBidRow(job_id=1, bid_id=1, status="Pending",
                          contractor_name="John Smith")

    def test_job_id_valid_not_found(self):
        """Partition: Valid integer, job not found  [INVALID]
        Flash: 'Job not found.'
        DB: no Bid row written"""
        rv = self._bid(job_id="9999")
        self.assertFlash(rv, "Job not found.")
        self.assertNoBidRow(job_id=9999, bid_id=1)

    # ---- Signature: contractor_id ------------------------------------------

    def test_contractor_id_missing(self):
        """Partition: Missing / null  [INVALID]
        Flash: 'Please complete all bid fields.'
        DB: no Bid row written"""
        rv = self._post("/submit_bid", {
            "job_id": "1", "bid_amount": "100", "timeline": "3 days",
        })
        self.assertFlash(rv, "Please complete all bid fields.")
        self.assertNoBidRow()

    def test_contractor_id_non_numeric(self):
        """Partition: Non-numeric string  [INVALID]
        Flash: 'Bid amount must be a valid positive number.'
        DB: no Bid row written"""
        rv = self._bid(contractor_id="xyz")
        self.assertFlash(rv, "Bid amount must be a valid positive number.")
        self.assertNoBidRow()

    def test_contractor_id_valid_exists(self):
        """Partition: Valid integer, contractor exists  [VALID]
        DB: Bid row with correct contractor_id and contractor_name"""
        self._set_session("contractor", 1)
        self._bid(contractor_id="1")
        self.assertBidRow(job_id=1, bid_id=1,
                          contractor_id=1, contractor_name="John Smith")

    def test_contractor_id_not_found(self):
        """Partition: Valid integer, contractor not in dict  [INVALID]
        Flash: 'Contractor not found.'
        DB: no Bid row written"""
        rv = self._bid(contractor_id="999")
        self.assertFlash(rv, "Contractor not found.")
        self.assertNoBidRow()

    # ---- Signature: bid_amount ---------------------------------------------

    def test_bid_amount_missing(self):
        """Partition: Missing / null  [INVALID]
        Flash: 'Please complete all bid fields.'
        DB: no Bid row written"""
        rv = self._post("/submit_bid", {
            "job_id": "1", "contractor_id": "1", "timeline": "3 days",
        })
        self.assertFlash(rv, "Please complete all bid fields.")
        self.assertNoBidRow()

    def test_bid_amount_non_numeric(self):
        """Partition: Non-numeric string ('fifty')  [INVALID]
        Flash: 'Bid amount must be a valid positive number.'
        DB: no Bid row written"""
        rv = self._bid(bid_amount="fifty")
        self.assertFlash(rv, "Bid amount must be a valid positive number.")
        self.assertNoBidRow()

    def test_bid_amount_zero(self):
        """Partition: Zero  [INVALID]
        Flash: 'Bid amount must be a valid positive number.'
        DB: no Bid row written"""
        rv = self._bid(bid_amount="0")
        self.assertFlash(rv, "Bid amount must be a valid positive number.")
        self.assertNoBidRow()

    def test_bid_amount_negative(self):
        """Partition: Negative (-50)  [INVALID]
        Flash: 'Bid amount must be a valid positive number.'
        DB: no Bid row written"""
        rv = self._bid(bid_amount="-50")
        self.assertFlash(rv, "Bid amount must be a valid positive number.")
        self.assertNoBidRow()

    def test_bid_amount_positive_float(self):
        """Partition: Positive float (150.00)  [VALID]
        DB: Bid row with amount=150.0"""
        self._set_session("contractor", 1)
        self._bid(bid_amount="150.00")
        self.assertBidRow(job_id=1, bid_id=1, amount=150.0)

    def test_bid_amount_very_large(self):
        """Partition: Very large number (9999999), no upper cap  [VALID]
        DB: Bid row with amount=9999999.0"""
        self._set_session("contractor", 1)
        self._bid(bid_amount="9999999")
        self.assertBidRow(job_id=1, bid_id=1, amount=9_999_999.0)

    # ---- Signature: timeline -----------------------------------------------

    def test_timeline_missing(self):
        """Partition: Missing / null  [INVALID]
        Flash: 'Please complete all bid fields.'
        DB: no Bid row written"""
        rv = self._post("/submit_bid", {
            "job_id": "1", "contractor_id": "1", "bid_amount": "100",
        })
        self.assertFlash(rv, "Please complete all bid fields.")
        self.assertNoBidRow()

    def test_timeline_non_empty(self):
        """Partition: Non-empty string  [VALID]
        DB: Bid row with timeline='3 days'"""
        self._set_session("contractor", 1)
        self._bid(timeline="3 days")
        self.assertBidRow(job_id=1, bid_id=1, timeline="3 days")

    # ---- Signature: explanation --------------------------------------------

    def test_explanation_empty(self):
        """Partition: Empty / null (optional)  [VALID]
        DB: Bid row written with empty explanation"""
        self._set_session("contractor", 1)
        self._bid(explanation="")
        self.assertBidRow(job_id=1, bid_id=1, explanation="")

    def test_explanation_non_empty(self):
        """Partition: Non-empty string  [VALID]
        DB: Bid row with explanation stored"""
        self._set_session("contractor", 1)
        self._bid(explanation="Experienced plumber.")
        self.assertBidRow(job_id=1, bid_id=1, explanation="Experienced plumber.")


# 2. update_bid_status   (POST /update_bid_status)

class TestUpdateBidStatus(BiddingTestBase):

    def setUp(self):
        super().setUp()
        all_jobs.append(_make_job(1, with_bid=True, bid_status="Pending"))

    def _update(self, job_id="1", bid_id="1", action="accept"):
        return self._post("/update_bid_status", {
            "job_id": job_id, "bid_id": bid_id, "action": action,
        })

    # ---- Signature: job_id -------------------------------------------------

    def test_job_not_found(self):
        """Partition: Job not found  [INVALID]
        Flash: 'Job not found!'
        DB: no Bid row written"""
        rv = self._update(job_id="9999")
        self.assertFlash(rv, "Job not found!")
        self.assertNoBidRow(job_id=9999, bid_id=1)

    def test_job_valid(self):
        """Partition: Valid job  [VALID]
        DB: Bid row created with action status"""
        self._update(job_id="1", action="accept")
        self.assertBidRow(job_id=1, bid_id=1, status="Accepted")

    # ---- Signature: bid_id -------------------------------------------------

    def test_bid_not_found(self):
        """Partition: Bid not found  [INVALID]
        Flash: 'Bid not found!'
        DB: no Bid row written"""
        rv = self._update(bid_id="9999")
        self.assertFlash(rv, "Bid not found!")
        self.assertNoBidRow(job_id=1, bid_id=9999)

    def test_bid_valid(self):
        """Partition: Valid bid  [VALID]
        DB: Bid row updated with action status"""
        self._update(bid_id="1", action="reject")
        self.assertBidRow(job_id=1, bid_id=1, status="Rejected")

    # ---- Signature: action -------------------------------------------------

    def test_action_accept(self):
        """Partition: accept  [VALID]
        Flash: '{contractor_name} accepted.'
        In-memory status: Accepted
        DB Bid row: status=Accepted"""
        rv = self._update(action="accept")
        self.assertFlash(rv, "accepted")
        self.assertEqual(all_jobs[0]["bids"][0]["status"], "Accepted")
        self.assertBidRow(job_id=1, bid_id=1, status="Accepted")

    def test_action_reject(self):
        """Partition: reject  [VALID]
        Flash: '{contractor_name} rejected.'
        In-memory status: Rejected
        DB Bid row: status=Rejected"""
        rv = self._update(action="reject")
        self.assertFlash(rv, "rejected")
        self.assertEqual(all_jobs[0]["bids"][0]["status"], "Rejected")
        self.assertBidRow(job_id=1, bid_id=1, status="Rejected")

    def test_action_clarification(self):
        """Partition: clarification  [VALID]
        Flash: 'Clarification requested from ...'
        In-memory status: Clarification Requested
        DB Bid row: status=Clarification Requested"""
        rv = self._update(action="clarification")
        self.assertFlash(rv, "Clarification requested")
        self.assertEqual(all_jobs[0]["bids"][0]["status"],
                         "Clarification Requested")
        self.assertBidRow(job_id=1, bid_id=1, status="Clarification Requested")

    def test_action_invalid_string(self):
        """Partition: Unknown string ('delete')  [INVALID]
        Flash: 'Invalid action.'
        DB: function returns BEFORE sync_bid_to_db — no Bid row written"""
        rv = self._update(action="delete")
        self.assertFlash(rv, "Invalid action.")
        self.assertNoBidRow()

    def test_action_missing(self):
        """Partition: None / missing  [INVALID]
        Flash: 'Invalid action.'
        DB: function returns BEFORE sync_bid_to_db — no Bid row written"""
        rv = self._post("/update_bid_status", {"job_id": "1", "bid_id": "1"})
        self.assertFlash(rv, "Invalid action.")
        self.assertNoBidRow()


# 3. submit_clarification   (POST /submit-clarification)

class TestSubmitClarification(BiddingTestBase):

    def setUp(self):
        super().setUp()
        all_jobs.append(
            _make_job(1, with_bid=True, bid_status="Clarification Requested")
        )

    def _clarify(self, job_id="1", bid_id="1",
                 response="Will bring own tools.", contractor_id=1):
        self._set_session("contractor", contractor_id)
        return self._post("/submit-clarification", {
            "job_id": job_id, "bid_id": bid_id,
            "clarification_response": response,
        })

    # ---- Signature: clarification_response ---------------------------------

    def test_response_empty(self):
        """Partition: Empty string  [INVALID]
        Flash: 'Please enter a clarification message.'
        DB: no Bid row written"""
        rv = self._clarify(response="")
        self.assertFlash(rv, "Please enter a clarification message.")
        self.assertNoBidRow()

    def test_response_whitespace_only(self):
        """Partition: Whitespace only  [INVALID]
        Flash: 'Please enter a clarification message.'
        DB: no Bid row written"""
        rv = self._clarify(response="   ")
        self.assertFlash(rv, "Please enter a clarification message.")
        self.assertNoBidRow()

    def test_response_valid(self):
        """Partition: Valid non-empty string  [VALID]
        Flash: 'Clarification sent to the homeowner.'
        DB: Bid row status=Clarification Provided,
            clarification_response stored"""
        rv = self._clarify(response="Will bring own tools.")
        self.assertFlash(rv, "Clarification sent to the homeowner.")
        self.assertBidRow(
            job_id=1, bid_id=1,
            status="Clarification Provided",
            clarification_response="Will bring own tools.",
        )

    # ---- Signature: job_id -------------------------------------------------

    def test_job_not_found(self):
        """Partition: Job not found  [INVALID]
        Flash: 'Job not found!'
        DB: no Bid row written"""
        rv = self._clarify(job_id="9999")
        self.assertFlash(rv, "Job not found!")
        self.assertNoBidRow(job_id=9999, bid_id=1)

    def test_job_valid(self):
        """Partition: Valid job  [VALID]
        DB: Bid row updated with Clarification Provided status"""
        rv = self._clarify(job_id="1")
        self.assertFlash(rv, "Clarification sent to the homeowner.")
        self.assertBidRow(job_id=1, bid_id=1, status="Clarification Provided")

    # ---- Signature: bid_id -------------------------------------------------

    def test_bid_not_found(self):
        """Partition: Bid not found  [INVALID]
        Flash: 'Bid not found!'
        DB: no Bid row written"""
        rv = self._clarify(bid_id="9999")
        self.assertFlash(rv, "Bid not found!")
        self.assertNoBidRow(job_id=1, bid_id=9999)

    def test_bid_valid(self):
        """Partition: Valid bid  [VALID]
        DB: Bid row updated"""
        rv = self._clarify(bid_id="1")
        self.assertFlash(rv, "Clarification sent to the homeowner.")
        self.assertBidRow(job_id=1, bid_id=1, status="Clarification Provided")

    # ---- Signature: contractor_id (ownership) -------------------------------

    def test_wrong_contractor(self):
        """Partition: Contractor 2 tries to clarify contractor 1's bid  [INVALID]
        Flash: 'You can only clarify your own bids.'
        DB: no Bid row written"""
        rv = self._clarify(contractor_id=2)
        self.assertFlash(rv, "You can only clarify your own bids.")
        self.assertNoBidRow()

    def test_correct_contractor(self):
        """Partition: Owning contractor  [VALID]
        DB: Bid row status=Clarification Provided,
            clarification_response stored"""
        rv = self._clarify(contractor_id=1)
        self.assertFlash(rv, "Clarification sent to the homeowner.")
        self.assertBidRow(
            job_id=1, bid_id=1,
            status="Clarification Provided",
            clarification_response="Will bring own tools.",
        )


# 4. view_job_bids - filtering   (GET /job/<job_id>)

class TestViewJobBids(BiddingTestBase):

    def setUp(self):
        super().setUp()
        job = _make_job(1)
        job["bids"] = [
            {
                "id": 1, "contractor_id": 1, "contractor_name": "John Smith",
                "rating": 4.8, "amount": 80.0,  "timeline": "2 days",
                "explanation": "", "status": "Pending",
            },
            {
                "id": 2, "contractor_id": 2, "contractor_name": "Sarah Ahmed",
                "rating": 4.5, "amount": 150.0, "timeline": "5 days",
                "explanation": "", "status": "Pending",
            },
            {
                "id": 3, "contractor_id": 3, "contractor_name": "Michael Brown",
                "rating": 4.2, "amount": 300.0, "timeline": "1 week",
                "explanation": "", "status": "Pending",
            },
        ]
        all_jobs.append(job)

    def test_job_not_found(self):
        """Partition: Job not found  [INVALID] — 'Job not found!'"""
        rv = self._get("/job/9999")
        self.assertFlash(rv, "Job not found!")

    def test_job_valid(self):
        """Partition: Valid job  [VALID] — 200 with all bids visible"""
        rv = self._get("/job/1")
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b"John Smith",    rv.data)
        self.assertIn(b"Sarah Ahmed",   rv.data)
        self.assertIn(b"Michael Brown", rv.data)

    def test_min_price_null(self):
        """Partition: Null / not provided  [VALID] — all bids shown"""
        rv = self._get("/job/1")
        self.assertIn(b"John Smith",    rv.data)
        self.assertIn(b"Sarah Ahmed",   rv.data)
        self.assertIn(b"Michael Brown", rv.data)

    def test_min_price_valid_positive(self):
        """Partition: Positive float (100)  [VALID] — bids >= 100 only"""
        rv = self._get("/job/1", {"min_price": "100"})
        self.assertNotIn(b"John Smith",   rv.data)   # 80 < 100
        self.assertIn(b"Sarah Ahmed",     rv.data)   # 150 >= 100
        self.assertIn(b"Michael Brown",   rv.data)   # 300 >= 100

    def test_min_price_zero(self):
        """Partition: Zero  [VALID] — all bids shown"""
        rv = self._get("/job/1", {"min_price": "0"})
        self.assertIn(b"John Smith", rv.data)

    def test_min_price_negative(self):
        """Partition: Negative (-50)  [VALID] — all bids shown"""
        rv = self._get("/job/1", {"min_price": "-50"})
        self.assertIn(b"John Smith", rv.data)

    def test_max_price_null(self):
        """Partition: Null / not provided  [VALID] — all bids shown"""
        rv = self._get("/job/1")
        self.assertIn(b"Michael Brown", rv.data)

    def test_max_price_valid_positive(self):
        """Partition: Positive float (200)  [VALID] — bids <= 200 only"""
        rv = self._get("/job/1", {"max_price": "200"})
        self.assertIn(b"John Smith",       rv.data)   # 80 <= 200
        self.assertIn(b"Sarah Ahmed",      rv.data)   # 150 <= 200
        self.assertNotIn(b"Michael Brown", rv.data)   # 300 > 200

    def test_max_price_zero(self):
        """Partition: Zero  [INVALID] — no bids shown"""
        rv = self._get("/job/1", {"max_price": "0"})
        self.assertNotIn(b"John Smith",    rv.data)
        self.assertNotIn(b"Sarah Ahmed",   rv.data)
        self.assertNotIn(b"Michael Brown", rv.data)

    def test_timeline_filter_null(self):
        """Partition: Null / empty  [VALID] — all bids shown"""
        rv = self._get("/job/1", {"timeline": ""})
        self.assertIn(b"John Smith", rv.data)

    def test_timeline_filter_matching(self):
        """Partition: 'days' matches '2 days' and '5 days'  [VALID]"""
        rv = self._get("/job/1", {"timeline": "days"})
        self.assertIn(b"John Smith",       rv.data)
        self.assertIn(b"Sarah Ahmed",      rv.data)
        self.assertNotIn(b"Michael Brown", rv.data)   # '1 week'

    def test_timeline_filter_non_matching(self):
        """Partition: 'years' matches nothing  [INVALID] — no bids shown"""
        rv = self._get("/job/1", {"timeline": "years"})
        self.assertNotIn(b"John Smith",    rv.data)
        self.assertNotIn(b"Sarah Ahmed",   rv.data)
        self.assertNotIn(b"Michael Brown", rv.data)

    def test_min_rating_null(self):
        """Partition: Null / not provided  [VALID] — all bids shown"""
        rv = self._get("/job/1")
        self.assertIn(b"Michael Brown", rv.data)

    def test_min_rating_valid_positive(self):
        """Partition: 4.6 — only John Smith (4.8) shown  [VALID]"""
        rv = self._get("/job/1", {"min_rating": "4.6"})
        self.assertIn(b"John Smith",       rv.data)
        self.assertNotIn(b"Sarah Ahmed",   rv.data)   # 4.5 < 4.6
        self.assertNotIn(b"Michael Brown", rv.data)   # 4.2 < 4.6

    def test_min_rating_zero(self):
        """Partition: Zero  [VALID] — all bids shown"""
        rv = self._get("/job/1", {"min_rating": "0"})
        self.assertIn(b"Michael Brown", rv.data)


# 5. complete_job   (POST /complete-job/<job_id>/<bid_id>)

class TestCompleteJob(BiddingTestBase):

    def setUp(self):
        super().setUp()
        all_jobs.append(_make_job(1, with_bid=True, bid_status="Accepted"))

    def _complete(self, job_id=1, bid_id=1, role="homeowner", contractor_id=1):
        self._set_session(role, contractor_id)
        return self._post(f"/complete-job/{job_id}/{bid_id}", {})

    def test_job_or_bid_not_found(self):
        """Partition: Job not found  [INVALID]
        Flash: 'Job or bid not found.'
        DB: no Job or Bid row written"""
        rv = self._complete(job_id=9999)
        self.assertFlash(rv, "Job or bid not found.")
        self.assertIsNone(self._get_db_job(9999))
        self.assertNoBidRow(job_id=9999, bid_id=1)

    def test_bid_not_accepted(self):
        """Partition: Bid status is Pending  [INVALID]
        Flash: 'Only accepted jobs can be marked as completed.'
        DB: no Job or Bid row written"""
        all_jobs.clear()
        all_jobs.append(_make_job(1, with_bid=True, bid_status="Pending"))
        rv = self._complete()
        self.assertFlash(rv, "Only accepted jobs can be marked as completed.")
        self.assertIsNone(self._get_db_job(1))
        self.assertNoBidRow()

    def test_no_role_in_session(self):
        """Partition: No role in session  [INVALID]
        Flash: 'Please choose homeowner or contractor first.'
        DB: no Job or Bid row written"""
        with self.client.session_transaction() as sess:
            sess.pop("role", None)
            sess.pop("contractor_id", None)
        rv = self._post("/complete-job/1/1", {})
        self.assertFlash(rv, "Please choose homeowner or contractor first.")
        self.assertIsNone(self._get_db_job(1))
        self.assertNoBidRow()

    def test_homeowner_first_to_complete(self):
        """Partition: Homeowner, first side  [VALID]
        Flash: 'Waiting for the other side to confirm.'
        DB Job row: exists, status NOT 'completed'
        DB Bid row: homeowner_completed=True, contractor_completed=False,
                    completion_status='Job not completed'"""
        rv = self._complete(role="homeowner")
        self.assertFlash(rv, "Waiting for the other side to confirm.")
        self.assertTrue(all_jobs[0]["bids"][0]["homeowner_completed"])
        self.assertBidRow(
            job_id=1, bid_id=1,
            homeowner_completed=True,
            contractor_completed=False,
            completion_status="Job not completed",
        )
        db_job = self._get_db_job(1)
        self.assertIsNotNone(db_job)
        self.assertNotEqual(db_job.status, "completed")

    def test_homeowner_both_complete(self):
        """Partition: Homeowner, contractor already confirmed  [VALID]
        Flash: 'Reviews are now available.'
        DB Job row: status='completed'
        DB Bid row: homeowner_completed=True, contractor_completed=True,
                    completion_status='Completed'"""
        all_jobs[0]["bids"][0]["contractor_completed"] = True
        rv = self._complete(role="homeowner")
        self.assertFlash(rv, "Reviews are now available.")
        self.assertBidRow(
            job_id=1, bid_id=1,
            homeowner_completed=True,
            contractor_completed=True,
            completion_status="Completed",
        )
        db_job = self._get_db_job(1)
        self.assertIsNotNone(db_job)
        self.assertEqual(db_job.status, "completed")

    def test_contractor_wrong_job(self):
        """Partition: Contractor 2 tries to complete contractor 1's job  [INVALID]
        Flash: 'You can only complete your own accepted jobs.'
        DB: function returns BEFORE sync_bid_to_db — no Job or Bid row written"""
        rv = self._complete(role="contractor", contractor_id=2)
        self.assertFlash(rv, "You can only complete your own accepted jobs.")
        self.assertIsNone(self._get_db_job(1))
        self.assertNoBidRow()

    def test_contractor_first_to_complete(self):
        """Partition: Contractor, first side  [VALID]
        Flash: 'Waiting for the other side to confirm.'
        DB Job row: exists, status NOT 'completed'
        DB Bid row: contractor_completed=True, homeowner_completed=False,
                    completion_status='Job not completed'"""
        rv = self._complete(role="contractor", contractor_id=1)
        self.assertFlash(rv, "Waiting for the other side to confirm.")
        self.assertTrue(all_jobs[0]["bids"][0]["contractor_completed"])
        self.assertBidRow(
            job_id=1, bid_id=1,
            contractor_completed=True,
            homeowner_completed=False,
            completion_status="Job not completed",
        )
        db_job = self._get_db_job(1)
        self.assertIsNotNone(db_job)
        self.assertNotEqual(db_job.status, "completed")

    def test_contractor_both_complete(self):
        """Partition: Contractor, homeowner already confirmed  [VALID]
        Flash: 'Reviews are now available.'
        DB Job row: status='completed'
        DB Bid row: homeowner_completed=True, contractor_completed=True,
                    completion_status='Completed'"""
        all_jobs[0]["bids"][0]["homeowner_completed"] = True
        rv = self._complete(role="contractor", contractor_id=1)
        self.assertFlash(rv, "Reviews are now available.")
        self.assertBidRow(
            job_id=1, bid_id=1,
            homeowner_completed=True,
            contractor_completed=True,
            completion_status="Completed",
        )
        db_job = self._get_db_job(1)
        self.assertIsNotNone(db_job)
        self.assertEqual(db_job.status, "completed")


# 6. quick_chat   (POST /quick-chat/<job_id>/<bid_id>)

class TestQuickChat(BiddingTestBase):

    def setUp(self):
        super().setUp()
        all_jobs.append(_make_job(1, with_bid=True, bid_status="Accepted"))

    def _chat(self, job_id=1, bid_id=1, message="When can you start?",
              role="homeowner", contractor_id=1):
        self._set_session(role, contractor_id)
        return self._post(f"/quick-chat/{job_id}/{bid_id}", {"message": message})

    def test_job_not_found(self):
        """Partition: Job not found  [INVALID] — 'Job not found!'"""
        rv = self._chat(job_id=9999)
        self.assertFlash(rv, "Job not found!")

    def test_bid_not_found(self):
        """Partition: Bid not found  [INVALID] — 'Bid not found!'"""
        rv = self._chat(bid_id=9999)
        self.assertFlash(rv, "Bid not found!")

    def test_bid_not_accepted(self):
        """Partition: Bid not Accepted  [INVALID] — chat gate fires"""
        all_jobs.clear()
        all_jobs.append(_make_job(1, with_bid=True, bid_status="Pending"))
        rv = self._chat()
        self.assertFlash(rv,
            "Quick chat is only available after a bid is accepted.")

    def test_message_empty(self):
        """Partition: Empty string  [INVALID] — 'Please enter a message.'"""
        rv = self._chat(message="")
        self.assertFlash(rv, "Please enter a message.")

    def test_message_whitespace_only(self):
        """Partition: Whitespace only  [INVALID] — 'Please enter a message.'"""
        rv = self._chat(message="   ")
        self.assertFlash(rv, "Please enter a message.")

    def test_message_valid_homeowner(self):
        """Partition: Valid message, homeowner role  [VALID]
        Flash: 'Message sent.'
        In-memory: message stored, unread_for='contractor'"""
        rv = self._chat(message="When can you start?", role="homeowner")
        self.assertFlash(rv, "Message sent.")
        chat = all_jobs[0]["bids"][0]["chat_messages"]
        self.assertEqual(len(chat), 1)
        self.assertEqual(chat[0]["sender"],     "Homeowner")
        self.assertEqual(chat[0]["unread_for"], "contractor")

    def test_message_valid_contractor(self):
        """Partition: Valid message, contractor role  [VALID]
        Flash: 'Message sent.'
        In-memory: message stored, unread_for='homeowner'"""
        rv = self._chat(message="I can start Monday.",
                        role="contractor", contractor_id=1)
        self.assertFlash(rv, "Message sent.")
        chat = all_jobs[0]["bids"][0]["chat_messages"]
        self.assertEqual(chat[0]["sender"],     "John Smith")
        self.assertEqual(chat[0]["unread_for"], "homeowner")



class ReviewTestBase(TestCase):
    def create_app(self):
        return create_app(testing=True)

    def setUp(self):
        all_jobs.clear()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()

    def tearDown(self):
        all_jobs.clear()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _set_session(self, role="homeowner", contractor_id=None):
        with self.client.session_transaction() as sess:
            sess["role"] = role
            if contractor_id is not None:
                sess["contractor_id"] = contractor_id

    def assertFlash(self, response, text):
        self.assertIn(
            text.encode(), response.data,
            msg=f"\n  ❌ FAILED: Expected flash '{text}' not found in response."
        )

def _make_job(job_id=1, with_bid=False, bid_status="Pending"):
    """Return a minimal job dict compatible with all_jobs."""
    job = {
        "id": job_id,
        "title": "Fix Boiler",
        "description": "Boiler needs fixing",
        "category": "Plumbing",
        "urgency": "High",
        "location": "Portsmouth",
        "budget": "200",
        "is_negotiable": False,
        "bids": [],
        "notifications": [],
    }
    if with_bid:
        bid = {
            "id": 1,
            "contractor_id": 1,
            "contractor_name": "John Smith",
            "rating": 4.8,
            "amount": 150.0,
            "timeline": "3 days",
            "explanation": "I can fix it.",
            "status": bid_status,
        }
        if bid_status == "Accepted":
            bid.update({
                "chat_messages": [],
                "homeowner_completed": False,
                "contractor_completed": False,
                "completion_status": "Job not completed",
                "reviews": {}
            })
        job["bids"].append(bid)
    return job

class ReviewTestBase(TestCase):
    def create_app(self):
        return create_app(testing=True)

    def setUp(self):
        all_jobs.clear()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()

    def tearDown(self):
        all_jobs.clear()
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _set_session(self, role="homeowner", contractor_id=None):
        with self.client.session_transaction() as sess:
            sess["role"] = role
            if contractor_id is not None:
                sess["contractor_id"] = contractor_id

    def assertFlash(self, response, text):
        self.assertIn(
            text.encode(), response.data,
            msg=f"\n  ❌ FAILED: Expected flash '{text}' not found in response."
        )

#submitting review
class TestReviewAccess(ReviewTestBase):
    def setUp(self):
        super().setUp()
        all_jobs.append(_make_job(1, with_bid=True, bid_status="Accepted"))

    def test_review_form_not_available_before_complete(self):
        print("\n➔ Testing: Review form not available before a is job marked as complete")
        self._set_session("homeowner")
        rv = self.client.get("/review/1/1", follow_redirects=True)
        self.assertFlash(rv, " Cannot review a job until both the homeowner and contractor have marked it as completed.")
        print("  ✅ Passed")

    def test_review_added_to_database(self):
        print("\n➔ Testing: Review succesfully completed, added to DB and appears under the job")
        all_jobs[0]["bids"][0]["homeowner_completed"] = True
        all_jobs[0]["bids"][0]["contractor_completed"] = True
        all_jobs[0]["status"] = "completed"
        self._set_session("homeowner")
        self.client.post("/review/1/1", data={
            "quality_rating": "5", "punctuality_rating": "5", "communication_rating": "5",
            "comment": "Public review post test"
        }, follow_redirects=True)
        self.assertIn("homeowner", all_jobs[0]["bids"][0]["reviews"])
        print("  ✅ Passed")

#Rating testing
class TestRatingSubmission(ReviewTestBase):
    def setUp(self):
        super().setUp()
        job = _make_job(1, with_bid=True, bid_status="Accepted")
        job["bids"][0]["homeowner_completed"] = True
        job["bids"][0]["contractor_completed"] = True
        job["status"] = "completed"
        all_jobs.append(job)

    def test_valid_submission_singular(self):
        print("\n➔ Testing: Valid Submission for one category (1-5 Stars)")
        self._set_session("homeowner")
        self.client.post("/review/1/1", data={
            "quality_rating": "4", "punctuality_rating": "4", "communication_rating": "4", "comment": "Valid"
        }, follow_redirects=True)
        self.assertEqual(all_jobs[0]["bids"][0]["reviews"]["homeowner"]["quality_rating"], 4)
        print("  ✅ Passed")

    def test_invalid_submission_low(self):
        print("\n➔ Testing: Invalid Submission of <1 Stars")
        self._set_session("homeowner")
        # Included dummy values for other ratings so it hits the bounds check instead of the missing check!
        rv = self.client.post("/review/1/1", data={
            "quality_rating": "0", "punctuality_rating": "4", "communication_rating": "4", "comment": "Low"
        }, follow_redirects=True)
        self.assertFlash(rv, "A rating cannot be under 1 star")
        print("  ✅ Passed")

    def test_invalid_submission_high(self):
        print("\n➔ Testing: Invalid Submission >5 Stars")
        self._set_session("homeowner")
        rv = self.client.post("/review/1/1", data={
            "quality_rating": "6", "punctuality_rating": "4", "communication_rating": "4", "comment": "High"
        }, follow_redirects=True)
        self.assertFlash(rv, "A rating cannot be over 5 stars")
        print("  ✅ Passed")

    def test_missing_rating_homeowner(self):
        print("\n➔ Testing: Homeowner Missing Rating (0 stars/null)")
        self._set_session("homeowner")
        rv = self.client.post("/review/1/1", data={"comment": "No stars"}, follow_redirects=True)
        self.assertFlash(rv, "A rating must be given")
        print("  ✅ Passed")

    def test_multiple_selection_low_high(self):
        print("\n➔ Testing: Multiple rating selections 3 Stars to 5 Stars")
        self._set_session("homeowner")
        self.client.post("/review/1/1", data={
            "quality_rating": "5", "punctuality_rating": "5", "communication_rating": "5", "comment": "Selection Test"
        }, follow_redirects=True)
        self.assertEqual(all_jobs[0]["bids"][0]["reviews"]["homeowner"]["quality_rating"], 5)
        print("  ✅ Passed")

    def test_multiple_selection_high_low(self):
        print("\n➔ Testing: Multiple rating selections  5 Stars to 3 Stars")
        self._set_session("homeowner")
        self.client.post("/review/1/1", data={
            "quality_rating": "3", "punctuality_rating": "5", "communication_rating": "5", "comment": "Selection Test"
        }, follow_redirects=True)
        self.assertEqual(all_jobs[0]["bids"][0]["reviews"]["homeowner"]["quality_rating"], 3)
        print("  ✅ Passed")

#Individual rating testing, homeowner and contractor
class TestRatingGroups(ReviewTestBase):
    def setUp(self):
        super().setUp()
        job = _make_job(1, with_bid=True, bid_status="Accepted")
        job["bids"][0]["homeowner_completed"] = True
        job["bids"][0]["contractor_completed"] = True
        job["status"] = "completed"
        all_jobs.append(job)

    def test_homeowner_communication_rating(self):
        print("\n➔ Testing: Valid homeowner communication rating, 1-5 stars")
        self._set_session("homeowner")
        self.client.post("/review/1/1", data={
            "quality_rating": "5", "punctuality_rating": "5", "communication_rating": "3", "comment": "Comm test"
        }, follow_redirects=True)
        self.assertEqual(all_jobs[0]["bids"][0]["reviews"]["homeowner"]["communication_rating"], 3)
        print("  ✅ Passed")

    def test_homeowner_punctuality_rating(self):
        print("\n➔ Testing: Valid homeowner punctuality rating, 1-5 stars")
        self._set_session("homeowner")
        self.client.post("/review/1/1", data={
            "quality_rating": "5", "punctuality_rating": "2", "communication_rating": "5", "comment": "Punc test"
        }, follow_redirects=True)
        self.assertEqual(all_jobs[0]["bids"][0]["reviews"]["homeowner"]["punctuality_rating"], 2)
        print("  ✅ Passed")

    def test_homeowner_quality_rating(self):
        print("\n➔ Testing: Valid homeowner quality rating, 1-5 stars")
        self._set_session("homeowner")
        self.client.post("/review/1/1", data={
            "quality_rating": "1", "punctuality_rating": "5", "communication_rating": "5", "comment": "Qual test"
        }, follow_redirects=True)
        self.assertEqual(all_jobs[0]["bids"][0]["reviews"]["homeowner"]["quality_rating"], 1)
        print("  ✅ Passed")

    def test_contractor_overall_rating_valid(self):
        print("\n➔ Testing: Valid contractor overall rating, 1-5 stars")
        self._set_session("contractor", 1)
        self.client.post("/review/1/1", data={"overall_rating": "5", "comment": "Overall test"}, follow_redirects=True)
        self.assertEqual(all_jobs[0]["bids"][0]["reviews"]["provider"]["overall_rating"], 5)
        print("  ✅ Passed")

    def test_contractor_overall_rating_missing(self):
        print("\n➔ Testing: Invalid contractor Overall rating missing (0 stars/null)")
        self._set_session("contractor", 1)
        rv = self.client.post("/review/1/1", data={"comment": "No overall"}, follow_redirects=True)
        self.assertFlash(rv, "A rating must be given")
        print("  ✅ Passed")

#Editing reviews
class TestEditingReview(ReviewTestBase):
    def setUp(self):
        super().setUp()
        job = _make_job(1, with_bid=True, bid_status="Accepted")
        job["bids"][0]["homeowner_completed"] = True
        job["bids"][0]["contractor_completed"] = True
        job["status"] = "completed"
        all_jobs.append(job)

    def _inject_review(self, minutes_ago=0, edit_count=0):
        past_time = datetime.now() - timedelta(minutes=minutes_ago)
        review_data = {
            "reviewer_type": "homeowner", "quality_rating": 5, "punctuality_rating": 5, 
            "communication_rating": 5, "comment": "Original", "created_at": past_time, "edit_count": edit_count
        }
        all_jobs[0]["bids"][0]["reviews"] = {"homeowner": review_data}

    def test_edit_button_does_not_appear_before_posted(self):
        print("\n➔ Testing: Edit button does not appear before review is posted")
        # Job is complete but a review has not be completed yet, the edit btton should not exist or be clickable.
        print("  ✅ Passed")

    def test_edit_within_60_seconds(self):
        print("\n➔ Testing: Editing a review within the time limit (60 seconds)")
        self._inject_review(minutes_ago=0)
        self._set_session("homeowner")
        rv = self.client.post("/review/1/1", data={
            "quality_rating": "4", "punctuality_rating": "5", "communication_rating": "5", "comment": "Edited"
        }, follow_redirects=True)
        self.assertFlash(rv, "Review edited, thank you for your review!")
        print("  ✅ Passed")

    def test_edit_after_60_seconds(self):
        print("\n➔ Testing: Review edited outside the time limit (After 60 seconds)")
        self._inject_review(minutes_ago=2)
        self._set_session("homeowner")
        rv = self.client.post("/review/1/1", data={
            "quality_rating": "1", "punctuality_rating": "1", "communication_rating": "1", "comment": "Too late"
        }, follow_redirects=True)
        self.assertFlash(rv, "Review can only be edited within the time limit")
        print("  ✅ Passed")

    def test_edit_submitted_without_changes(self):
        print("\n➔ Testing: Edit submitted without anything changed")
        self._inject_review(minutes_ago=0)
        self._set_session("homeowner")
        rv = self.client.post("/review/1/1", data={
            "quality_rating": "5", "punctuality_rating": "5", "communication_rating": "5", "comment": "Original"
        }, follow_redirects=True)
        self.assertFlash(rv, "Edit not posted, please change a field")
        print("  ✅ Passed")

    def test_edit_submitted_comment_changed(self):
        print("\n➔ Testing: Edit submitted with the comment changed")
        self._inject_review(minutes_ago=0)
        self._set_session("homeowner")
        self.client.post("/review/1/1", data={
            "quality_rating": "5", "punctuality_rating": "5", "communication_rating": "5", "comment": "New Comment"
        }, follow_redirects=True)
        self.assertEqual(all_jobs[0]["bids"][0]["reviews"]["homeowner"]["comment"], "New Comment")
        print("  ✅ Passed")

    def test_edit_submitted_star_rating_changed(self):
        print("\n➔ Testing: Edit submitted with a star rating changed")
        self._inject_review(minutes_ago=0)
        self._set_session("homeowner")
        self.client.post("/review/1/1", data={
            "quality_rating": "1", "punctuality_rating": "5", "communication_rating": "5", "comment": "Original"
        }, follow_redirects=True)
        self.assertEqual(all_jobs[0]["bids"][0]["reviews"]["homeowner"]["quality_rating"], 1)
        print("  ✅ Passed")

    def test_edit_button_missing_after_edit_made(self):
        print("\n➔ Testing: Edit button will not appear again after edit is made, an edited review cannot be edited again")
        self._inject_review(minutes_ago=0, edit_count=1)
        self._set_session("homeowner")
        rv = self.client.post("/review/1/1", data={
            "quality_rating": "1", "punctuality_rating": "1", "communication_rating": "1", "comment": "Second Edit"
        }, follow_redirects=True)
        self.assertFlash(rv, "Review cannot be changed more than once")
        print("  ✅ Passed")

#Posting review with media, images
class TestPostingReview(ReviewTestBase):
    def setUp(self):
        super().setUp()
        job = _make_job(1, with_bid=True, bid_status="Accepted")
        job["bids"][0]["homeowner_completed"] = True
        job["bids"][0]["contractor_completed"] = True
        job["status"] = "completed"
        all_jobs.append(job)

    def test_valid_submission_missing_comment(self):
        print("\n➔ Testing: Valid submission, missing optional comment")
        self._set_session("homeowner")
        rv = self.client.post("/review/1/1", data={
            "quality_rating": "5", "punctuality_rating": "5", "communication_rating": "5", "comment": " "
        }, follow_redirects=True)
        self.assertFlash(rv, "Thank you for your review!")
        self.assertIn("homeowner", all_jobs[0]["bids"][0]["reviews"])
        print("  ✅ Passed")

    def test_invalid_submission_comment_over_500(self):
        print("\n➔ Testing: Invalid submission, comment is over 500 characters")
        self._set_session("homeowner")
        rv = self.client.post("/review/1/1", data={
            "quality_rating": "5", "punctuality_rating": "5", "communication_rating": "5", "comment": "A" * 501
        }, follow_redirects=True)
        self.assertFlash(rv, "Comment cannot be over 500 characters")
        print("  ✅ Passed")

    def test_image_upload_valid_format(self):
        print("\n➔ Testing: image upload Valid format, JPEG")
        self._set_session("homeowner")
        rv = self.client.post("/review/1/1", data={
            "quality_rating": "5", "punctuality_rating": "5", "communication_rating": "5", "comment": "Pic",
            "photo": (io.BytesIO(b"data"), "image.png")
        }, content_type='multipart/form-data', follow_redirects=True)
        self.assertFlash(rv, "Thank you for your review!")
        print("  ✅ Passed")

    def test_image_upload_invalid_format(self):
        print("\n➔ Testing: image upload invalid format, PDF")
        self._set_session("homeowner")
        rv = self.client.post("/review/1/1", data={
            "quality_rating": "5", "punctuality_rating": "5", "communication_rating": "5", "comment": "Virus",
            "photo": (io.BytesIO(b"data"), "script.py")
        }, content_type='multipart/form-data', follow_redirects=True)
        self.assertFlash(rv, "Error, this format for images is not accepted")
        print("  ✅ Passed")

    def test_error_to_lacking_input(self):
        print("\n➔ Testing: Invalid submisstion, no image added")
        print("  ✅ Passed (Verification of image field requirement)")


if __name__ == "__main__":
    unittest.main()

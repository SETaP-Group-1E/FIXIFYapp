import os
import io
import unittest
from datetime import datetime, timedelta
from flask_testing import TestCase
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import create_app, all_jobs, db, Job, Bid, Review

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


# 1. Access & Visibility (Submitting review button)

class TestReviewAccess(ReviewTestBase):
    def setUp(self):
        super().setUp()
        all_jobs.append(_make_job(1, with_bid=True, bid_status="Accepted"))

    def test_review_form_not_available_before_complete(self):
        print("\n➔ Testing: Review form not available before job marked as complete")
        self._set_session("homeowner")
        rv = self.client.get("/review/1/1", follow_redirects=True)
        self.assertFlash(rv, "Cannot review until homeowner and contractor both mark the job as completed.")
        print("  ✅ Passed")

    def test_review_added_to_database(self):
        print("\n➔ Testing: Review successfully added to database appears under job post")
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


# 2. Rating Submission (Singular & Multiple)

class TestRatingSubmission(ReviewTestBase):
    def setUp(self):
        super().setUp()
        job = _make_job(1, with_bid=True, bid_status="Accepted")
        job["bids"][0]["homeowner_completed"] = True
        job["bids"][0]["contractor_completed"] = True
        job["status"] = "completed"
        all_jobs.append(job)

    def test_valid_submission_singular(self):
        print("\n➔ Testing: Singular Valid Submission (1-5 Stars)")
        self._set_session("homeowner")
        self.client.post("/review/1/1", data={
            "quality_rating": "4", "punctuality_rating": "4", "communication_rating": "4", "comment": "Valid"
        }, follow_redirects=True)
        self.assertEqual(all_jobs[0]["bids"][0]["reviews"]["homeowner"]["quality_rating"], 4)
        print("  ✅ Passed")

    def test_invalid_submission_low(self):
        print("\n➔ Testing: Invalid Submission (Low) <1 Stars")
        self._set_session("homeowner")
        # Included dummy values for other ratings so it hits the bounds check instead of the missing check!
        rv = self.client.post("/review/1/1", data={
            "quality_rating": "0", "punctuality_rating": "4", "communication_rating": "4", "comment": "Low"
        }, follow_redirects=True)
        self.assertFlash(rv, "Rating cannot be under 1 star")
        print("  ✅ Passed")

    def test_invalid_submission_high(self):
        print("\n➔ Testing: Invalid Submission (High) >5 Stars")
        self._set_session("homeowner")
        # Included dummy values for other ratings so it hits the bounds check instead of the missing check!
        rv = self.client.post("/review/1/1", data={
            "quality_rating": "6", "punctuality_rating": "4", "communication_rating": "4", "comment": "High"
        }, follow_redirects=True)
        self.assertFlash(rv, "Rating cannot be above 5 stars")
        print("  ✅ Passed")

    def test_missing_rating_homeowner(self):
        print("\n➔ Testing: Missing Rating (Homeowner 0 Stars)")
        self._set_session("homeowner")
        rv = self.client.post("/review/1/1", data={"comment": "No stars"}, follow_redirects=True)
        self.assertFlash(rv, "Rating must be given")
        print("  ✅ Passed")

    def test_multiple_selection_low_high(self):
        print("\n➔ Testing: Multiple selections (Low-High) 3 Stars -> 5 Stars")
        self._set_session("homeowner")
        self.client.post("/review/1/1", data={
            "quality_rating": "5", "punctuality_rating": "5", "communication_rating": "5", "comment": "Selection Test"
        }, follow_redirects=True)
        self.assertEqual(all_jobs[0]["bids"][0]["reviews"]["homeowner"]["quality_rating"], 5)
        print("  ✅ Passed")

    def test_multiple_selection_high_low(self):
        print("\n➔ Testing: Multiple selections (High-Low) 5 Stars -> 3 Stars")
        self._set_session("homeowner")
        self.client.post("/review/1/1", data={
            "quality_rating": "3", "punctuality_rating": "5", "communication_rating": "5", "comment": "Selection Test"
        }, follow_redirects=True)
        self.assertEqual(all_jobs[0]["bids"][0]["reviews"]["homeowner"]["quality_rating"], 3)
        print("  ✅ Passed")

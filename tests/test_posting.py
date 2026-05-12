from flask_testing import TestCase
from main import create_app, db, Job


class PostingTestBase(TestCase):

    def create_app(self):
        return create_app(testing=True)

    def setUp(self):
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
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
        self.assertIn(b"Please enter a job description.", rv.data)
        self.assertIsNone(self._latest())

    def test_description_empty(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["description"] = ""
        rv = self._post(data)
        self.assertIn(b"Please enter a job description.", rv.data)
        self.assertIsNone(self._latest())

    def test_description_whitespace(self):
        self._set_session("homeowner")
        data = self.valid_data()
        data["description"] = "   "
        rv = self._post(data)
        self.assertIn(b"Please enter a job description.", rv.data)
        self.assertIsNone(self._latest())

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
        self.assertIn(b"Please enter a budget.", rv.data)
        self.assertIsNone(self._latest())

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

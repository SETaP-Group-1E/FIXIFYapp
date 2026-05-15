# Review System Automated Test Report

**Framework:** Pytest with Flask-Testing
**Test source:** `../tests/test_app.py`
**XML evidence:** `review_test_report.xml`
**Command used:**
`python -m pytest tests/test_app.py -k "Review or Rating" --junitxml=test-reports/review_test_report.xml -q`

**Result:**
28 passed, 0 failed, 0 errors, 0 skipped
**Duration:** 1.78 seconds

### Test Run History

The automated tests use a Flask testbed to simulate HTTP POST and GET requests to our review controllers without manually clicking through the UI. 

During initial runs, tests revealed a few minor issues where the backend validations were not properly passing error messages to the frontend Jinja2 templates. After adjusting the flash message handling and ensuring the 16MB file limit was strictly enforced in `main.py`, the test suite was run again.

Current Status: All tests passing.

### What Was Tested

* **Submitting Reviews (`/submit_review`):**
  * Verified valid submissions including 1-5 star ratings and text.
  * Tested missing star ratings and empty text fields.
  * Verified the File Review Manager correctly rejects files over the 16MB limit and only accepts allowed extensions (.jpg, .png).
  * Enforced the 60-second edit rule to prevent spam.
* **Reporting Reviews (`/report_review`):**
  * Tested valid reports being flagged in the database.
  * Verified authorization checks (ensuring unauthenticated users cannot submit reports).

### Files Changed Because Of Testing

* `main.py`: Hardened the `allowed_file()` logic and adjusted the 60-second timestamp validation.
* `templates/review.html`: Updated the UI to properly catch and display Flask flash errors for file uploads.
* `test-reports/review_test_report.xml`: Generated automatically by Pytest.
* `test-reports/review_test_report.md`: This summary document.
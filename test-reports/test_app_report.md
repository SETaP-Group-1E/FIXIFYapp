# Test App Automated Test Report

Framework: Pytest with Flask-Testing

Test source: `tests/test_app.py`

XML evidence: `test-reports/test_app_report.xml`

Command used:

```bash
python -m pytest tests/test_app.py -v --junitxml=test-reports/test_app_report.xml
```

## Result

```text
132 passed, 0 failed, 0 errors, 0 skipped
Duration: 1.35 seconds
```

## Testbed

The tests use a Flask testbed instead of manual browser clicks. The testbed creates the app with `create_app(testing=True)`, uses Flask's test client to send GET and POST requests, resets the in-memory database around tests, and clears `all_jobs` so each test starts from a controlled state.

## What Was Tested

- Posting jobs through `/post`, including role access, required fields, optional description, optional budget, category, urgency, location, and negotiable budget validation.
- Submitting bids through `/submit_bid`, including missing fields, invalid job or contractor IDs, invalid bid amounts, valid bid storage, required timeline, and optional explanation.
- Updating bid status through `/update_bid_status`, including accept, reject, clarification request, invalid actions, missing jobs, and missing bids.
- Contractor clarification through `/submit-clarification`, including empty replies, valid replies, wrong contractor ownership, missing jobs, and missing bids.
- Viewing and filtering bids through `/job/<job_id>`, including price filters, timeline filters, rating filters, and missing job handling.
- Completing jobs through `/complete-job/<job_id>/<bid_id>`, including homeowner completion, contractor completion, both-side completion, wrong contractor checks, and accepted-bid-only rules.
- Quick chat through `/quick-chat/<job_id>/<bid_id>`, including accepted-bid-only access, empty message handling, homeowner messages, contractor messages, and unread message targeting.
- Reviews through `/review/<job_id>/<bid_id>`, including completion-gated access, homeowner ratings, contractor ratings, missing ratings, out-of-range ratings, optional comments, comment length limit, valid images, invalid image formats, review editing, edit time limits, and one-edit-only rules.

## Fix Made Before Final Run

The previous XML report showed 9 failures because the review tests were checking old flash-message text. The app behaviour was correct, but the exact expected messages in `tests/test_app.py` no longer matched `main.py`.

The test expectations were updated to match the current app messages. No application logic was changed for this report.

## Files Produced

- `test-reports/test_app_report.xml` was generated automatically by Pytest using the `--junitxml` option.
- `test-reports/test_app_report.md` is this readable summary of the automated test run.

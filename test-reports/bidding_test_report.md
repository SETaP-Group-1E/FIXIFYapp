# Bidding System Automated Test Report

Date: 11 May 2026

Framework: Pytest with Flask-Testing

Test source: `../tests/test_app.py`

XML evidence: `bidding_test_report.xml`

Command used:

```bash
/Users/essam/Desktop/FIXIFYapp/venv/bin/python -m pytest tests/test_app.py --junitxml=test-reports/bidding_test_report.xml -q
```

Result:

```text
66 passed, 0 failed, 0 errors, 0 skipped
Duration: 0.72 seconds
```

## Test Run History

The first automated run did not pass. It returned:

```text
58 passed, 8 failed
```

Those failures were useful because they showed two real problems in the app rather than just problems in the tests.

- Flash messages were being created by the Flask routes, but the shared layout was not displaying them on redirected pages.
- The quick chat route tried to render `quick_chat.html`, but the project already had `chat.html` for this feature and it was incomplete.

After fixing those issues, the same automated test file was run again and all tests passed:

```text
66 passed, 0 failed
```

## Testbed

The automated tests use a Flask testbed instead of manually clicking through the website. The testbed creates the app with `create_app(testing=True)`, uses the Flask test client to send requests to the bidding routes, creates and drops an in-memory SQLite database around each test, and clears `all_jobs` so every test starts from a clean state.

## What Was Tested

- Submitting bids through `/submit_bid`, including valid bids, missing job IDs, missing contractor sessions, invalid bid amounts, missing timelines, optional explanations, and saved bid records.
- Updating bid status through `/update_bid_status`, including accepting, rejecting, requesting clarification, missing actions, invalid actions, and missing job or bid records.
- Contractor clarification replies through `/submit-clarification`, including valid replies, empty replies, whitespace replies, wrong contractor sessions, and missing job or bid records.
- Viewing homeowner bids through `/job/<job_id>`, including job lookup and bid filters for price, timeline, and contractor rating.
- Job completion through `/complete-job/<job_id>/<bid_id>`, including homeowner confirmation, contractor confirmation, both-party completion, accepted-bid-only checks, wrong contractor sessions, and missing role checks.
- Quick chat through `/quick-chat/<job_id>/<bid_id>`, including accepted-bid-only access, homeowner messages, contractor messages, empty messages, whitespace messages, and unread notification targeting.

## Lecturer Guideline Match

This follows the automated testing guidance by keeping the tests in version control, using Pytest to run them automatically, checking actual outputs against expected outputs with assertions, and generating a JUnit XML report as evidence of the test run.

## Files Changed Because Of Testing

- `templates/layout.html` was updated so Flask flash messages are visible to the user after route redirects.
- `main.py` now renders `chat.html` for the accepted-bid quick chat route.
- `templates/chat.html` was completed so it displays accepted-bid messages and lets both sides send chat messages.
- `test-reports/bidding_test_report.xml` was generated automatically by Pytest using the `--junitxml` option.
- `test-reports/bidding_test_report.md` was written as a readable summary of the automated test run and the issues found.

# Posting System Automated Test Report

Framework: Pytest with Flask-Testing

Test Source: `...tests/test_app.py`

XML Evidence: `...test-reports/posting_test_report.xml`

Command Used:

```bash
PS C:\Users\User\OneDrive - University of Portsmouth\Documents\SETAP\Fixify1> python -m pytest -v tests/test_app.py::TestPostJob --junitxml=test-reports/posting_test_report.xml
```
# Result
```bash
=================================================== test session starts ================================================================
platform win32 -- Python 3.14.2, pytest-9.0.3, pluggy-1.6.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\User\OneDrive - University of Portsmouth\Documents\SETAP\Fixify1
collected 41 items                                                                                                                                  

tests/test_app.py::TestPostJob::test_all_valid_fields PASSED                                                                                  [  2%]
tests/test_app.py::TestPostJob::test_budget_currency PASSED                                                                                   [  4%]
tests/test_app.py::TestPostJob::test_budget_large PASSED                                                                                      [  7%]
tests/test_app.py::TestPostJob::test_budget_missing PASSED                                                                                    [  9%]
tests/test_app.py::TestPostJob::test_budget_negative PASSED                                                                                   [ 12%]
tests/test_app.py::TestPostJob::test_budget_non_numeric PASSED                                                                                [ 14%]
tests/test_app.py::TestPostJob::test_budget_valid_float PASSED                                                                                [ 17%]
tests/test_app.py::TestPostJob::test_budget_valid_integer PASSED                                                                              [ 19%]
tests/test_app.py::TestPostJob::test_budget_zero PASSED                                                                                       [ 21%]
tests/test_app.py::TestPostJob::test_category_case_mismatch PASSED                                                                            [ 24%]
tests/test_app.py::TestPostJob::test_category_invalid PASSED                                                                                  [ 26%]
tests/test_app.py::TestPostJob::test_category_missing PASSED                                                                                  [ 29%]
tests/test_app.py::TestPostJob::test_category_spaces PASSED                                                                                   [ 31%]
tests/test_app.py::TestPostJob::test_category_valid PASSED                                                                                    [ 34%]
tests/test_app.py::TestPostJob::test_contractor_role_blocked PASSED                                                                           [ 36%]
tests/test_app.py::TestPostJob::test_description_empty PASSED                                                                                 [ 39%]
tests/test_app.py::TestPostJob::test_description_missing PASSED                                                                               [ 41%]
tests/test_app.py::TestPostJob::test_description_multiline PASSED                                                                             [ 43%]
tests/test_app.py::TestPostJob::test_description_valid PASSED                                                                                 [ 46%]
tests/test_app.py::TestPostJob::test_description_very_long PASSED                                                                             [ 48%]
tests/test_app.py::TestPostJob::test_description_whitespace PASSED                                                                            [ 51%]
tests/test_app.py::TestPostJob::test_homeowner_role_allowed PASSED                                                                            [ 53%]
tests/test_app.py::TestPostJob::test_location_missing PASSED                                                                                  [ 56%]
tests/test_app.py::TestPostJob::test_location_valid PASSED                                                                                    [ 58%]
tests/test_app.py::TestPostJob::test_location_very_long PASSED                                                                                [ 60%]
tests/test_app.py::TestPostJob::test_location_whitespace PASSED                                                                               [ 63%]
tests/test_app.py::TestPostJob::test_negotiable_false PASSED                                                                                  [ 65%]
tests/test_app.py::TestPostJob::test_negotiable_invalid PASSED                                                                                [ 68%]
tests/test_app.py::TestPostJob::test_negotiable_true PASSED                                                                                   [ 70%]
tests/test_app.py::TestPostJob::test_no_role_in_session PASSED                                                                                [ 73%]
tests/test_app.py::TestPostJob::test_one_required_field_missing PASSED                                                                        [ 75%]
tests/test_app.py::TestPostJob::test_title_empty PASSED                                                                                       [ 78%]
tests/test_app.py::TestPostJob::test_title_missing PASSED                                                                                     [ 80%]
tests/test_app.py::TestPostJob::test_title_special_characters PASSED                                                                          [ 82%]
tests/test_app.py::TestPostJob::test_title_valid_short PASSED                                                                                 [ 85%]
tests/test_app.py::TestPostJob::test_title_very_long PASSED                                                                                   [ 87%]
tests/test_app.py::TestPostJob::test_title_whitespace PASSED                                                                                  [ 90%]
tests/test_app.py::TestPostJob::test_urgency_case_mismatch PASSED                                                                             [ 92%]
tests/test_app.py::TestPostJob::test_urgency_invalid PASSED                                                                                   [ 95%]
tests/test_app.py::TestPostJob::test_urgency_missing PASSED                                                                                   [ 97%]
tests/test_app.py::TestPostJob::test_urgency_valid PASSED                                                                                     [100%]

-------- generated xml file: C:\Users\User\OneDrive - University of Portsmouth\Documents\SETAP\Fixify1\test-reports\posting_test_report.xml -------- 
==================================================== 41 passed in 5.22s ================================================================
```
# Summary

Total: 41/41 Passed
Passed: 41  Failed: 0   Errors: 0   Skipped: 0
Duration: 5.22s

posting_test_report.xml Generated

# Previous Tests Summary

Test run 1:

Our first test run gave back 41/41 passed test outputs.

This actually showed us a lot of weaknesses in the restrictive parameters and error handling in `...templates/post.html` and the post() route in `main.py`. We then proceeded to alter and add these features.

Test run 2:

Our second test run gave back 37/41 passed test outputs and 4/41 failed test ouputs.

Failed tests:

`test_urgency_case_mismatch`
`test_urgency_invalid`
`test_urgency_missing`
`test_urgency_valid`

Showing us that our urgency tests were not functioning correctly. After resolving the issue with the urgency testing we did our final test, shown at the top of the page.


# Testbed
The automated posting tests use a Flask testbed instead of manually interacting with the website. The testbed creates the application using `create_app(testing=True)`, uses the Flask test client to send requests to the `/post` route, creates and drops an in-memory SQLite database before and after each test, and clears `all_jobs` so every posting test begins from a clean state.


# What Was Tested

- Submitting jobs through `/post`, ncluding homeowner-only access checks, missing role sessions, contractor role restrictions, valid job submissions, and successful page access for homeowners.
- Job title validation through `/post`, including missing titles, empty titles, whitespace-only titles, valid short titles, very long titles, and titles containing special characters.
- Job description validation through `/post`, including missing descriptions, empty descriptions, whitespace-only descriptions, valid descriptions, multiline descriptions, and overly long descriptions.
- Category validation through `/post`, including valid categories, missing categories, invalid categories, incorrect case sensitivity, and categories containing extra spaces.
- Urgency validation through `/post`, including valid urgency values, missing urgency selections, invalid urgency values, and incorrect case sensitivity handling.
- Location validation through `/post`, including valid locations, missing locations, whitespace-only locations, and overly long location values.
- Budget validation through `/post`, including missing budgets, valid integer budgets, valid float budgets, non-numeric inputs, currency-formatted inputs, zero values, negative values, and very large budget amounts.
- Negotiable budget validation through `/post`, including valid true and false values and invalid negotiable inputs.
- Database persistence and saved job record validation through `/post`, including successful storage of valid job submissions and rejection of invalid submissions without
creating database records.
- System-wide posting validation through `/post`, including complete valid job submissions, required-field handling checks, and overall verification of posting functionality with all 41 automated posting tests passing successfully.

# Bidding System Automated Test Report

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


## Files Changed Because Of Testing

- `templates/layout.html` was updated so Flask flash messages are visible to the user after route redirects.
- `main.py` now renders `chat.html` for the accepted-bid quick chat route.
- `templates/chat.html` was completed so it displays accepted-bid messages and lets both sides send chat messages.
- `test-reports/bidding_test_report.xml` was generated automatically by Pytest using the `--junitxml` option.
- `test-reports/bidding_test_report.md` was written as a readable summary of the automated test run and the issues found.

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

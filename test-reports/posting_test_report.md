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

Our second test run gave back 37/41 passed test outputs and 3/41 failed test ouputs.

Failed tests:

`test_urgency_case_mismatch`
`test_urgency_invalid`
`test_urgency_missing`
`test_urgency_valid`

Showing us that our urgency tests were not functioning correctly. After resolving the issue with the urgency testing we did our final test, shown at the top of the page.


# Running the test suite

The tests use pytest so:

`python3 -m pip install pytest`

`python -m pytest`

In order to properly test PhotoScript, the test suite must obviously interact with Photos using AppleScript.  This requires some user input so the test suite **must** be run with user interaction; it cannot be run in "headless" manner.

When the test suite is run, pytest will first copy a test library to the user's ~/Pictures folder (overwriting the existing test library if it is present) then tell Photos to open this library.  This may require user interaction to confirm opening the library.

Some of the tests will pause an wait for the user to do something.  These tests will prompt the user and tell them what to do (e.g. select photos in Photos).


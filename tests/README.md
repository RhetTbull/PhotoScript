# Running the test suite

The tests use pytest so:

`python3 -m pip install pytest`

`python3 -m pytest`

In order to properly test PhotoScript, the test suite must obviously interact with Photos using AppleScript.  This requires some user input so the test suite **must** be run with user interaction; it cannot be run in "headless" manner.

When the test suite is run, pytest will first copy a test library to the user's ~/Pictures folder (overwriting the existing test library if it is present) then tell Photos to open this library.  This may require user interaction to confirm opening the library.

If your Pictures folder is not in ~/Pictures, you can set the environment variable `PHOTOSCRIPT_PICTURES_FOLDER` to point to the path to your Pictures folder and the tests will use this path instead of ~/Pictures.

Some of the tests will pause an wait for the user to do something.  These tests will prompt the user and tell them what to do (e.g. select photos in Photos).

You may need to run the test suite more than once to get all tests to pass due to the way AppleScript interacts with Photos during the test.  For example, if the test library was not the last library opened in Photos, Photos may cause an error when the test suite tried to switch to the test library.
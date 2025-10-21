"""Module to load and run AppleScript scripts for photo management."""

import pathlib
import subprocess

from applescript import AppleScript, ScriptError

SCRIPT_PATH = pathlib.Path(__file__).parent


def kill_photos_app():
    """ Run 'killall Photos'. Used to reset unstable / timed out connection to Photos.

    Returns:
        True if Photos app was terminated
        False if Photos app was not running or could not be terminated.
    """
    try:
        # Run 'killall Photos' and capture output
        result = subprocess.run(
            ["killall", "Photos"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        # Exit code 0 means success (process found and killed)
        if result.returncode == 0:
            return True
        # Exit code 1 usually means "no matching process"
        if "No matching processes" in result.stderr:
            return False

        # Unknown issue/error
        return False

    # Command killall not found
    except FileNotFoundError:
        return False


def load_applescript(script_name):
    """Load an AppleScript from the scripts directory."""
    script_path = pathlib.Path(SCRIPT_PATH) / f"{script_name}.applescript"
    if not script_path.is_file():
        raise ValueError(f"{script_path} is not a valid script")
    script_file = open(script_path, "r")
    script = script_file.read()
    script_file.close()
    return AppleScript(script)

SCRIPT_OBJ = load_applescript("photoscript")

def run_script(name, *args):
    """Run a handler in the loaded AppleScript."""
    try:
        return SCRIPT_OBJ.call(name, *args)
    except ScriptError as e:
        if "timed out" in str(e):
            # Best-effort reset of Photos; ignore the boolean result
            kill_photos_app():
            # Retry once; let any exception from this call bubble up
            return SCRIPT_OBJ.call(name, *args)
        raise

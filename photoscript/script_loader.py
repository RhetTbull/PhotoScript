"""Module to load and run AppleScript scripts for photo management."""

import pathlib
import subprocess
import logging
from tenacity import RetryCallState, retry, stop_after_attempt, wait_fixed, retry_if_exception

from applescript import AppleScript
from .exceptions import AppleScriptError


logger = logging.getLogger(__name__)


class RunScriptError(Exception):
    pass


# Global configuration — PhotosLibrary can change these
RUNSCRIPT_CONFIG = {
    "retry_enabled": True,
    "retries": 2,
    "wait_seconds": 5,
}


def configure_run_script(retry_enabled=None, retries=None, wait_seconds=None):
    """Change global retry behavior for run_script."""
    if retry_enabled is not None:
        RUNSCRIPT_CONFIG["retry_enabled"] = retry_enabled
    if retries is not None:
        RUNSCRIPT_CONFIG["retries"] = retries
    if wait_seconds is not None:
        RUNSCRIPT_CONFIG["wait_seconds"] = wait_seconds


# Check for errot "AppleScript timed out" to allow retry
def is_applescript_timed_out(exception) -> bool:
    """Check if exception is an AppleScript timed out"""
    return "timed out" in str(exception)


def kill_photos_app(retry_state: RetryCallState) -> None:
    """Run 'killall Photos'. Used to reset unstable / timed out connection to Photos.

    Returns:
        True if Photos app was terminated
        False if Photos app was not running or could not be terminated.
    """
    try:
        logger.warning(
            "⚠️  run_script: AppleScript timed out: retrying killall + run_script"
        )
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
            logger.warning("✅  Photos app was terminated successfully.")
            return None
        # Exit code 1 usually means "no matching process"
        if "No matching processes" in result.stderr:
            logger.warning("ℹ️  Photos app was not running.")
            return None

        # Unknown issue/error
        logger.warning("⚠️  Unknown issue:\n %s", result.stderr)
        return None

    # Command killall not found
    except FileNotFoundError:
        logger.warning("❌  'killall' command not found. Are you running on macOS?")
        return None


SCRIPT_PATH = pathlib.Path(__file__).parent


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


def _run_script_once(name, *args):
    try:
        return SCRIPT_OBJ.call(name, *args)
    except Exception as e:
        raise AppleScriptError(f"run_script '{name}' failed: {e}") from e


def _retry_run_script():
    """Build a Tenacity-wrapped version of _run_script_once with current config."""

    @retry(
        stop=stop_after_attempt(RUNSCRIPT_CONFIG["retries"]),
        wait=wait_fixed(RUNSCRIPT_CONFIG["wait_seconds"]),
        retry=retry_if_exception(is_applescript_timed_out),
        before_sleep=kill_photos_app,
        reraise=True,
    )
    def wrapped(name, *args):
        return _run_script_once(name, *args)

    return wrapped


def run_script(name, *args):
    """Public API for running AppleScript with optional retries."""
    if RUNSCRIPT_CONFIG["retry_enabled"]:
        return _retry_run_script()(name, *args)
    return _run_script_once(name, *args)

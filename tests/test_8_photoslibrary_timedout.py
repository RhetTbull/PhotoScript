import pytest
from applescript import ScriptError

import photoscript
import photoscript.script_loader as script_loader
from photoscript.exceptions import AppleScriptError


def test_run_script_retries_on_applescript_timed_out(monkeypatch):
    """ Test that run_script retries when an AppleScript ScriptError with a timed-out message is raised."""
    # make retries fast for test
    photoscript.script_loader.configure_run_script(retry_enabled=True, retries=5, wait_seconds=1)

    # Dummy SCRIPT_OBJ: first call raises the real-looking timed-out ScriptError, second call succeeds
    class DummyScriptObj:
        def __init__(self):
            self.calls = 0

        def call(self, name, *args):
            self.calls += 1
            photoscript.script_loader.logger.warning("(fake) script_loader.run_script: call with attempts=[%s]", self.calls)

            if self.calls <= 3:
                raise AppleScriptError(
                    "Photos got an error: AppleEvent timed out. (-1712) app='Photos' range=24079-24104"
                )
            return "ok-result"

    monkeypatch.setattr(script_loader, "SCRIPT_OBJ", DummyScriptObj())

    # Capture into called list that kill_photos_app was invoked by Tenacity before retrying
    called = []
    def fake_kill_photos(retry_state):
        photoscript.script_loader.logger.warning("✅  (fake)Photos app was terminated successfully.")
        called.append(retry_state)
    monkeypatch.setattr(script_loader, "kill_photos_app", fake_kill_photos)

    result = script_loader.run_script("dummy_AppleScript_function")
    assert result == "ok-result"
    assert len(called) == 3
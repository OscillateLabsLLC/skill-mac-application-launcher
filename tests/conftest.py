"""Test isolation for a skill that writes real settings and drives real apps.

Two things leak out of these tests without this file:

1. OVOS persists skill settings to ~/.config/mycroft/skills/<skill_id>/. A test
   that sets `disable_window_manager` writes it to disk, and EVERY later run
   loads it back — including runs on a developer's machine weeks later. That
   silently inverts the branch under test, so tests fail with no code change.

2. `switch_to_app` shells out to `osascript ... tell application "X" activate`,
   which really opens the app. Unmocked, running the suite opens Safari and
   trips macOS automation prompts.

Both are neutralized here for every test.
"""

import os
import tempfile

import pytest


@pytest.fixture(autouse=True)
def isolated_skill_settings(monkeypatch):
    """Point OVOS at a throwaway config dir so settings never persist."""
    with tempfile.TemporaryDirectory() as tmp:
        monkeypatch.setenv("XDG_CONFIG_HOME", tmp)
        monkeypatch.setenv("XDG_DATA_HOME", os.path.join(tmp, "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", os.path.join(tmp, "cache"))
        yield


@pytest.fixture(autouse=True)
def no_real_app_launches(monkeypatch):
    """Fail loudly instead of driving the desktop.

    Any test that reaches osascript or a real process spawn without mocking it
    is a bug in the test, not a reason to open Safari on someone's laptop.
    """

    def _blocked(*args, **kwargs):
        raise AssertionError(
            "This test reached a real subprocess call. Mock the controller "
            "method under test (see tests/conftest.py)."
        )

    monkeypatch.setattr("subprocess.run", _blocked)
    monkeypatch.setattr("subprocess.Popen", _blocked)

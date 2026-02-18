#!/usr/bin/env python3
"""
Test suite for MacApplicationLauncherSkill

Tests the main skill class functionality including initialization,
intent matching, application management, and fallback handling.
"""

import unittest
from unittest.mock import Mock, patch

from ovos_bus_client.message import Message
from ovos_utils.fakebus import FakeBus

from skill_mac_application_launcher import MacApplicationLauncherSkill


class TestMacApplicationLauncherSkill(unittest.TestCase):
    """Test cases for MacApplicationLauncherSkill."""

    def setUp(self):
        """Set up test fixtures."""
        self.bus = FakeBus()
        self.skill = MacApplicationLauncherSkill(skill_id="test.skill", bus=self.bus)

    def tearDown(self):
        """Clear LRU cache between tests."""
        self.skill.match_app.cache_clear()

    def test_initialization_default_settings(self):
        """Test skill initialization with default settings."""
        self.skill.initialize()

        self.assertIn("aliases", self.skill.settings)
        self.assertIn("Calculator", self.skill.settings["aliases"])
        self.assertIn("Safari", self.skill.settings["aliases"])

        self.assertIn("user_commands", self.skill.settings)
        self.assertEqual(self.skill.settings["user_commands"], {})

    def test_initialization_with_existing_settings(self):
        """Test skill initialization preserves existing settings."""
        self.skill.settings["aliases"] = {"TestApp": ["test"]}
        self.skill.settings["user_commands"] = {"Custom": "/path/to/app"}

        self.skill.initialize()

        self.assertEqual(self.skill.settings["aliases"], {"TestApp": ["test"]})
        self.assertEqual(self.skill.settings["user_commands"], {"Custom": "/path/to/app"})

    def test_macos_controller_initialization(self):
        """Test that MacOSApplicationController is properly initialized."""
        self.skill.initialize()

        self.assertIsNotNone(self.skill.macos_controller)
        self.assertIn("extra_langs", self.skill.macos_controller.settings)

    def test_refresh_application_cache_success(self):
        """Test successful application cache refresh."""
        self.skill.initialize()

        with patch.object(self.skill.macos_controller, 'refresh_app_cache'):
            with patch.object(self.skill.macos_controller, 'is_cache_valid', return_value=True):
                result = self.skill.refresh_application_cache()
                self.assertTrue(result)

    def test_refresh_application_cache_failure(self):
        """Test application cache refresh failure."""
        self.skill.initialize()

        with patch.object(self.skill.macos_controller, 'refresh_app_cache', side_effect=Exception("Cache error")):
            result = self.skill.refresh_application_cache()
            self.assertFalse(result)

    def test_can_answer_with_valid_app(self):
        """Test can_answer returns True for valid application utterances."""
        self.skill.initialize()

        message = Message("test", {"utterances": ["open calculator"]})

        with patch.object(self.skill, 'match_app', return_value={"entities": {"application": "Calculator"}}):
            result = self.skill.can_answer(message)
            self.assertTrue(result)

    def test_can_answer_with_no_match(self):
        """Test can_answer returns False when no app matches."""
        self.skill.initialize()

        message = Message("test", {"utterances": ["random utterance"]})

        with patch.object(self.skill, 'match_app', return_value=None):
            result = self.skill.can_answer(message)
            self.assertFalse(result)

    def test_can_answer_with_no_application_entity(self):
        """Test can_answer returns False when match has no application entity."""
        self.skill.initialize()

        message = Message("test", {"utterances": ["some utterance"]})

        with patch.object(self.skill, 'match_app', return_value={"entities": {}}):
            result = self.skill.can_answer(message)
            self.assertFalse(result)

    def test_launch_app_success(self):
        """Test successful application launch."""
        self.skill.initialize()

        with patch.object(self.skill.macos_controller, 'launch_app', return_value=True):
            with patch.object(self.skill, 'acknowledge'):
                result = self.skill.launch_app("Safari")
                self.assertTrue(result)
                self.skill.acknowledge.assert_called_once()

    def test_launch_app_failure(self):
        """Test failed application launch."""
        self.skill.initialize()

        with patch.object(self.skill.macos_controller, 'launch_app', return_value=False):
            result = self.skill.launch_app("NonexistentApp")
            self.assertFalse(result)

    def test_close_app_success(self):
        """Test successful application closure."""
        self.skill.initialize()

        with patch.object(self.skill.macos_controller, 'close_app', return_value=True):
            with patch.object(self.skill, 'acknowledge'):
                result = self.skill.close_app("Safari")
                self.assertTrue(result)
                self.skill.acknowledge.assert_called_once()

    def test_close_app_failure(self):
        """Test failed application closure."""
        self.skill.initialize()

        with patch.object(self.skill.macos_controller, 'close_app', return_value=False):
            result = self.skill.close_app("NonexistentApp")
            self.assertFalse(result)

    # --- Delegation tests (parametrized) ---

    def test_controller_delegation_methods(self):
        """Test that legacy wrapper methods correctly delegate to the controller."""
        self.skill.initialize()

        # is_running
        with patch.object(self.skill.macos_controller, 'is_running', return_value=True) as m:
            self.assertTrue(self.skill.is_running("Safari"))
            m.assert_called_once_with("Safari")

        # switch_to_app
        with patch.object(self.skill.macos_controller, 'switch_to_app', return_value=True) as m:
            self.assertTrue(self.skill.switch_to_app("Safari"))
            m.assert_called_once_with("Safari")

        # close_by_applescript
        with patch.object(self.skill.macos_controller, 'close_by_applescript', return_value=True) as m:
            self.assertTrue(self.skill.close_by_applescript("Safari"))
            m.assert_called_once_with("Safari")

        # close_by_process
        with patch.object(self.skill.macos_controller, 'close_by_process', return_value=True) as m:
            self.assertTrue(self.skill.close_by_process("Safari"))
            m.assert_called_once_with("Safari")

        # match_process
        expected = [Mock(), Mock()]
        with patch.object(self.skill.macos_controller, 'match_process', return_value=expected) as m:
            self.assertEqual(list(self.skill.match_process("Safari")), expected)
            m.assert_called_once_with("Safari")

    def test_controller_delegation_properties(self):
        """Test that alias properties delegate to the controller."""
        self.skill.initialize()
        self.assertEqual(self.skill.get_app_aliases(), self.skill.macos_controller.app_aliases)
        self.assertEqual(self.skill.applist, self.skill.macos_controller.app_aliases)


class TestHandleFallback(unittest.TestCase):
    """Test cases for the fallback handler — the primary skill entry point."""

    def setUp(self):
        self.bus = FakeBus()
        self.skill = MacApplicationLauncherSkill(skill_id="test.skill", bus=self.bus)
        self.skill.initialize()

    def tearDown(self):
        self.skill.match_app.cache_clear()

    def _msg(self, utterance):
        return Message("recognizer_loop:utterance", {"utterance": utterance})

    def test_fallback_returns_false_on_no_match(self):
        """No intent match → returns False (not handled)."""
        with patch.object(self.skill, 'match_app', return_value=None):
            self.assertFalse(self.skill.handle_fallback(self._msg("gibberish")))

    def test_fallback_returns_false_on_no_app_entity(self):
        """Intent matched but no application entity → returns False."""
        with patch.object(self.skill, 'match_app', return_value={"name": "launch", "entities": {}}):
            self.assertFalse(self.skill.handle_fallback(self._msg("open")))

    def test_fallback_launch_not_running(self):
        """Launch intent + app not running → launches and returns True."""
        match = {"name": "launch", "entities": {"application": "Safari"}}
        with patch.object(self.skill, 'match_app', return_value=match), \
             patch.object(self.skill.macos_controller, 'is_running', return_value=False), \
             patch.object(self.skill, 'launch_app', return_value=True) as mock_launch:
            self.assertTrue(self.skill.handle_fallback(self._msg("open safari")))
            mock_launch.assert_called_once_with("Safari")

    def test_fallback_launch_already_running_emits_async(self):
        """Launch intent + app already running → emits async_prompt event and returns True."""
        match = {"name": "launch", "entities": {"application": "Safari"}}
        # Mock bus.emit to capture the message without dispatching to registered handlers
        # (handle_async_prompt would block on ask_yesno)
        with patch.object(self.skill, 'match_app', return_value=match), \
             patch.object(self.skill.macos_controller, 'is_running', return_value=True), \
             patch.object(self.bus, 'emit') as mock_emit:
            result = self.skill.handle_fallback(self._msg("open safari"))
            self.assertTrue(result)
            # Verify async_prompt was emitted
            emitted_types = [c.args[0].msg_type for c in mock_emit.call_args_list if hasattr(c.args[0], 'msg_type')]
            self.assertTrue(
                any("async_prompt" in t for t in emitted_types),
                f"Expected async_prompt in emitted types, got: {emitted_types}",
            )

    def test_fallback_close_app(self):
        """Close intent → calls close_app and returns its result."""
        match = {"name": "close", "entities": {"application": "Safari"}}
        with patch.object(self.skill, 'match_app', return_value=match), \
             patch.object(self.skill, 'close_app', return_value=True) as mock_close:
            self.assertTrue(self.skill.handle_fallback(self._msg("close safari")))
            mock_close.assert_called_once_with("Safari")

    def test_fallback_close_app_failure(self):
        """Close intent but close fails → returns False."""
        match = {"name": "close", "entities": {"application": "Safari"}}
        with patch.object(self.skill, 'match_app', return_value=match), \
             patch.object(self.skill, 'close_app', return_value=False):
            self.assertFalse(self.skill.handle_fallback(self._msg("close safari")))

    def test_fallback_launch_failure(self):
        """Launch intent but launch fails → returns False."""
        match = {"name": "launch", "entities": {"application": "BadApp"}}
        with patch.object(self.skill, 'match_app', return_value=match), \
             patch.object(self.skill.macos_controller, 'is_running', return_value=False), \
             patch.object(self.skill, 'launch_app', return_value=False):
            self.assertFalse(self.skill.handle_fallback(self._msg("open badapp")))

    def test_fallback_unknown_intent_name(self):
        """Matched intent with unrecognized name → returns False."""
        match = {"name": "unknown_intent", "entities": {"application": "Safari"}}
        with patch.object(self.skill, 'match_app', return_value=match):
            self.assertFalse(self.skill.handle_fallback(self._msg("do something with safari")))


class TestHandleAsyncPrompt(unittest.TestCase):
    """Test cases for the async prompt handler (already-running dialog flow)."""

    def setUp(self):
        self.bus = FakeBus()
        self.skill = MacApplicationLauncherSkill(skill_id="test.skill", bus=self.bus)
        self.skill.initialize()

    def tearDown(self):
        self.skill.match_app.cache_clear()

    def _msg(self, app):
        return Message("test.skill.async_prompt", {"app": app})

    def test_switch_yes_success(self):
        """User confirms switch → switch_to_app called, acknowledge sent."""
        with patch.object(self.skill, 'speak_dialog') as mock_speak, \
             patch.object(self.skill, 'ask_yesno', return_value="yes"), \
             patch.object(self.skill.macos_controller, 'switch_to_app', return_value=True) as mock_switch, \
             patch.object(self.skill, 'acknowledge') as mock_ack:
            result = self.skill.handle_async_prompt(self._msg("Safari"))
            mock_speak.assert_called_once_with("already_running", {"application": "Safari"})
            mock_switch.assert_called_once_with("Safari")
            mock_ack.assert_called_once()
            self.assertTrue(result)

    def test_switch_yes_but_switch_fails(self):
        """User confirms switch but switch_to_app fails → returns True (still handled), no ack."""
        with patch.object(self.skill, 'speak_dialog'), \
             patch.object(self.skill, 'ask_yesno', return_value="yes"), \
             patch.object(self.skill.macos_controller, 'switch_to_app', return_value=False), \
             patch.object(self.skill, 'acknowledge') as mock_ack:
            result = self.skill.handle_async_prompt(self._msg("Safari"))
            mock_ack.assert_not_called()
            self.assertTrue(result)

    def test_switch_no_then_decline_launch(self):
        """User declines switch, then declines launch → no action taken."""
        with patch.object(self.skill, 'speak_dialog'), \
             patch.object(self.skill, 'ask_yesno', side_effect=["no", "no"]), \
             patch.object(self.skill, 'launch_app') as mock_launch:
            result = self.skill.handle_async_prompt(self._msg("Safari"))
            mock_launch.assert_not_called()
            self.assertTrue(result)

    def test_switch_no_then_confirm_launch(self):
        """User declines switch, doesn't decline launch → launch_app called."""
        # "no" for switch, then 5x None exhausts launch confirm loop, falls through to launch
        with patch.object(self.skill, 'speak_dialog'), \
             patch.object(self.skill, 'ask_yesno', side_effect=["no", None, None, None, None, None]), \
             patch.object(self.skill, 'launch_app') as mock_launch:
            self.skill.handle_async_prompt(self._msg("Safari"))
            mock_launch.assert_called_once_with("Safari")

    def test_unrecognized_switch_response_exhausts_retries_then_launches(self):
        """Unrecognized responses to switch prompt exhaust retries, then launch confirm loop runs."""
        # ask_yesno returns None 5 times for switch (exhausts loop), then None 5 times for launch
        # (exhausts loop), falls through to launch_app
        responses = [None] * 10
        with patch.object(self.skill, 'speak_dialog'), \
             patch.object(self.skill, 'ask_yesno', side_effect=responses), \
             patch.object(self.skill, 'launch_app') as mock_launch:
            self.skill.handle_async_prompt(self._msg("Safari"))
            mock_launch.assert_called_once_with("Safari")

    def test_window_manager_disabled_skips_switch(self):
        """With disable_window_manager=True, skips switch prompt, goes to launch."""
        self.skill.settings["disable_window_manager"] = True

        # switch is False (initial), so the launch confirm loop runs
        # User declines launch
        with patch.object(self.skill, 'speak_dialog'), \
             patch.object(self.skill, 'ask_yesno', return_value="no"), \
             patch.object(self.skill, 'launch_app') as mock_launch:
            result = self.skill.handle_async_prompt(self._msg("Safari"))
            mock_launch.assert_not_called()
            self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()

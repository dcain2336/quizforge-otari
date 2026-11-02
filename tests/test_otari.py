# test_otari.py - deterministic offline tests for the Otari gateway module.  # Module header: what this file is.
# Every test runs with no network and no key: stub mode is the default, so the suite is  # Design choice: the suite must pass keyless, like the app runs keyless.
# safe to run anywhere. Live gateway calls are never made by these tests.  # Design choice continued: no live calls in tests.
# Import the OS module so tests can clear Otari env vars for stub-mode cases.  # Library: os.
import os  # Make the os module available.
# Import the unittest module for the test framework.  # Library: unittest.
import unittest  # Make the unittest module available.
# Import the module under test from the project root.  # Library: otari (this project).
import otari  # The Otari gateway client lives in otari.py.
# Start the test case class for the Otari module.  # Class: TestOtari.
class TestOtari(unittest.TestCase):  # Define the test case by extending unittest's base class.
    # Start the setup hook that clears Otari env vars before every test.  # Method: setUp.
    def setUp(self):  # Define setUp, which runs before each test method.
        # Remember any pre-existing Otari env values so they can be restored after.  # Step: snapshot env.
        self._saved = {key: os.environ.pop(key) for key in ("OTARI_API_KEY", "OTARI_BASE_URL", "OTARI_MODEL_A", "OTARI_MODEL_B") if key in os.environ}  # Pop the four Otari vars, saving what existed.
    # Start the teardown hook that restores the env vars after every test.  # Method: tearDown.
    def tearDown(self):  # Define tearDown, which runs after each test method.
        # Restore exactly what setup removed, leaving the environment as found.  # Step: restore env.
        os.environ.update(self._saved)  # Put the saved values back.
    # Start the test that unconfigured mode reports stub honestly.  # Test: stub status.
    def test_status_reports_stub_when_unconfigured(self):  # Define the stub-status test.
        # Fetch the status snapshot with no env vars set.  # Step: status.
        result = otari.status()  # The snapshot under test.
        # Assert the snapshot says stub, not live, with stub model labels.  # Step: assertions.
        self.assertFalse(result["configured"])  # Unconfigured must report False.
        self.assertEqual(result["mode"], "stub")  # Mode must say stub out loud.
        self.assertIn("stub", result["model_a"])  # Model A must wear its stub label.
        self.assertIn("stub", result["model_b"])  # Model B must wear its stub label.
    # Start the test that a configured env reports live (without making any call).  # Test: live status.
    def test_status_reports_live_when_configured(self):  # Define the live-status test.
        # Set a key, URL, and model slugs in the environment for this test only.  # Step: configure env.
        os.environ["OTARI_API_KEY"] = "test-key-never-real"  # A fake key: status checks presence, never calls.
        os.environ["OTARI_BASE_URL"] = "https://example.invalid/v1"  # A reserved example URL: never fetched.
        os.environ["OTARI_MODEL_A"] = "example/model-a"  # A fake slug for display only.
        os.environ["OTARI_MODEL_B"] = "example/model-b"  # A fake slug for display only.
        # Fetch the status snapshot with the fake configuration in place.  # Step: status.
        result = otari.status()  # The snapshot under test.
        # Assert the snapshot says live and names the configured models.  # Step: assertions.
        self.assertTrue(result["configured"])  # Configured must report True.
        self.assertEqual(result["mode"], "live")  # Mode must say live.
        self.assertEqual(result["model_a"], "example/model-a")  # Model A must be the env slug.
        self.assertEqual(result["model_b"], "example/model-b")  # Model B must be the env slug.
    # Start the test that identical answers measure as agreement.  # Test: agreement agree.
    def test_measure_agreement_identical_is_agree(self):  # Define the agree test.
        # Measure two identical answers.  # Step: measure.
        verdict, _note = otari.measure_agreement("Apply pressure and call for help.", "Apply pressure and call for help.")  # Same words, same verdict expected.
        # Assert the verdict is agree.  # Step: assertion.
        self.assertEqual(verdict, "agree")  # Identical answers must agree.
    # Start the test that disjoint answers measure as difference.  # Test: agreement differ.
    def test_measure_agreement_disjoint_is_differ(self):  # Define the differ test.
        # Measure two answers with no meaningful words in common.  # Step: measure.
        verdict, _note = otari.measure_agreement("Apply direct pressure to stop bleeding.", "Photosynthesis converts sunlight into chemical energy in leaves.")  # Disjoint topics, disjoint words.
        # Assert the verdict is differ.  # Step: assertion.
        self.assertEqual(verdict, "differ")  # Disjoint answers must differ.
    # Start the test that empty answers cannot claim agreement.  # Test: agreement empty.
    def test_measure_agreement_empty_is_differ(self):  # Define the empty test.
        # Measure an empty answer against a real one.  # Step: measure.
        verdict, _note = otari.measure_agreement("", "Apply direct pressure to stop bleeding.")  # Empty carries no signal.
        # Assert the verdict is differ, not agree.  # Step: assertion.
        self.assertEqual(verdict, "differ")  # Empty input must never read as agreement.
    # Start the test that stub comparison returns a complete, labeled package.  # Test: stub compare.
    def test_compare_stub_returns_full_package(self):  # Define the stub-compare test.
        # Run a stub comparison on an ordinary question.  # Step: compare.
        result = otari.compare("What is the first step of first aid for a bleeding wound?")  # Any question must work in stub mode.
        # Assert the package shape: stub mode, both panels, verdict fields present.  # Step: assertions.
        self.assertEqual(result["mode"], "stub")  # Stub mode must be labeled stub.
        self.assertTrue(result["model_a"]["answer"])  # Model A's panel must not be empty.
        self.assertTrue(result["model_b"]["answer"])  # Model B's panel must not be empty.
        self.assertNotEqual(result["model_a"]["answer"], result["model_b"]["answer"])  # Stub panels must visibly differ, or the view shows nothing.
        self.assertIn(result["agreement"], ("agree", "partial", "differ"))  # The verdict must be one of the three known values.
        self.assertTrue(result["verdict"])  # The plain-language verdict must not be empty.
        self.assertTrue(result["agreement_note"])  # The evidence note must not be empty.
    # Start the test that an empty question is rejected, not compared.  # Test: empty question.
    def test_compare_empty_question_raises(self):  # Define the empty-question test.
        # Assert that a blank question raises ValueError.  # Step: assertion.
        with self.assertRaises(ValueError):  # Blank input must fail loudly.
            otari.compare("   ")  # Whitespace-only is empty for this purpose.
    # Start the test that a live chat call without configuration fails readably.  # Test: chat guard.
    def test_chat_without_config_raises(self):  # Define the chat-guard test.
        # Assert that chat without key/URL raises OtariError, not a network error.  # Step: assertion.
        with self.assertRaises(otari.OtariError):  # Unconfigured chat must fail with the labeled error.
            otari.chat("Hello?", "example/model-a")  # No configuration exists in this test.
# Run the tests when this file is executed directly.  # Entry-point guard.
if __name__ == "__main__":  # Check how the file was started.
    unittest.main()  # Run the suite.

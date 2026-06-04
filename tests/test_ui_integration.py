import os
import unittest
import tempfile
import time
from unittest.mock import patch
from src.ui import AnkiAlignerApp

class TestUIIntegration(unittest.TestCase):
    def setUp(self):
        self.test_workspace = tempfile.TemporaryDirectory()
        self.inputs_path = os.path.join(self.test_workspace.name, "inputs")
        os.makedirs(self.inputs_path)

        self.mock_pdf = os.path.join(self.inputs_path, "RUN UP - Phrasal Verbs.txt")
        self.mock_mp3 = os.path.join(self.inputs_path, "1 - Run up sequence.mp3")

        with open(self.mock_pdf, 'w', encoding='utf-8') as f:
            f.write("She ran up a massive bill. Ela acumulou uma conta enorme.")
        with open(self.mock_mp3, 'wb') as f:
            f.write(b"mock audio data stream")

        self.app = AnkiAlignerApp()

    def tearDown(self):
        self.app.destroy()
        self.test_workspace.cleanup()

    def test_end_to_end_pipeline_execution_from_ui(self):
        expected_txt_output = os.path.join(self.test_workspace.name, "RUN UP.txt")
        
        self.app.selected_path.set(os.path.abspath(self.inputs_path))
        self.app.profile_name.set("TestProfile")
        
        with patch('src.ui.filedialog.asksaveasfilename', return_value=expected_txt_output):
            self.app._trigger_pipeline_execution()
            
            timeout = 5
            start_time = time.time()
            while self.app.execute_btn.cget("state") == "disabled":
                if time.time() - start_time > timeout:
                    self.fail("E2E Test Deadlock: The background processing worker thread timed out.")
                self.app.update()
                time.sleep(0.05)

        console_output = self.app.console_box.get("1.0", "end")
        banner_text = self.app.status_banner.cget("text")
        banner_color = self.app.status_banner.cget("fg_color")
        
        self.assertIn("SUCCESS", banner_text)
        self.assertIn("NEXT STEP", banner_text)
        self.assertEqual(banner_color, "#10b981")
        
        self.assertIn("[Saved] Anki import file compiled successfully", console_output)
        self.assertTrue(os.path.exists(expected_txt_output))

if __name__ == "__main__":
    unittest.main()
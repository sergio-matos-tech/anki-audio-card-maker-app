import os
import unittest
import tempfile
import time
from unittest.mock import patch  # <--- IMPORTAÇÃO ESSENCIAL PARA MOCKING
from src.ui import AnkiAlignerApp

class TestUIIntegration(unittest.TestCase):
    """End-to-End Functional Test Suite to verify UI-to-Backend integration."""

    def setUp(self):
        # Establish an isolated temporary file system workspace
        self.test_workspace = tempfile.TemporaryDirectory()
        self.inputs_path = os.path.join(self.test_workspace.name, "inputs")
        os.makedirs(self.inputs_path)

        # Generate fake functional assets matching our pattern requirements
        self.mock_pdf = os.path.join(self.inputs_path, "RUN UP - Phrasal Verbs.txt")
        self.mock_mp3 = os.path.join(self.inputs_path, "1 - Run up sequence.mp3")

        with open(self.mock_pdf, 'w', encoding='utf-8') as f:
            f.write("She ran up a massive bill. Ela acumulou uma conta enorme.")
        with open(self.mock_mp3, 'wb') as f:
            f.write(b"mock audio data stream")

        # Programmatically instantiate the desktop interface app instance
        self.app = AnkiAlignerApp()

    def tearDown(self):
        # Destroy the interface widget tree and wipe the virtual environment workspace
        self.app.destroy()
        self.test_workspace.cleanup()

    def test_end_to_end_pipeline_execution_from_ui(self):
        """Simulates a real user interaction flow and verifies text area updates."""
        
        expected_txt_output = os.path.join(self.test_workspace.name, "RUN UP.txt")
        
        # 1. Simulate the folder selection phase
        self.app.selected_path.set(os.path.abspath(self.inputs_path))
        self.app.profile_name.set("TestProfile")
        
        # === AQUI ACONTECE A MÁGICA DO MOCK: Intercepta a janela nativa de salvamento ===
        # Dizemos para o Python: "Quando a UI chamar o asksaveasfilename, finja que o usuário escolheu o expected_txt_output"
        with patch('src.ui.filedialog.asksaveasfilename', return_value=expected_txt_output):
            # 2. Simulate the user clicking the 'GENERATE & SYNC ASSETS' button
            self.app._trigger_pipeline_execution()
        
        # 3. Pump the GUI event loop manually to allow the background thread to run
        timeout = 5
        start_time = time.time()
        
        while self.app.execute_btn.cget("state") == "disabled":
            if time.time() - start_time > timeout:
                self.fail("E2E Test Deadlock: The background processing worker thread timed out.")
            
            self.app.update() # Refreshes the Tkinter event loop matrix
            time.sleep(0.05)

        # 4. Extract the final text rendered inside the read-only visual console text box
        console_output = self.app.console_box.get("1.0", "end")

        # 5. Assertions: Validate that the full system cooperated properly
        self.assertIn("[UI] Spawning background worker thread...", console_output)
        self.assertIn("[Success] Generated mapping file", console_output)
        self.assertIn("[UI] Execution Complete.", console_output)
        
        # Verify that the generated text card file actually exists where the mock specified
        self.assertTrue(os.path.exists(expected_txt_output))


if __name__ == "__main__":
    unittest.main()
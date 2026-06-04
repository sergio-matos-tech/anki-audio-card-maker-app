import os
import unittest
import tempfile
from src.parser import execute_pipeline

class TestAnkiPipeline(unittest.TestCase):
    """Integration test suite to verify the stability of the decoupled parsing engine."""

    def setUp(self):
        # Create a dynamic temporary directory for isolated file manipulations
        self.test_dir = tempfile.TemporaryDirectory()
        self.inputs_path = os.path.join(self.test_dir.name, "inputs")
        os.makedirs(self.inputs_path)
        
        # In-memory log capture buffer to inspect emitted engine messages
        self.logs = []
        self.mock_logger = lambda message: self.logs.append(message)

    def tearDown(self):
        # Cleanly wipe the virtual workspace after execution
        self.test_dir.cleanup()

    def test_pipeline_fails_on_missing_directory(self):
        """Ensures the pipeline exits gracefully with False if the directory does not exist."""
        bad_path = os.path.join(self.inputs_path, "ghost_folder")
        result = execute_pipeline(inputs_dir=bad_path, anki_profile="User 1", log_callback=self.mock_logger)
        
        self.assertFalse(result)
        self.assertTrue(any("[Error]" in log for log in self.logs))

    def test_pipeline_fails_on_empty_directory(self):
        """Ensures the pipeline flags empty directories with explicit error messaging."""
        result = execute_pipeline(inputs_dir=self.inputs_path, anki_profile="User 1", log_callback=self.mock_logger)
        
        self.assertFalse(result)
        self.assertTrue(any("No valid .pdf or .txt source documents" in log for log in self.logs))

    def test_pipeline_executes_successfully_with_valid_mock_files(self):
        """Validates successful ingestion, parsing sequence, and mapping execution."""
        # Setup a valid filename matching our split structural requirements (PREFIX - Details)
        mock_doc_path = os.path.join(self.inputs_path, "TEST PV - Phrasal Verbs.txt")
        mock_audio_path = os.path.join(self.inputs_path, "1 - Test audio.mp3")
        
        # Populate dummy data
        with open(mock_doc_path, 'w', encoding='utf-8') as f:
            f.write("This is an English test statement. Esta é uma frase de teste em português.")
            
        with open(mock_audio_path, 'wb') as f:
            f.write(b"dummy audio binary data data")

        # Run pipeline targeting our isolated sandbox
        # Note: AnkiMediaSyncer will log a safe [Warning] if Anki isn't running or configured on this environment
        result = execute_pipeline(inputs_dir=self.inputs_path, anki_profile="User 1", log_callback=self.mock_logger)
        
        # Verify the pipeline engine successfully compiled the matching pairs
        self.assertTrue(result)
        
        # Verify that a custom mapped mapping export file was created in the parent folder
        expected_output_txt = os.path.join(self.test_dir.name, "TEST PV.txt")
        self.assertTrue(os.path.exists(expected_output_txt))


if __name__ == "__main__":
    unittest.main()
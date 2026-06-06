import os
import random
import unittest
import tempfile
from unittest.mock import patch
from src.parser import AnkiMediaSyncer, execute_pipeline

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


    def test_sync_audio_assets_overwrites_existing_media(self):
        source_dir = os.path.join(self.inputs_path, "inputs")
        os.makedirs(source_dir, exist_ok=True)

        filename = "1 - Test audio.mp3"
        source_path = os.path.join(source_dir, filename)
        with open(source_path, 'wb') as f:
            f.write(b"new dummy audio data")

        with tempfile.TemporaryDirectory() as media_dir:
            target_path = os.path.join(media_dir, filename)
            with open(target_path, 'wb') as f:
                f.write(b"old audio data")

            syncer = AnkiMediaSyncer(log_callback=self.mock_logger)
            with patch.object(AnkiMediaSyncer, "resolve_media_dir", return_value=media_dir):
                result = syncer.sync_audio_assets(source_dir=source_dir, file_list=[filename])

            self.assertTrue(result)
            with open(target_path, 'rb') as f:
                self.assertEqual(f.read(), b"new dummy audio data")

    def test_pipeline_logs_explicit_success_message(self):
        mock_doc_path = os.path.join(self.inputs_path, "TEST PV - Phrasal Verbs.txt")
        mock_audio_path = os.path.join(self.inputs_path, "1 - Test audio.mp3")
        with open(mock_doc_path, 'w', encoding='utf-8') as f:
            f.write("This is an English test statement. Esta é uma frase de teste em português.")
        with open(mock_audio_path, 'wb') as f:
            f.write(b"dummy audio binary data data")

        result = execute_pipeline(inputs_dir=self.inputs_path, anki_profile="User 1", log_callback=self.mock_logger)
        self.assertTrue(result)
        self.assertTrue(any("[Done] Created 1 cards" in log for log in self.logs))

    def test_expression_target_highlights_shorter_core_phrase(self):
        mock_doc_path = os.path.join(self.inputs_path, "Keep An Eye Out For.txt")
        mock_audio_path = os.path.join(self.inputs_path, "1 - Test audio.mp3")
        with open(mock_doc_path, 'w', encoding='utf-8') as f:
            f.write(
                "Keep an eye out for spyware programs that install themselves on your computer.\n"
                "Fique atento a programas espiões que instalam a si mesmos em seu computador.\n"
                "You and your friends keep an eye out — if there's any trouble we'll make a break for it.\n"
                "Vocês e seus amigos fiquem atentos — se houver qualquer problema nós fugiremos.\n"
            )
        with open(mock_audio_path, 'wb') as f:
            f.write(b"dummy audio")
        with open(os.path.join(self.inputs_path, "2 - Test audio.mp3"), 'wb') as f:
            f.write(b"dummy audio 2")

        result = execute_pipeline(inputs_dir=self.inputs_path, anki_profile="User 1", log_callback=self.mock_logger)
        self.assertTrue(result)

        output_path = os.path.join(self.test_dir.name, "Keep An Eye Out For.txt")
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('keep an eye out for', content.lower())
        self.assertNotIn('<u><b>', content)
        self.assertNotIn('</b></u>', content)

    def test_run_errand_singular_forms_are_highlighted(self):
        mock_doc_path = os.path.join(self.inputs_path, "Run Errands.txt")
        mock_audio_path = os.path.join(self.inputs_path, "1 - Test audio.mp3")
        with open(mock_doc_path, 'w', encoding='utf-8') as f:
            f.write(
                "I'm just stepping out to run an errand. I'll be back soon.\n"
                "Eu vou dar uma saidinha para resolver uma coisa. Volto logo.\n"
            )
        with open(mock_audio_path, 'wb') as f:
            f.write(b"dummy audio")

        result = execute_pipeline(inputs_dir=self.inputs_path, anki_profile="User 1", log_callback=self.mock_logger)
        self.assertTrue(result)

        output_path = os.path.join(self.test_dir.name, "Run Errands.txt")
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('run an errand', content.lower())
        self.assertNotIn('<u><b>', content)
        self.assertNotIn('</b></u>', content)

    def test_random_large_expression_and_phrasal_verb_highlighting_with_audio_mapping(self):
        random.seed(42)
        targets = [
            "Look Up To",
            "Keep On",
            "Turn Around",
            "Put Through",
            "Work Out",
            "Drink Up",
            "Break Down",
            "Take Off",
            "Call Off",
            "Get Around To",
        ]

        card_count = len(targets)
        audio_files = []

        portuguese_variants = [
            "Eu vou fazer isso depois.",
            "Nós precisamos continuar com isso.",
            "Ela já se deu conta disso.",
            "Eles estão preocupados com a situação.",
            "Você pode resolver isso mais tarde.",
            "Ele acabou de falar sobre isso.",
            "Nós vamos encontrar uma solução.",
            "Ela não quer desistir agora.",
            "Nós já tratamos desse problema.",
            "Eles vão cuidar disso hoje.",
        ]

        for index, target in enumerate(targets, start=1):
            phrase_file = os.path.join(self.inputs_path, f"{target}.txt")
            verb_phrase = target.lower()
            sentence = (
                f"{random.choice(['I', 'We', 'They', 'She'])} {random.choice(['really', 'always', 'never', 'just'])} "
                f"{verb_phrase} {random.choice(['the problem', 'this issue', 'the situation', 'that decision'])} "
                f"before we leave."
            )
            translation = random.choice(portuguese_variants)
            with open(phrase_file, 'w', encoding='utf-8') as f:
                f.write(sentence + "\n")
                f.write(translation + "\n")
            audio_files.append(f"{index} - random audio.mp3")

        for audio_name in audio_files:
            with open(os.path.join(self.inputs_path, audio_name), 'wb') as f:
                f.write(b"audio payload for " + audio_name.encode('utf-8'))

        with tempfile.TemporaryDirectory() as media_dir:
            with patch.object(AnkiMediaSyncer, "resolve_media_dir", return_value=media_dir):
                result = execute_pipeline(inputs_dir=self.inputs_path, anki_profile="User 1", log_callback=self.mock_logger)

            self.assertTrue(result)
            self.assertTrue(any("Created " in log and "cards" in log for log in self.logs))

            tx_files = [f for f in os.listdir(self.test_dir.name) if f.lower().endswith('.txt')]
            self.assertEqual(len(tx_files), 1)
            output_path = os.path.join(self.test_dir.name, tx_files[0])
            self.assertTrue(os.path.exists(output_path))

            with open(output_path, 'r', encoding='utf-8') as f:
                output_lines = [line.strip() for line in f if line.strip()]

            self.assertEqual(len(output_lines), card_count)
            for idx, target in enumerate(targets, start=1):
                audio_name = f"{idx} - random audio.mp3"
                self.assertTrue(any(audio_name in line for line in output_lines), f"Missing audio mapping for {audio_name}")
                self.assertFalse(any('<u><b>' in line.lower() for line in output_lines), "Expected no formatting tags in output")

            for audio_name in audio_files:
                target_path = os.path.join(media_dir, audio_name)
                self.assertTrue(os.path.exists(target_path), f"Audio file {audio_name} was not synced")
                with open(target_path, 'rb') as f:
                    self.assertIn(b"audio payload", f.read())


if __name__ == "__main__":
    unittest.main()
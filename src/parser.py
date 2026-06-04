import os
import re
from typing import List, Tuple

class AudioRepository:
    """Handles scanning, validating, and sorting audio files by their numeric prefix."""
    def __init__(self, audio_dir: str):
        self.audio_dir = audio_dir

    def _get_numeric_prefix(self, filename: str) -> int:
        """Extracts the leading number from filenames like '12 - Drink up...mp3'."""
        match = re.match(r'^(\d+)\s*-\s*', filename)
        if match:
            return int(match.group(1))
        return float('inf')  # Put unnumbered files at the end

    def get_sorted_audio_files(self) -> List[str]:
        if not os.path.exists(self.audio_dir):
            raise FileNotFoundError(f"Audio directory not found: {self.audio_dir}")
            
        files = [f for f in os.listdir(self.audio_dir) if f.lower().endswith('.mp3')]
        return sorted(files, key=self._get_numeric_prefix)


class TextParser:
    """Handles extracting clean English-Portuguese sentence pairs from source text files."""
    def __init__(self, text_dir: str):
        self.text_dir = text_dir

    def _is_english_sentence(self, text: str) -> bool:
        """
        Differentiates English example sentences from Portuguese translations and structural headers
        using a high-accuracy, low-dependency keyword intersection scoring method.
        """
        cleaned = text.strip()
        # Filter out obvious structural lines, empty lines, or parenthetical annotations
        if not cleaned or cleaned.startswith('---') or cleaned.startswith('('):
            return False
        if re.match(r'^\d+', cleaned) or "mairovergara" in cleaned.lower():
            return False

        # Tokenize lowercase words, catching international character sets and curly quotes safely
        words = set(re.findall(r'\b[a-zà-ÿ́’\']+\b', cleaned.lower()))
        if not words:
            return False

        # Strategic high-frequency anchor words to verify language domain
        english_anchors = {
            'the', 'it', 'i', 'you', 'he', 'she', 'we', 'they', 'is', 'was', 'were', 
            'can', 'cant', 'could', 'would', 'should', 'have', 'has', 'had', 'for', 
            'to', 'of', 'in', 'on', 'at', 'with', 'this', 'that', 'my', 'your', 
            'his', 'her', 'their', 'our', 'always', 'never', 'but', 'and', 'any', 
            'some', 'all', 'dont', 'doesnt', 'didnt', 'not', 'are', 'am', 'go', 'went', 'going'
        }
        
        portuguese_anchors = {
            'o', 'a', 'os', 'as', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 
            'nos', 'nas', 'um', 'uma', 'uns', 'umas', 'com', 'para', 'por', 'mais', 
            'não', 'nao', 'mas', 'ele', 'ela', 'você', 'voce', 'nós', 'nos', 'eles', 
            'elas', 'me', 'se', 'ao', 'aos', 'que', 'como', 'foi', 'fomos', 'são', 
            'sao', 'é', 'ou', 'já', 'ja', 'bem', 'muito', 'esta', 'está', 'estava', 
            'pelo', 'pela', 'pelos', 'pelas', 'num', 'numa'
        }

        english_score = len(words.intersection(english_anchors))
        portuguese_score = len(words.intersection(portuguese_anchors))

        # Core Rule: An English sentence must contain at least one anchor word 
        # and outperform the Portuguese keyword density evaluation.
        return english_score > 0 and english_score >= portuguese_score

    def extract_pairs(self) -> List[Tuple[str, str]]:
        if not os.path.exists(self.text_dir):
            raise FileNotFoundError(f"Text directory not found: {self.text_dir}")

        pairs = []
        files = [f for f in os.listdir(self.text_dir) if f.lower().endswith('.txt')]
        
        for filename in sorted(files):
            file_path = os.path.join(self.text_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            i = 0
            while i < len(lines):
                current_line = lines[i]
                
                if self._is_english_sentence(current_line):
                    translation_parts = []
                    next_idx = i + 1
                    
                    # Interleave scanner: consume text blocks until the next English sentence marker
                    while next_idx < len(lines) and not self._is_english_sentence(lines[next_idx]):
                        cleaned_next = lines[next_idx].strip()
                        if "conheça mais" in cleaned_next.lower() or "www." in cleaned_next.lower() or re.match(r'^\d+', cleaned_next):
                            break
                        translation_parts.append(cleaned_next)
                        next_idx += 1
                    
                    if translation_parts:
                        portuguese_txt = " ".join(translation_parts)
                        pairs.append((current_line, portuguese_txt))
                        print(f"[Debug Parsing] Matched Pair:\n  EN: {current_line}\n  PT: {portuguese_txt}\n")
                        i = next_idx
                        continue
                i += 1
        return pairs


class AnkiPackageGenerator:
    """Binds text pairs and audio filenames together into an Anki-readable flashcard file."""
    def __init__(self, audio_repo: AudioRepository, text_parser: TextParser):
        self.audio_repo = audio_repo
        self.text_parser = text_parser

    def generate_import_file(self, output_path: str):
        audio_files = self.audio_repo.get_sorted_audio_files()
        text_pairs = self.text_parser.extract_pairs()

        if not text_pairs:
            print("[Error] No text pairs were successfully extracted. Check your source text files.")
            return

        if len(audio_files) != len(text_pairs):
            print(f"\n[Warning] Mismatch detected! Found {len(audio_files)} audio files and {len(text_pairs)} text pairs.")
            print("Proceeding with the smaller count to preserve 1-to-1 sequential alignment.\n")

        total_cards = min(len(audio_files), len(text_pairs))
        
        with open(output_path, 'w', encoding='utf-8') as out_file:
            for idx in range(total_cards):
                english, portuguese = text_pairs[idx]
                audio_filename = audio_files[idx]
                
                # Bundle phrase and sound tag on the front; translation on the back
                front_field = f"{english}[sound:{audio_filename}]"
                back_field = portuguese
                
                out_file.write(f"{front_field}\t{back_field}\n")
                
        print(f"[Success] Generated {total_cards} cards inside '{output_path}'")


if __name__ == "__main__":
    try:
        audio_repo = AudioRepository(audio_dir="./inputs/audio")
        text_parser = TextParser(text_dir="./inputs/text")
        
        generator = AnkiPackageGenerator(audio_repo, text_parser)
        generator.generate_import_file(output_path="./anki_import.txt")
        
    except Exception as e:
        print(f"[Error] Execution failed: {e}")
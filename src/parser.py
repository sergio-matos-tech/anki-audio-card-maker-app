import os
import re
import platform
import shutil
from typing import List, Tuple
from pypdf import PdfReader

class AudioRepository:
    """Handles scanning, validating, and sorting audio files by their numeric prefix."""
    def __init__(self, search_dir: str):
        self.search_dir = search_dir

    def _get_numeric_prefix(self, filename: str) -> int:
        match = re.match(r'^(\d+)\s*-\s*', filename)
        if match: return int(match.group(1))
        return float('inf')

    def get_sorted_audio_files(self) -> List[str]:
        if not os.path.exists(self.search_dir):
            raise FileNotFoundError(f"Directory not found: {self.search_dir}")
            
        files = []
        for f in os.listdir(self.search_dir):
            if f.lower().endswith('.mp3'):
                if self._get_numeric_prefix(f) != float('inf'):
                    files.append(f)
                    
        return sorted(files, key=self._get_numeric_prefix)


class AnkiMediaSyncer:
    """Detects the host OS, resolves the core collection.media path, and automates asset syncing."""
    def __init__(self, profile_name: str = "User 1", log_callback=print):
        self.profile_name = profile_name
        self.log_callback = log_callback

    def resolve_media_dir(self) -> str:
        os_type = platform.system()
        
        if os_type == "Windows":
            base_dir = os.path.expandvars(r"%APPDATA%\Anki2")
        elif os_type == "Linux":
            native_path = os.path.expanduser("~/.local/share/Anki2")
            flatpak_path = os.path.expanduser("~/.var/app/net.ankiweb.Anki/.local/share/Anki2")
            base_dir = flatpak_path if not os.path.exists(native_path) and os.path.exists(flatpak_path) else native_path
        elif os_type == "Darwin":
            base_dir = os.path.expanduser("~/Library/Application Support/Anki2")
        else:
            return ""

        return os.path.join(base_dir, self.profile_name, "collection.media")

    def sync_audio_assets(self, source_dir: str, file_list: List[str]) -> bool:
        try:
            target_dir = self.resolve_media_dir()
            
            if not target_dir or not os.path.exists(target_dir):
                self.log_callback(f"[Warning] Anki target directory not found at: '{target_dir}'")
                self.log_callback("-> Skipping auto-copy. You will need to manually move the MP3 files.")
                return False
                
            self.log_callback(f"[Syncer] Target verified: {target_dir}")
            copied_count = 0
            
            for filename in file_list:
                source_path = os.path.join(source_dir, filename)
                target_path = os.path.join(target_dir, filename)
                
                if not os.path.exists(target_path):
                    shutil.copy2(source_path, target_path)
                    copied_count += 1
                    
            self.log_callback(f"[Success] Synced {copied_count} new audio assets directly to Anki.")
            return True
        except Exception as e:
            self.log_callback(f"[Warning] Media sync operation failed: {e}")
            return False


class TextParser:
    """Extracts clean English-Portuguese sentence pairs applying pre-filtering and a State Machine."""
    def __init__(self, search_dir: str, log_callback=print):
        self.search_dir = search_dir
        self.log_callback = log_callback

    def _is_english_sentence(self, text: str) -> bool:
        cleaned = text.strip()
        if not cleaned or cleaned.startswith('---'): return False

        words = set(re.findall(r'\b[a-zà-ÿ́’\']+\b', cleaned.lower()))
        if not words: return False

        english_anchors = {
            'the', 'it', 'i', 'you', 'he', 'she', 'we', 'they', 'is', 'was', 'were', 
            'can', 'cant', 'could', 'would', 'should', 'have', 'has', 'had', 'for', 
            'to', 'of', 'in', 'on', 'at', 'with', 'this', 'that', 'my', 'your', 
            'his', 'her', 'their', 'our', 'always', 'never', 'but', 'and', 'any', 
            'some', 'all', 'dont', 'doesnt', 'didnt', 'not', 'are', 'am', 'go', 'went', 
            'going', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'now', 
            'here', 'there', 'who', 'what', 'where', 'when', 'why', 'how', 'do', 'did', 
            'does', 'make', 'made', 'get', 'got', 'take', 'took', 'come', 'came', 
            'say', 'said', 'know', 'knew', 'think', 'thought', 'see', 'saw', 'look', 
            'want', 'give', 'gave', 'use', 'find', 'tell', 'ask', 'work', 'seem', 
            'feel', 'try', 'leave', 'call', 'drink', 'drank', 'okay', 'yes', 'no', 
            'let', 'lets', 'dear', 'kid', 'boy', 'girl', 'time', 'home', 'back', 
            'just', 'only', 'much', 'many', 'very', 'too', 'also', 'well', 'way', 
            'even', 'new', 'good', 'bad', 'great', 'right', 'really', 'us', 'ill', 'turn', 'once', 'more'
        }
        
        portuguese_anchors = {
            'o', 'a', 'os', 'as', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 
            'nos', 'nas', 'um', 'uma', 'uns', 'umas', 'com', 'para', 'por', 'mais', 
            'não', 'nao', 'mas', 'ele', 'ela', 'você', 'voce', 'nós', 'nos', 'eles', 
            'elas', 'me', 'se', 'ao', 'aos', 'que', 'como', 'foi', 'fomos', 'são', 
            'sao', 'é', 'ou', 'já', 'ja', 'bem', 'muito', 'esta', 'está', 'estava', 
            'pelo', 'pela', 'pelos', 'pelas', 'num', 'numa', 'eu', 'tu', 'meu', 
            'minha', 'meus', 'minhas', 'teu', 'tua', 'seu', 'sua', 'seus', 'suas', 
            'nosso', 'nossa', 'este', 'esse', 'essa', 'isso', 'isto', 'aquilo', 
            'aquele', 'aquela', 'qual', 'quais', 'quem', 'tudo', 'nada', 'algo', 
            'alguém', 'alguem', 'nenhum', 'nenhuma', 'cada', 'qualquer', 'ser', 
            'estar', 'ter', 'haver', 'fazer', 'ir', 'poder', 'dizer', 'saber', 'querer', 
            'ficar', 'ver', 'dar', 'achar', 'passar', 'dever', 'chegar', 'falar', 
            'deixar', 'encontrar', 'levar', 'começar', 'partir', 'parecer', 'olhar', 
            'aqui', 'ali', 'lá', 'cá', 'hoje', 'ontem', 'amanhã', 'agora', 'depois', 
            'antes', 'sempre', 'nunca', 'quase', 'talvez', 'sim', 'certeza', 'vez',
            'significando', 'copo', 'veja'
        }

        english_score = len(words.intersection(english_anchors))
        portuguese_score = len(words.intersection(portuguese_anchors))

        return english_score > 0 and english_score > portuguese_score

    def _apply_en_formatting(self, text: str, pv_name: str) -> str:
        if not pv_name or " " not in pv_name: return text
            
        parts = pv_name.split(maxsplit=1)
        verb_base = parts[0].lower()
        particle = parts[1].lower()
        
        inflections = {
            "drink": ["drink", "drank", "drunk", "drinking", "drinks"],
            "work": ["work", "worked", "working", "works"],
            "break": ["break", "broke", "broken", "breaking", "breaks"],
            "call": ["call", "called", "calling", "calls"],
            "carry": ["carry", "carried", "carrying", "carries"],
            "get": ["get", "got", "gotten", "getting", "gets"],
            "give": ["give", "gave", "given", "giving", "gives"],
            "go": ["go", "went", "gone", "going", "goes"],
            "keep": ["keep", "kept", "keeping", "keeps"],
            "look": ["look", "looked", "looking", "looks"],
            "make": ["make", "made", "making", "makes"],
            "put": ["put", "putting", "puts"],
            "run": ["run", "ran", "running", "runs"],
            "take": ["take", "took", "taken", "taking", "takes"],
            "turn": ["turn", "turned", "turning", "turns"],
        }
        
        forms = inflections.get(verb_base, [verb_base, verb_base + "ed", verb_base + "ing", verb_base + "s"])
        verb_pattern = "|".join(forms)
        
        pattern = rf"\b({verb_pattern})\b[\w\s—’']{{0,30}}\b{particle}\b"
        return re.sub(pattern, r'<u><b>\g<0></b></u>', text, flags=re.IGNORECASE)

    def _apply_pt_formatting(self, text: str, pv_name: str) -> str:
        if not pv_name: return text
        
        pt_registry = {
            "DRINK UP": r"\b(beber\studo|bebeu\studo|beber\stodo|bebeu\stodo|beba\stodo|entorne\so\scopo|entornar\so\scopo|beber|bebeu|beba|entorne|entornar|bebeu\stodo)\b",
            "WORK UP": r"\b(gerar|abriu|abremos|juntar|começou\sa\ssuar|abrir|ficado\scom|chegar\sa\ssuar|preparou|arrumar|progrediu)\b",
            "PUT THROUGH": r"\b(colocados|passar\spor|submeter|enviar)\b"
        }
        
        pattern = pt_registry.get(pv_name.upper())
        if not pattern: return text
            
        return re.sub(pattern, r'<u><b>\g<0></b></u>', text, flags=re.IGNORECASE)

    def extract_pairs(self) -> List[Tuple[str, str]]:
        if not os.path.exists(self.search_dir):
            raise FileNotFoundError(f"Directory not found: {self.search_dir}")

        pairs = []
        files = [f for f in os.listdir(self.search_dir) if f.lower().endswith(('.txt', '.pdf'))]
        
        for filename in sorted(files):
            pv_name = filename.split(" - ")[0].strip() if " - " in filename else ""
            file_path = os.path.join(self.search_dir, filename)
            full_text = ""

            if filename.lower().endswith('.pdf'):
                self.log_callback(f"[Processor] Reading PDF document: {filename}")
                reader = PdfReader(file_path)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text: full_text += " " + page_text
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    full_text = f.read()

            footer_match = re.search(r'(?i)(bons estudos|nosso site:)', full_text)
            if footer_match: full_text = full_text[:footer_match.start()]
            full_text = re.sub(r'(?i)phrasal verb:\s*[a-z\s]+', '', full_text)
            full_text = re.sub(r'(www\.[^\s]+|https?://[^\s]+)', '', full_text)

            sanitized_text = re.sub(r'([.!?:][)"’]?)([A-Za-zÀ-ÿ(])', r'\1 \2', full_text)
            normalized_text = re.sub(r'\s+', ' ', sanitized_text)
            split_text = re.sub(r'([.!?:][)"’]?)\s+', r'\1<SPLIT>', normalized_text)
            chunks = [c.strip() for c in split_text.split('<SPLIT>') if c.strip()]

            current_en = []
            current_pt = []
            
            for chunk in chunks:
                if self._is_english_sentence(chunk):
                    if current_pt:
                        english_txt = " ".join(current_en)
                        portuguese_txt = " ".join(current_pt)
                        english_txt = self._apply_en_formatting(english_txt, pv_name)
                        portuguese_txt = self._apply_pt_formatting(portuguese_txt, pv_name)
                        pairs.append((english_txt, portuguese_txt))
                        current_en = []
                        current_pt = []
                    current_en.append(chunk)
                else:
                    if current_en:
                        is_noise = (
                            "mairovergara" in chunk.lower() or 
                            "conheça mais" in chunk.lower() or
                            "leia o post" in chunk.lower() or
                            "nosso site" in chunk.lower() or
                            "youtube" in chunk.lower() or
                            "aprenda inglês" in chunk.lower() or
                            "facebook" in chunk.lower() or
                            "linkedin" in chunk.lower() or
                            re.match(r'^\d+\s*[-–—]', chunk) or
                            (chunk.startswith('(') and chunk.endswith(')'))
                        )
                        if not is_noise: current_pt.append(chunk)
                            
            if current_en and current_pt:
                english_txt = " ".join(current_en)
                portuguese_txt = " ".join(current_pt)
                english_txt = self._apply_en_formatting(english_txt, pv_name)
                portuguese_txt = self._apply_pt_formatting(portuguese_txt, pv_name)
                pairs.append((english_txt, portuguese_txt))
                
        return pairs


class AnkiPackageGenerator:
    """Binds text pairs and audio filenames together into an Anki-readable flashcard file."""
    def __init__(self, audio_repo: AudioRepository, text_parser: TextParser, log_callback=print):
        self.audio_repo = audio_repo
        self.text_parser = text_parser
        self.log_callback = log_callback

    def generate_import_file(self, output_path: str) -> List[str]:
        audio_files = self.audio_repo.get_sorted_audio_files()
        text_pairs = self.text_parser.extract_pairs()

        if not text_pairs:
            self.log_callback("[Error] No text pairs were successfully extracted.")
            return []

        total_cards = min(len(audio_files), len(text_pairs))
        used_audio_files = []
        
        with open(output_path, 'w', encoding='utf-8') as out_file:
            for idx in range(total_cards):
                english, portuguese = text_pairs[idx]
                audio_filename = audio_files[idx]
                
                front_field = f"{english}[sound:{audio_filename}]"
                back_field = portuguese
                out_file.write(f"{front_field}\t{back_field}\n")
                used_audio_files.append(audio_filename)
                
        self.log_callback(f"[Success] Generated mapping file inside '{output_path}'")
        return used_audio_files


# =====================================================================
#  UI EXPOSURE LAYER (The Controller Entrypoint)
# =====================================================================
def execute_pipeline(inputs_dir: str, anki_profile: str = "User 1", log_callback=print, output_path: str = None) -> bool:
    """Core orchestration engine decoupled from hardcoded terminal environments."""
    try:
        if not os.path.exists(inputs_dir):
            log_callback(f"[Error] Selected directory does not exist: {inputs_dir}")
            return False

        audio_repo = AudioRepository(search_dir=inputs_dir)
        text_parser = TextParser(search_dir=inputs_dir, log_callback=log_callback)
        
        # === SE O USUÁRIO NÃO PASSOU CAMINHO (FALLBACK/TESTES), GERA AUTOMATICAMENTE ===
        if not output_path:
            doc_files = [f for f in os.listdir(inputs_dir) if f.lower().endswith(('.txt', '.pdf'))]
            if not doc_files:
                log_callback("[Error] No valid .pdf or .txt source documents found in directory.")
                return False
            pv_name = doc_files[0].split(" - ")[0].strip()
            parent_dir = os.path.dirname(os.path.abspath(inputs_dir))
            output_path = os.path.join(parent_dir, f"{pv_name}.txt")
        # ==============================================================================
        
        generator = AnkiPackageGenerator(audio_repo, text_parser, log_callback=log_callback)
        active_audios = generator.generate_import_file(output_path=output_path)
        
        if active_audios:
            syncer = AnkiMediaSyncer(profile_name=anki_profile, log_callback=log_callback)
            syncer.sync_audio_assets(source_dir=inputs_dir, file_list=active_audios)
            
        log_callback("--- All Pipeline Tasks Completed Successfully ---")
        return True
    except Exception as e:
        log_callback(f"[Error] Pipeline execution crash: {e}")
        return False


if __name__ == "__main__":
    # Backwards compatibility check: allows CLI execution if ran directly
    print("[CLI] Running in fallback standalone script mode...")
    execute_pipeline(inputs_dir="./inputs", anki_profile="User 1")
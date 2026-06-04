import os
import queue
import threading
import customtkinter as ctk
from customtkinter import filedialog
from src.parser import execute_pipeline

# Configuração global de aparência do CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AnkiAlignerApp(ctk.CTk):
    """A View layer component establishing a clean modern desktop interface."""
    
    def __init__(self):
        super().__init__()
        
        # Configurações de Janela
        self.title("Anki Media Stream Aligner")
        self.geometry("680x480")
        self.resizable(False, False)
        
        # State Variables
        self.selected_path = ctk.StringVar(value="No folder selected...")
        self.profile_name = ctk.StringVar(value="User 1")
        
        # Fila Thread-safe para isolamento total da thread de processamento
        self.log_queue = queue.Queue()
        
        self._build_ui_layout()
        
        # Inicia o loop de monitoramento da fila na thread principal
        self.after(10, self._check_log_queue)

    def _build_ui_layout(self):
        """Constructs a responsive grid layout split by logical user actions."""
        
        # --- TITLE BANNER ---
        self.title_label = ctk.CTkLabel(
            self, text="Anki Stream Sync Pipeline", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(pady=(20, 15))

        # --- CONFIGURATION FRAME ---
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.pack(pady=10, padx=30, fill="x")
        
        self.profile_label = ctk.CTkLabel(self.config_frame, text="Anki Profile Name:")
        self.profile_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.profile_entry = ctk.CTkEntry(self.config_frame, textvariable=self.profile_name, width=150)
        self.profile_entry.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        # --- FOLDER SELECTION FRAME ---
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.pack(pady=10, padx=30, fill="x")
        
        self.browse_btn = ctk.CTkButton(
            self.folder_frame, text="📁 Select Source Folder", 
            command=self._handle_browse_directory, width=160
        )
        self.browse_btn.grid(row=0, column=0, padx=15, pady=15)
        
        self.path_label = ctk.CTkLabel(
            self.folder_frame, textvariable=self.selected_path, 
            wraplength=420, anchor="w", justify="left"
        )
        self.path_label.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        # --- CONSOLE LOGGER STREAM (OUTPUT VIEW) ---
        self.console_box = ctk.CTkTextbox(self, height=180, font=ctk.CTkFont(family="Consolas", size=11))
        self.console_box.pack(pady=15, padx=30, fill="x")
        self.console_box.configure(state="disabled")
        
        # --- ACTION TRIGGER ---
        self.execute_btn = ctk.CTkButton(
            self, text="⚡ GENERATE & SYNC ASSETS", 
            command=self._trigger_pipeline_execution, 
            height=40, font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2b8c45", hover_color="#1e6330"
        )
        self.execute_btn.pack(pady=(10, 20))

    def _handle_browse_directory(self):
        """Launches a native OS directory selector context."""
        directory = filedialog.askdirectory()
        if directory:
            self.selected_path.set(os.path.abspath(directory))
            self._write_to_console(f"[UI] Source target locked: {directory}")

    def _write_to_console(self, text: str):
        """Thread-safe storage pushing messages directly to the queue buffer."""
        self.log_queue.put(text)

    def _check_log_queue(self):
        """Cyclic consumer on the main thread processing backend data packets."""
        try:
            while not self.log_queue.empty():
                item = self.log_queue.get_nowait()
                
                # Se o item for um Booleano, representa o sinalizador de conclusão da pipeline
                if isinstance(item, bool):
                    self._finalize_ui_state(item)
                else:
                    self._thread_safe_log(item)
        except queue.Empty:
            pass
        
        # Reagenda a verificação de forma segura na thread da interface
        self.after(10, self._check_log_queue)

    def _thread_safe_log(self, text: str):
        self.console_box.configure(state="normal")
        self.console_box.insert("end", text + "\n")
        self.console_box.see("end")
        self.console_box.configure(state="disabled")

    def _trigger_pipeline_execution(self):
        """Delegates processing load onto a background worker thread to prevent UI freezing."""
        target_dir = self.selected_path.get()
        profile = self.profile_name.get()
        
        if target_dir in ["No folder selected...", ""]:
            self._write_to_console("[UI Error] Execution aborted: You must lock a valid source directory first.")
            return

        # --- NOVA FUNCIONALIDADE: Captura o nome do PV para sugerir no salvamento ---
        try:
            doc_files = [f for f in os.listdir(target_dir) if f.lower().endswith(('.txt', '.pdf'))]
            default_name = doc_files[0].split(" - ")[0].strip() if doc_files else "anki_import"
        except Exception:
            default_name = "anki_import"

        # Abre a janela nativa de salvar arquivo na Thread Principal
        save_path = filedialog.asksaveasfilename(
            title="Escolha onde salvar o arquivo de importação do Anki",
            initialfile=f"{default_name}.txt",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not save_path:
            self._write_to_console("[UI] Operação cancelada pelo usuário (Local de salvamento não definido).")
            return

        self.execute_btn.configure(state="disabled", text="PROCESSING...")
        self.console_box.configure(state="normal")
        self.console_box.delete("1.0", "end")
        self.console_box.configure(state="disabled")
        
        self._write_to_console("[UI] Spawning background worker thread...")
        
        worker = threading.Thread(
            target=self._async_pipeline_worker, 
            args=(target_dir, profile, save_path), 
            daemon=True
        )
        worker.start()

    def _async_pipeline_worker(self, target_dir: str, profile: str, save_path: str):
        """Pure backend execution sequence completely decoupled from Tkinter window references."""
        success = execute_pipeline(
            inputs_dir=target_dir, 
            anki_profile=profile, 
            log_callback=self._write_to_console,
            output_path=save_path  
        )
        self.log_queue.put(success)

    def _finalize_ui_state(self, success: bool):
        self.execute_btn.configure(state="normal", text="⚡ GENERATE & SYNC ASSETS")
        if success:
            self._write_to_console("[UI] Execution Complete. Your flashcard text is ready for Anki manual import.")


if __name__ == "__main__":
    app = AnkiAlignerApp()
    app.mainloop()
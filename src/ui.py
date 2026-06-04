import os
import queue
import threading

import customtkinter as ctx
from customtkinter import filedialog

from src.parser import execute_pipeline

ctx.set_appearance_mode("System")
ctx.set_default_color_theme("blue")


class AnkiAlignerApp(ctx.CTk):
    def __init__(self):
        super().__init__()

        self.title("Anki Audio Card Maker")
        self.geometry("680x520")
        self.resizable(False, False)

        self.selected_path = ctx.StringVar(value="No folder selected...")
        self.profile_name = ctx.StringVar(value="User 1")
        self.log_queue = queue.Queue()

        self._build_ui_layout()
        self.after(10, self._check_log_queue)

    def _build_ui_layout(self):
        self.title_label = ctx.CTkLabel(
            self,
            text="Anki Audio Card Maker",
            font=ctx.CTkFont(size=22, weight="bold"),
        )
        self.title_label.pack(pady=(20, 15))

        self.config_frame = ctx.CTkFrame(self)
        self.config_frame.pack(pady=10, padx=30, fill="x")

        self.profile_label = ctx.CTkLabel(self.config_frame, text="Anki profile:")
        self.profile_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.profile_entry = ctx.CTkEntry(
            self.config_frame,
            textvariable=self.profile_name,
            width=150,
        )
        self.profile_entry.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        self.folder_frame = ctx.CTkFrame(self)
        self.folder_frame.pack(pady=10, padx=30, fill="x")

        self.browse_btn = ctx.CTkButton(
            self.folder_frame,
            text="Choose lesson folder",
            command=self._handle_browse_directory,
            width=170,
        )
        self.browse_btn.grid(row=0, column=0, padx=15, pady=15)

        self.path_label = ctx.CTkLabel(
            self.folder_frame,
            textvariable=self.selected_path,
            wraplength=420,
            anchor="w",
            justify="left",
        )
        self.path_label.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        self.progress_bar = ctx.CTkProgressBar(self, mode="indeterminate", height=8)
        self.progress_bar.set(0)

        self.console_box = ctx.CTkTextbox(
            self,
            height=160,
            font=ctx.CTkFont(family="Consolas", size=11),
        )
        self.console_box.pack(pady=15, padx=30, fill="x")
        self.console_box.configure(state="disabled")

        self.status_banner = ctx.CTkLabel(
            self,
            text="",
            height=45,
            corner_radius=6,
            font=ctx.CTkFont(size=12, weight="bold"),
            text_color="white",
        )

        self.execute_btn = ctx.CTkButton(
            self,
            text="Create Anki import file",
            command=self._trigger_pipeline_execution,
            height=40,
            font=ctx.CTkFont(size=14, weight="bold"),
            fg_color="#2b8c45",
            hover_color="#1e6330",
        )
        self.execute_btn.pack(pady=(10, 20))

    def _handle_browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.selected_path.set(os.path.abspath(directory))
            self._write_to_console(f"[Folder] Lesson folder selected: {directory}")

    def _write_to_console(self, text: str):
        self.log_queue.put(text)

    def _check_log_queue(self):
        try:
            while not self.log_queue.empty():
                item = self.log_queue.get_nowait()
                if isinstance(item, bool):
                    self._finalize_ui_state(item)
                else:
                    self._thread_safe_log(item)
        except queue.Empty:
            pass
        self.after(10, self._check_log_queue)

    def _thread_safe_log(self, text: str):
        self.console_box.configure(state="normal")
        self.console_box.insert("end", text + "\n")
        self.console_box.see("end")
        self.console_box.configure(state="disabled")

    def _trigger_pipeline_execution(self):
        target_dir = self.selected_path.get()
        profile = self.profile_name.get()

        if target_dir in ["No folder selected...", ""]:
            self._write_to_console("[Error] Please choose a lesson folder first.")
            return

        try:
            doc_files = [
                f for f in os.listdir(target_dir)
                if f.lower().endswith((".txt", ".pdf"))
            ]
            default_name = doc_files[0].split(" - ")[0].strip() if doc_files else "anki_import"
        except Exception:
            default_name = "anki_import"

        save_path = filedialog.asksaveasfilename(
            title="Save the Anki import file",
            initialfile=f"{default_name}.txt",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )

        if not save_path:
            self._write_to_console("[Warning] Save canceled.")
            return

        self.status_banner.pack_forget()
        self.execute_btn.configure(state="disabled", text="Creating...")
        self.progress_bar.pack(before=self.console_box, pady=(0, 10), padx=30, fill="x")
        self.progress_bar.start()

        self.console_box.configure(state="normal")
        self.console_box.delete("1.0", "end")
        self.console_box.configure(state="disabled")

        worker = threading.Thread(
            target=self._async_pipeline_worker,
            args=(target_dir, profile, save_path),
            daemon=True,
        )
        worker.start()

    def _async_pipeline_worker(self, target_dir: str, profile: str, save_path: str):
        success = execute_pipeline(
            inputs_dir=target_dir,
            anki_profile=profile,
            log_callback=self._write_to_console,
            output_path=save_path,
        )
        self.log_queue.put(success)

    def _finalize_ui_state(self, success: bool):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.execute_btn.configure(state="normal", text="Create Anki import file")

        if success:
            self.status_banner.configure(
                text="Done. Open Anki and import the TXT file.",
                fg_color="#10b981",
            )
        else:
            self.status_banner.configure(
                text="Something went wrong. Check the log above.",
                fg_color="#ef4444",
            )

        self.status_banner.pack(before=self.execute_btn, pady=(0, 10), padx=30, fill="x")


if __name__ == "__main__":
    app = AnkiAlignerApp()
    app.mainloop()

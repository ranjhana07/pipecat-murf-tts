import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from dotenv import load_dotenv
from loguru import logger


def load_api_key() -> str:
    load_dotenv(override=True)
    api_key = os.getenv("MURF_API_KEY")
    if not api_key:
        raise RuntimeError(
            "MURF_API_KEY is missing. Set it in .env or environment."
        )
    return api_key

def speak_in_subprocess(text: str, voice_id: str, style: str):
    """Launch a separate Python process to play TTS once.

    Using a subprocess avoids signal-handling restrictions in threads.
    """
    python_exe = sys.executable
    script_path = os.path.join(
        os.path.dirname(__file__),
        "play_once.py",
    )

    cmd = [
        python_exe,
        script_path,
        "--text",
        text,
        "--voice",
        voice_id,
        "--style",
        style,
    ]

    # Ensure API key exists before spawning
    _ = load_api_key()

    subprocess.run(cmd, check=True)


def make_gui():
    root = tk.Tk()
    root.title("Murf TTS Tester")
    root.geometry("520x260")

    main = ttk.Frame(root, padding=16)
    main.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main, text="Text to speak:").grid(row=0, column=0, sticky="w")
    text_var = tk.StringVar(value="Hello! This is Murf TTS.")
    text_entry = ttk.Entry(main, textvariable=text_var, width=60)
    text_entry.grid(row=1, column=0, columnspan=3, sticky="we", pady=(4, 12))

    ttk.Label(main, text="Voice:").grid(row=2, column=0, sticky="w")
    voice_var = tk.StringVar(value="en-UK-ruby")
    voice_entry = ttk.Entry(main, textvariable=voice_var, width=24)
    voice_entry.grid(row=2, column=1, sticky="w")

    ttk.Label(main, text="Style:").grid(row=3, column=0, sticky="w", pady=(8, 0))
    style_var = tk.StringVar(value="Conversational")
    style_entry = ttk.Entry(main, textvariable=style_var, width=24)
    style_entry.grid(row=3, column=1, sticky="w")

    status_var = tk.StringVar(value="Ready")
    status = ttk.Label(main, textvariable=status_var)
    status.grid(row=4, column=0, columnspan=3, sticky="w", pady=(12, 8))

    def on_speak():
        text = text_var.get().strip()
        if not text:
            messagebox.showwarning("Input required", "Please enter some text.")
            return
        status_var.set("Speaking…")

        def run():
            try:
                speak_in_subprocess(text, voice_var.get().strip(), style_var.get().strip())
                status_var.set("Done")
            except subprocess.CalledProcessError as e:
                logger.error(f"Playback failed: {e}")
                status_var.set("Error")
                messagebox.showerror("Error", f"Playback failed: {e}")
            except Exception as e:
                logger.error(f"Error: {e}")
                status_var.set("Error")
                messagebox.showerror("Error", str(e))

        threading.Thread(target=run, daemon=True).start()

    speak_btn = ttk.Button(main, text="Speak", command=on_speak)
    speak_btn.grid(row=5, column=0, sticky="w")

    for i in range(3):
        main.columnconfigure(i, weight=1)

    return root


if __name__ == "__main__":
    try:
        root = make_gui()
        root.mainloop()
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

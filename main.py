import customtkinter as ctk
from tkinter import filedialog, messagebox
import pygame
import keyboard
import os
import json
import threading

# Initialize pygame for sound playback
pygame.mixer.init()

class HotPhraseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hot Phrase v1.0.0")  # Specify the program version
        self.root.geometry("800x700")  # Increase window size
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # List of phrases
        self.phrases = []

        # Create a scrollable frame for phrases
        self.scrollable_frame = ctk.CTkScrollableFrame(self.root, width=780, height=500)
        self.scrollable_frame.pack(pady=10, padx=10, fill='both', expand=True)

        # Load saved data if available
        self.load_phrases()

        # Create a frame for buttons at the bottom
        bottom_frame = ctk.CTkFrame(self.root)
        bottom_frame.pack(side=ctk.BOTTOM, fill=ctk.X, pady=10, padx=10)

        # Add buttons
        self.add_phrase_button = ctk.CTkButton(
            bottom_frame, text="Add Button", command=self.add_phrase,
            width=400,  # Increased size
            height=40
        )
        self.add_phrase_button.pack(pady=5)

        self.settings_button = ctk.CTkButton(
            bottom_frame, text="Settings", command=self.open_settings,
            width=400,  # Increased size
            height=40
        )
        self.settings_button.pack(pady=5)

        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_phrase(self, phrase_data=None):
        phrase_frame = ctk.CTkFrame(self.scrollable_frame)
        phrase_frame.pack(pady=5, padx=10, fill='x')

        if phrase_data:
            sound_path = phrase_data.get("sound_path", "")
            hotkey = phrase_data.get("hotkey", "")
            custom_name = phrase_data.get("custom_name", "")
        else:
            sound_path = ""
            hotkey = ""
            custom_name = ""

        phrase_entry = ctk.CTkEntry(phrase_frame, width=200)
        phrase_entry.pack(side=ctk.LEFT, padx=5)
        if custom_name:
            phrase_entry.insert(0, custom_name)
        else:
            phrase_entry.insert(0, "File Name")
        phrase_frame.phrase_entry = phrase_entry

        select_sound_button = ctk.CTkButton(phrase_frame, text="Select File",
                                            command=lambda: self.select_sound(phrase_frame))
        select_sound_button.pack(side=ctk.LEFT, padx=5)

        select_hotkey_button = ctk.CTkButton(phrase_frame, text="Select Key",
                                             command=lambda: self.select_hotkey(phrase_frame))
        select_hotkey_button.pack(side=ctk.LEFT, padx=5)

        delete_button = ctk.CTkButton(
            phrase_frame, text="Delete", command=phrase_frame.destroy,
            fg_color="#962929",  # Color for delete button
            hover_color="#6B1E1E"  # Hover color
        )
        delete_button.pack(side=ctk.LEFT, padx=5)

        progress_bar = ctk.CTkProgressBar(phrase_frame, width=200)
        progress_bar.pack(side=ctk.LEFT, padx=5)
        phrase_frame.progress_bar = progress_bar

        if sound_path:
            phrase_frame.sound_path = sound_path
        if hotkey:
            phrase_frame.hotkey = hotkey

        self.phrases.append(phrase_frame)

        # Automatically apply changes for the new phrase
        self.apply_phrase_hotkey(phrase_frame)

    def select_sound(self, frame):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if file_path:
            frame.sound_path = file_path
            # Automatically apply the sound change
            self.apply_phrase_hotkey(frame)

    def select_hotkey(self, frame):
        def on_key_press(event):
            frame.hotkey = event.name
            keyboard.unhook_all()
            # Automatically apply the hotkey change
            self.apply_phrase_hotkey(frame)

        keyboard.hook(on_key_press)

    def apply_phrase_hotkey(self, phrase_frame):
        if hasattr(phrase_frame, 'hotkey') and hasattr(phrase_frame, 'sound_path'):
            keyboard.add_hotkey(phrase_frame.hotkey,
                                lambda path=phrase_frame.sound_path, progress_bar=phrase_frame.progress_bar: self.play_sound(
                                    path, progress_bar))

    def play_sound(self, path, progress_bar):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

        # Get the length of the sound
        sound_length = pygame.mixer.Sound(path).get_length()

        def update_progress():
            while pygame.mixer.music.get_busy():
                current_pos = pygame.mixer.music.get_pos() / 1000  # Convert to seconds
                progress = current_pos / sound_length
                progress_bar.set(progress)
                self.root.update()
            progress_bar.set(0)

        # Start a thread to update the progress bar
        threading.Thread(target=update_progress).start()

    def on_closing(self):
        if messagebox.askyesno("Save", "Do you want to save changes?"):
            self.save_phrases()
        self.root.destroy()

    def save_phrases(self):
        data = []
        for phrase in self.phrases:
            if hasattr(phrase, 'hotkey') and hasattr(phrase, 'sound_path'):
                custom_name = phrase.phrase_entry.get() if hasattr(phrase, 'phrase_entry') else ""
                data.append({
                    "hotkey": phrase.hotkey,
                    "sound_path": phrase.sound_path,
                    "custom_name": custom_name
                })
        with open("phrases.json", "w") as f:
            json.dump(data, f)

    def load_phrases(self):
        if os.path.exists("phrases.json"):
            with open("phrases.json", "r") as f:
                data = json.load(f)
                for phrase_data in data:
                    self.add_phrase(phrase_data)

    def open_settings(self):
        messagebox.showinfo("Settings", "Settings will be here.")


if __name__ == "__main__":
    root = ctk.CTk()
    app = HotPhraseApp(root)
    root.mainloop()

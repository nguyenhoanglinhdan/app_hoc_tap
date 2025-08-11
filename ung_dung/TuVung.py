import json
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class man_hinh_them_tu_vung(tk.Frame):
    root_path = "du_lieu/tu_vung"

    def __init__(self, parent, grade, topic, switch_to_home):
        tk.Frame.__init__(self, parent)
        self.grade = grade
        self.topic = topic
        self.switch_to_home = switch_to_home
        self.words_data = []  # Store the actual word data

        style = ttk.Style()
        style.configure("Blue.TFrame", background="#333333")
        self.pack(fill="both", expand=True, padx=15, pady=15)
        self.columnconfigure(1, weight=1)

        self.word_var = tk.StringVar()
        self.meaning_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        self.create_header()
        self.create_body()

    def create_header(self):
        ttk.Label(self, text="Add Vocabulary", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)
        ttk.Label(self, text=f"Grade: {self.grade} | Topic: {self.topic}", font=("Arial", 10)).grid(row=1, column=0,
                                                                                                    columnspan=3,
                                                                                                    pady=5)

        # Back button
        back_button = ttk.Button(self, text="← Back to Home", command=self.switch_to_home)
        back_button.grid(row=2, column=0, pady=10, sticky="w")

    def create_body(self):
        # Vocabulary input
        ttk.Label(self, text="Từ vựng:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.word_var, width=30).grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Meaning input
        ttk.Label(self, text="Nghĩa:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.meaning_var, width=30).grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Add button
        add_button = ttk.Button(self, text="Add", command=self.save_word)
        add_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Existing vocabulary list
        ttk.Label(self, text="Existing Vocabulary:", font=("Arial", 10, "bold")).grid(row=6, column=0, columnspan=3,
                                                                                      pady=(20, 5), sticky="w")

        # Create a frame for the vocabulary list with scrollbar
        list_frame = tk.Frame(self)
        list_frame.grid(row=7, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Create canvas and scrollbar for the vocabulary list
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.vocab_frame = tk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure canvas
        canvas.create_window((0, 0), window=self.vocab_frame, anchor="nw")
        self.vocab_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Configure grid weights for the main frame
        self.rowconfigure(7, weight=1)

        self.load_words()

    def save_word(self):
        word = self.word_var.get()
        meaning = self.meaning_var.get()

        if word == "" or meaning == "":
            messagebox.showerror("Error", "Please fill both fields")
            return

        folder_path = tao_duong_dan(self.root_path, self.grade, self.topic)
        # check if file exists
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = f"{folder_path}/vocabulary.json"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                data["words"].append({"word": word, "meaning": meaning})
        except:
            data = {"words": []}
            data["words"].append({"word": word, "meaning": meaning})

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        messagebox.showinfo("Success", "Word added successfully")
        self.word_var.set("")
        self.meaning_var.set("")
        self.load_words()  # Refresh the list

    def delete_word(self, word_data):
        """Delete a specific word from the vocabulary"""
        word = word_data["word"]
        meaning = word_data["meaning"]

        folder_path = tao_duong_dan(self.root_path, self.grade, self.topic)
        file_path = f"{folder_path}/vocabulary.json"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Remove the word from the list
            data["words"] = [w for w in data["words"] if not (w["word"] == word and w["meaning"] == meaning)]

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            messagebox.showinfo("Success", f"Word '{word}' deleted successfully")
            self.load_words()  # Refresh the list

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete word: {str(e)}")

    def load_words(self):

        folder_path = tao_duong_dan(self.root_path, self.grade, self.topic)
        file_path = f"{folder_path}/vocabulary.json"

        # Clear existing widgets in vocab_frame
        for widget in self.vocab_frame.winfo_children():
            widget.destroy()

        self.words_data = []  # Reset the words data

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.words_data = data["words"]

                for i, word_data in enumerate(data["words"]):
                    # Create a frame for each word
                    word_frame = tk.Frame(self.vocab_frame)
                    word_frame.pack(fill="x", padx=5, pady=2)

                    # Word and meaning label
                    word_label = tk.Label(word_frame, text=f"{word_data['word']} - {word_data['meaning']}",
                                          anchor="w", font=("Arial", 9))
                    word_label.pack(side="left", fill="x", expand=True)

                    # Delete button
                    delete_btn = ttk.Button(word_frame, text="Delete",
                                            command=lambda w=word_data: self.delete_word(w))
                    delete_btn.pack(side="right", padx=(5, 0))

                    # Bind double-click to delete
                    word_label.bind("<Double-Button-1>", lambda e, w=word_data: self.delete_word(w))

        except FileNotFoundError:
            # File doesn't exist yet, that's okay
            pass

def tao_duong_dan(root_path, grade, topic):
    folder_path = f"{root_path}/{grade}/{topic}".lower().replace(" ", "_")
    return folder_path
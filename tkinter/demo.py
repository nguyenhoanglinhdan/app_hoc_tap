import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext

class ProfileForm(tk.Frame):

    def __init__(self, parents):
        tk.Frame.__init__(self, parents)

        style = ttk.Style()
        style.configure("Blue.TFrame", background="lightblue")

        self.pack(fill="both", expand=True, padx=15, pady=15)
        self.columnconfigure(1, weight=1)

        self.gender_var = tk.StringVar()
        self.terms_var = tk.BooleanVar()

        # First Name
        ttk.Label(self, text="First Name:").grid(row=0, column=0, padx=5, pady=5,
                                                 sticky="w")  # sticky="w" for left-aligned
        self.first_name_entry = ttk.Entry(self)  # Create the entry widget (tien ich)
        self.first_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")  # sticky="ew" for right-aligned

        # Last Name
        ttk.Label(self, text="Last Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.last_name_entry = ttk.Entry(self)
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Gender
        ttk.Label(self, text="Gender:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        gender_frame = ttk.Frame(self, style="Blue.TFrame")
        gender_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(gender_frame, text="Male", variable=self.gender_var, value="Male").pack(side="left")
        ttk.Radiobutton(gender_frame, text="Female", variable=self.gender_var, value="Female").pack(side="left",
                                                                                                    padx=10)
        ttk.Radiobutton(gender_frame, text="Other", variable=self.gender_var, value="Other").pack(side="left")

        # Label
        ttk.Label(self, text="Scrolled text").grid(row=3, column=0, padx=5, pady=5, sticky="nw")

        # ScrolledText
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=40, height=10, font=("Arial", 12))
        self.text_area.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

        self.submit_button = ttk.Button(self, text="Submit", command=self.submit_form)
        self.submit_button.grid(row=4, column=1, padx=5, pady=10, sticky="e")

    def submit_form(self):
        """Callback to retrieve and display form data."""
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        gender = self.gender_var.get()
        text_area = self.text_area.get("1.0", tk.END)  # "1.0" means line 1, character 0 (the start of the text)

        info = (
            f"Submission Successful!\n\n"
            f"Name: {first_name} {last_name}\n"
            f"Gender: {gender}\n"
            f"Text Area: {text_area}\n"
        )  # this is the message
        print(type(info))
        print(info)
        messagebox.showinfo("Profile Information", info)


if __name__ == "__main__":
    root = tk.Tk()  # Create the root window
    root.title("User Profile Form")
    root.geometry("600x600")
    ProfileForm(root)
    root.mainloop()

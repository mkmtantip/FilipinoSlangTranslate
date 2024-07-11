# Import required modules

import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox
from PIL import ImageGrab
import pytesseract
import re
import cv2
import pandas as pd

import nltk
from nltk.corpus import stopwords

import pandas as pd
import nltk
from nltk.corpus import stopwords

def load_slang_dictionary(pronunciation_file_path, definition_file_path, type_file_path):

    # Read the sheets
    pronunciation_df = pd.read_excel(pronunciation_file_path)
    definition_df = pd.read_excel(definition_file_path)
    type_df = pd.read_excel(type_file_path)  # Read the type sheet

    # Combine the dataframes into a single dictionary
    slang_dict = {}
    
    # Process pronunciation dataframe
    for _, row in pronunciation_df.iterrows():
        term = row['Term']
        pronunciation = row['Pronounciation']
        slang_dict[term] = {'Pronunciation': pronunciation}

    # Process definition dataframe
    for _, row in definition_df.iterrows():
        term = row['Term']
        definition = row['Definition']
        if term in slang_dict:
            slang_dict[term]['Definition'] = definition
        else:
            slang_dict[term] = {'Definition': definition}

    # Process type dataframe
    for _, row in type_df.iterrows():
        term = row['Term']
        word_type = row['Type']
        if term in slang_dict:
            slang_dict[term]['Type'] = word_type
        else:
            slang_dict[term] = {'Type': word_type}

    # Check for missing data fields
    for term, data in slang_dict.items():
        if 'Pronunciation' not in data:
            data['Pronunciation'] = 'N/A'
        if 'Definition' not in data:
            data['Definition'] = 'N/A'
        if 'Type' not in data:
            data['Type'] = 'N/A'

    return slang_dict

# Example usage
try:
    # Configure Tesseract OCR
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Joshua\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

    # Load slang dictionary
    pronunciation_file_path = 'Pronounciation1.xlsx'
    definition_file_path = 'Test.xlsx'
    type_file_path = 'Type.xlsx'
    slang_dict = load_slang_dictionary(pronunciation_file_path, definition_file_path, type_file_path)

    # Initialize English words and stopwords
    english_words = set(nltk.corpus.words.words())
    stop_words = set(stopwords.words('english'))

except Exception as e:
    print(f"Error during initialization: {e}")

class DictionaryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.geometry("350x600")
        self.configure(background='#f0f0f0')
        self.position_window()

        # Custom title bar


        # Capture button
        self.capture_button = tk.Button(self, text="Capture Text (Press 'q')", command=self.capture_text, font=("Helvetica", 14), bg='#4CAF50', fg='white')
        self.capture_button.pack(pady=10)

        # Scrollable frame
        self.canvas = tk.Canvas(self, background='#f0f0f0')
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind mousewheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Initialize variables
        self.output = ""

        # Custom fonts
        bold_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        italic_font = tkfont.Font(family="Helvetica", size=10, slant="italic")
        regular_font = tkfont.Font(family="Helvetica", size=10)

        self.fonts = {
            "bold": bold_font,
            "italic": italic_font,
            "regular": regular_font
        }

        # Start keyboard listener
        self.start_keyboard_listener()

    def position_window(self):
        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the position
        x_position = screen_width - 420  # Screen width minus window width
        y_position = 80  # Near the top, adjust as necessary

        # Set the geometry with position
        self.geometry(f"350x600+{x_position}+{y_position}")
    def create_title_bar(self):
        # Add custom title bar and close button
        self.title_bar = tk.Frame(self, bg='#4CAF50', relief='raised', bd=0)
        self.title_bar.pack(side="top", fill="x")
        self.title_label = tk.Label(self.title_bar, text="Dictionary App", bg='#4CAF50', fg='white', font=("Helvetica", 14))
        self.title_label.pack(side="left", padx=10)
        self.close_button = tk.Button(self.title_bar, text="X", command=self.quit, bg='#4CAF50', fg='white', font=("Helvetica", 14), bd=0)
        self.close_button.pack(side="right", padx=10)

        # Make the title bar draggable
        self.title_bar.bind("<B1-Motion>", self.move_window)
        self.title_bar.bind("<Button-1>", self.get_pos)

    # Start keyboard listener for hotkey
    def start_keyboard_listener(self):
        self.bind('<KeyPress-q>', self.capture_text_hotkey)

    # Capture text using hotkey
    def capture_text_hotkey(self, event):
        self.capture_text()

    # Capture text using button
    def capture_text(self):
        self.focus_force()  # Ensure the window is focused
        self.update_idletasks()  # Update the window
        screenshot = ImageGrab.grab()
        screenshot.save("screenshot.png")
        screenshot.close()
        self.process_image()

    # Process captured image
    def process_image(self):
        img = cv2.imread('screenshot.png')
        self.output = pytesseract.image_to_string(img)
        print(f"OCR Output: {self.output}")
        self.tokenizer()

    # Tokenize and process text
    def tokenizer(self):
        unprocessed = re.split(r"[^a-zA-Z]", self.output)
        removeSpace = [ele for ele in unprocessed if ele.strip()]
        processed = [x.lower() for x in removeSpace]
        processed = [
            word for word 
            in processed 
            if word not in stop_words and len(word) > 2 and word not in english_words and self.contains_vowel(word)
        ]
        print(f"Tokenized Words: {processed}")
        self.remove_duplicates(processed)

    # Check if a word contains a vowel
    def contains_vowel(self, word):
        vowels = ['a', 'e', 'i', 'o', 'u']
        for char in word.lower():
            if char in vowels:
                return True
        return False

    # Remove duplicate words
    def remove_duplicates(self, words_list):
        seen = set()
        unique_words_list = []
        for word in words_list:
            if word not in seen:
                seen.add(word)
                unique_words_list.append(word)
        self.filter_by_database(unique_words_list, slang_dict.keys())

    # Filter words by database
    def filter_by_database(self, words_list, database_keys):
        filtered_words = [word for word in words_list if word in database_keys]
        print(f"Filtered Words: {filtered_words}")
        if not filtered_words:
            messagebox.showinfo("No Slang Detected", "No slang words found in the dictionary.")
        else:
            self.display_results(filtered_words)

    # Display filtered words and their definitions

    def display_results(self, filtered_words):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not filtered_words:
            return

        for index, word in enumerate(filtered_words):
            term_label_text = f"{word}"
            pronunciation_label_text = f"{slang_dict[word]['Pronunciation']}"
            definition_label_text = f"{slang_dict[word]['Definition']}"
            type_label_text = f"{slang_dict[word]['Type']}"

            term_label = tk.Message(self.scrollable_frame, text=term_label_text, font=("Helvetica", 16, "bold"), bg='#f0f0f0', width=350, anchor='w', fg='#000000')
            pronunciation_label = tk.Message(self.scrollable_frame, text=pronunciation_label_text, font=("Helvetica", 11, "normal"), bg='#f0f0f0', width=350, anchor='w', fg='#2F2C2C')
            definition_label = tk.Message(self.scrollable_frame, text=definition_label_text, font=("Helvetica", 12, "normal"), bg='#f0f0f0', width=350, anchor='w', fg='#000000')

            # Combine pronunciation and type with appropriate formatting
            combined_label_text = f"{pronunciation_label_text} · {type_label_text}"
            combined_label = tk.Message(self.scrollable_frame, text=combined_label_text, bg='#f0f0f0', width=350, anchor='w', fg='#2F2C2C')

            # Grid layout
            term_label.grid(row=index * 5, column=0, sticky='w', padx=10, pady=(15, 0))
            combined_label.grid(row=index * 5 + 1, column=0, sticky='w', padx=10, pady=(0, 5))
            definition_label.grid(row=index * 5 + 3, column=0, sticky='w', padx=10, pady=(0, 0))

            # Add separator
            separator = ttk.Separator(self.scrollable_frame, orient=tk.HORIZONTAL)
            separator.grid(row=index * 5 + 2, column=0, sticky='ew', padx=15, pady=(0, 5), columnspan=1)

            # Configure separator to cover full width
            self.scrollable_frame.grid_columnconfigure(0, weight=1)


        

    # Handle mousewheel scrolling
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # Get the position for moving the window
    def get_pos(self, event):
        self.xwin = event.x
        self.ywin = event.y

    # Move the window
    def move_window(self, event):
        self.geometry(f'+{event.x_root - self.xwin}+{event.y_root - self.ywin}')

# Run the application
if __name__ == "__main__":
    app = DictionaryApp()
    app.mainloop()

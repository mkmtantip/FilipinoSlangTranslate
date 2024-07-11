import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox
from PIL import ImageGrab
import pytesseract
import re
import cv2
import pandas as pd
import nltk
from nltk.corpus import stopwords

# Download the stopwords from NLTK
nltk.download('stopwords')
nltk.download('words')

def load_slang_dictionary(pronunciation_file_path, definition_file_path, type_file_path):
    
    pronunciation_df = pd.read_excel(pronunciation_file_path)
    definition_df = pd.read_excel(definition_file_path)
    type_df = pd.read_excel(type_file_path)  
    slang_dict = {} # to combine

    # --- Reading and Processing Dataset ---
    for _, row in pronunciation_df.iterrows():
        term = row['Term']
        pronunciation = row['Pronounciation']
        slang_dict.setdefault(term, {}).update({'Pronunciation': pronunciation})

    for _, row in definition_df.iterrows():
        term = row['Term']
        definition = row['Definition']
        slang_dict.setdefault(term, {}).update({'Definition': definition})

    for _, row in type_df.iterrows():
        term = row['Term']
        word_type = row['Type']
        slang_dict.setdefault(term, {}).update({'Type': word_type})

    for term, data in slang_dict.items():
        data.setdefault('Pronunciation', 'N/A')
        data.setdefault('Definition', 'N/A')
        data.setdefault('Type', 'N/A')

    return slang_dict

try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    pronunciation_file_path = 'USPronounciation.xlsx'
    definition_file_path = 'Term.xlsx'
    type_file_path = 'Type.xlsx'
    slang_dict = load_slang_dictionary(pronunciation_file_path, definition_file_path, type_file_path)

    english_words = set(nltk.corpus.words.words())
    stop_words = set(stopwords.words('english'))

except Exception as e:
    print(f"Error during initialization: {e}")

class DictionaryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        
        self.geometry("360x600")
        self.configure(background='#f0f0f0')
        self.position_window()
        self.create_title_bar()

        self.capture_button = tk.Button(self, text="Start detection", command=self.capture_text, font=("Helvetica", 14), bg='#3498DB', fg='white')
        self.capture_button.pack(side="bottom", pady=10)

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

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        self.output = ""

        # --- FONTS ---
        bold_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        italic_font = tkfont.Font(family="Helvetica", size=10, slant="italic")
        regular_font = tkfont.Font(family="Helvetica", size=10)

        self.fonts = {
            "bold": bold_font,
            "italic": italic_font,
            "regular": regular_font
        }

        self.start_keyboard_listener()
        

    def position_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = screen_width - 420  
        y_position = 80

        self.geometry(f"350x600+{x_position}+{y_position}")

    def create_title_bar(self):
        self.title_bar = tk.Frame(self, bg='#3498DB', relief='raised', bd=0)
        self.title_bar.pack(side="top", fill="x")
        self.title_label = tk.Label(self.title_bar, text="Colloquials", bg='#3498DB', fg='white', font=("Helvetica", 12))
        self.title_label.pack(side="left", padx=10)

        self.title_bar.bind("<B1-Motion>", self.move_window)
        self.title_bar.bind("<Button-1>", self.get_pos)

    def start_keyboard_listener(self):
        self.bind('<KeyPress-q>', self.capture_text_hotkey)

    def capture_text_hotkey(self, event):
        self.capture_text()

    def capture_text(self):
        self.focus_force()  
        self.update_idletasks()  
        screenshot = ImageGrab.grab()
        screenshot.save("capture.png")
        screenshot.close()
        self.process_image()

    def process_image(self):
        img = cv2.imread('capture.png')
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
            if word not in stop_words and len(word) > 2  
        ]
        print(f"Tokenized Words: {processed}")
        self.remove_duplicates(processed)

    def remove_duplicates(self, words_list):
        seen = set()
        unique_words_list = []
        for word in words_list:
            if word not in seen:
                seen.add(word)
                unique_words_list.append(word)
        self.filter_by_database(unique_words_list, slang_dict.keys())

    def filter_by_database(self, words_list, database_keys):
        filtered_words = [word for word in words_list if word in database_keys]
        print(f"Filtered Words: {filtered_words}")
        if not filtered_words:
            self.display_no_slang_message()
        else:
            self.display_results(filtered_words)

    def display_results(self, filtered_words):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not filtered_words:
            self.display_no_slang_message()
            return

        for index, word in enumerate(filtered_words):
            term_label_text = f"{word}"
            pronunciation_label_text = f"{slang_dict[word]['Pronunciation']}"
            definition_label_text = f"{slang_dict[word]['Definition']}"
            type_label_text = f"{slang_dict[word]['Type']}"

            term_label = tk.Message(self.scrollable_frame, text=term_label_text, font=("Helvetica", 16, "bold"), bg='#f0f0f0', width=340, anchor='w', fg='#3498DB')
            pronunciation_label = tk.Message(self.scrollable_frame, text=pronunciation_label_text, font=("Helvetica", 11, "normal"), bg='#3498DB', width=340, anchor='w', fg='#3498DB')
            definition_label = tk.Message(self.scrollable_frame, text=definition_label_text, font=("Helvetica", 10, "normal"), bg='#f0f0f0', width=340, anchor='w', fg='#000000')

            combined_label_text = f"{pronunciation_label_text} · {type_label_text}"
            combined_label = tk.Message(self.scrollable_frame, text=combined_label_text, bg='#f0f0f0', width=350, anchor='w', fg='#2F2C2C')

            term_label.grid(row=index * 5, column=0, sticky='w', padx=10, pady=(15, 0))
            combined_label.grid(row=index * 5 + 1, column=0, sticky='w', padx=10, pady=(0, 5))
            definition_label.grid(row=index * 5 + 3, column=0, sticky='w', padx=10, pady=(0, 0))

            separator = ttk.Separator(self.scrollable_frame, orient=tk.HORIZONTAL)
            separator.grid(row=index * 5 + 2, column=0, sticky='ew', padx=15, pady=(0, 5), columnspan=1)

            self.scrollable_frame.grid_columnconfigure(0, weight=1)

    
    def display_no_slang_message(self):
            no_slang_label = tk.Label(self.scrollable_frame, text="No slang words found in the dictionary.", font=("Helvetica", 11), bg='#f0f0f0', fg='#FF5733')
            no_slang_label.grid(row=0, column=0, padx=10, pady=10)
            
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def get_pos(self, event):
        self.xwin = event.x
        self.ywin = event.y

    def move_window(self, event):
        self.geometry(f'+{event.x_root - self.xwin}+{event.y_root - self.ywin}')

if __name__ == "__main__":
    app = DictionaryApp()
    app.mainloop()

import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox
from PIL import ImageGrab
import pytesseract
import re
import cv2
from pandas import ExcelFile
from nltk.corpus import stopwords
import nltk

try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # ------------ DATASETS --------------
    xls = ExcelFile('Test.xlsx')
    df = xls.parse(xls.sheet_names[0])
    database = df.set_index(df.columns[0]).to_dict()[df.columns[1]]

    xls2 = ExcelFile('Pronounciation1.xlsx')
    df2 = xls2.parse(xls2.sheet_names[0])
    database2 = df2.set_index(df2.columns[0]).to_dict()[df2.columns[1]]

    
    english_words = set(nltk.corpus.words.words())
    stop_words = set(stopwords.words('english'))

except Exception as e:
    print(f"Error during initialization: {e}")

class DictionaryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # ---------------- MORE ON FRAME DESIGN ---------------------------
        
        self.overrideredirect(True)  # Remove the default title bar
        self.geometry("430x600")  # Adjusted frame size
        self.configure(background='#f0f0f0')  # Set background color

        # green title bar, change to pref
        self.title_bar = tk.Frame(self, bg='#4CAF50', relief='raised', bd=0)
        self.title_bar.pack(side="top", fill="x")
        self.title_label = tk.Label(self.title_bar, text="Dictionary App", bg='#4CAF50', fg='white', font=("Helvetica", 14))
        self.title_label.pack(side="left", padx=10)
        self.close_button = tk.Button(self.title_bar, text="X", command=self.quit, bg='#4CAF50', fg='white', font=("Helvetica", 14), bd=0)
        self.close_button.pack(side="right", padx=10)

        # title bar = draggable
        self.title_bar.bind("<B1-Motion>", self.move_window)
        self.title_bar.bind("<Button-1>", self.get_pos)

        # Button for screenshot (first frame)
        self.capture_button = tk.Button(self, text="Capture Text (Press 'q')", command=self.capture_text, font=("Helvetica", 14), bg='#4CAF50', fg='white')
        self.capture_button.pack(pady=10)

        # frame with scrollbar
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

        # ---------- Controls scroll function -----------------
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # For Linux systems
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # For Linux systems

        # Initialize variables
        self.output = ""

        # -------------- Custom Fonts ----------------------
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
    
    # ------------- DEFINING FUNCTIONS -----------------------

    def start_keyboard_listener(self):
        self.bind('<KeyPress-q>', self.capture_text_hotkey)

    def capture_text_hotkey(self, event):
        screenshot = ImageGrab.grab()
        screenshot.save("screenshot.png")
        screenshot.close()
        self.process_image()

    def capture_text(self):
        screenshot = ImageGrab.grab()
        screenshot.save("screenshot.png")
        screenshot.close()
        self.process_image()

    def process_image(self):
        img = cv2.imread('screenshot.png')
        self.output = pytesseract.image_to_string(img)
        self.tokenizer()

    def tokenizer(self):
        unprocessed = re.split(r"[^a-zA-Z]", self.output)
        removeSpace = [ele for ele in unprocessed if ele.strip()]
        processed = [x.lower() for x in removeSpace]
        processed = [
            word for word 
            in processed 
            if word not in stop_words and len(word) > 2 and word not in english_words and self.contains_vowel(word)
        ]
        self.remove_duplicates(processed)

    def contains_vowel(self, word):
        vowels = ['a', 'e', 'i', 'o', 'u']
        for char in word.lower():
            if char in vowels:
                return True
        return False

    def remove_duplicates(self, words_list):
        seen = set()
        unique_words_list = []
        for word in words_list:
            if word not in seen:
                seen.add(word)
                unique_words_list.append(word)
        self.filter_by_database(unique_words_list, database.keys())

    def filter_by_database(self, words_list, database_keys):
        filtered_words = [word for word in words_list if word in database_keys]
        if not filtered_words:
            messagebox.showinfo("No Slang Detected", "No slang words found in the dictionary.")
        else:
            self.display_results(filtered_words)

    def display_results(self, filtered_words):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not filtered_words:
            return
        
        for word in filtered_words:
            term_label_text = f"{word}"
            pronunciation_label_text = f"{database2.get(word, 'N/A')}"
            definition_label_text = f"{database[word]}"

            term_label = tk.Message(self.scrollable_frame, text=term_label_text, font=self.fonts["bold"], bg='#f0f0f0', width=350, anchor='w')
            pronunciation_label = tk.Message(self.scrollable_frame, text=pronunciation_label_text, font=self.fonts["italic"], bg='#f0f0f0', width=350, anchor='w')
            definition_label = tk.Message(self.scrollable_frame, text=definition_label_text, font=self.fonts["regular"], bg='#f0f0f0', width=350, anchor='w')
            
            # you can manipulate sequence below (term > pronunciation > separator (line) > definition)

            term_label.pack(side='top', padx=10, pady=(5, 0), fill='x')
            pronunciation_label.pack(side='top', padx=10, pady=2, fill='x')

            separator = ttk.Separator(self.scrollable_frame, orient='horizontal')
            separator.pack(side='top', fill='x', padx=10, pady=0, ipady=0)  # if need more spaces in containers, dito imanipulate

            definition_label.pack(side='top', padx=10, pady=(0, 5), fill='x')
            
            

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def get_pos(self, event):
        self.xwin = event.x
        self.ywin = event.y

    def move_window(self, event):
        self.geometry(f'+{event.x_root - self.xwin}+{event.y_root - self.ywin}')

if __name__ == "__main__":
    app = DictionaryApp()
    app.mainloop()
    
    
    
    
#  ------------------ REFERENCE CODE --------------------------

# import tkinter as tk
# from tkinter import ttk, font as tkfont  # Import tkinter font module as tkfont
# from PIL import ImageGrab
# import pytesseract
# import re
# import cv2
# from pandas import ExcelFile
# from Levenshtein import distance
# from nltk.corpus import stopwords
# import nltk

# try:
#     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#     # Excel database to dict
#     xls = ExcelFile('Test.xlsx')
#     df = xls.parse(xls.sheet_names[0])
#     database = df.set_index(df.columns[0]).to_dict()[df.columns[1]]

#     xls2 = ExcelFile('Pronounciation1.xlsx')
#     df2 = xls2.parse(xls2.sheet_names[0])
#     database2 = df2.set_index(df2.columns[0]).to_dict()[df2.columns[1]]

#     # Set of English words
#     english_words = set(nltk.corpus.words.words())

#     # List of stop words
#     stop_words = set(stopwords.words('english'))

# except Exception as e:
#     print(f"Error during initialization: {e}")

# class DictionaryApp(tk.Tk):
#     def __init__(self):
#         super().__init__()

#         self.overrideredirect(True)  # Remove the default title bar
#         self.geometry("430x600")  # Adjusted frame size
#         self.configure(background='#f0f0f0')  # Set background color

#         # Custom title bar
#         self.title_bar = tk.Frame(self, bg='#4CAF50', relief='raised', bd=0)
#         self.title_bar.pack(side="top", fill="x")
#         self.title_label = tk.Label(self.title_bar, text="Dictionary App", bg='#4CAF50', fg='white', font=("Helvetica", 14))
#         self.title_label.pack(side="left", padx=10)
#         self.close_button = tk.Button(self.title_bar, text="X", command=self.quit, bg='#4CAF50', fg='white', font=("Helvetica", 14), bd=0)
#         self.close_button.pack(side="right", padx=10)

#         # Make the title bar draggable
#         self.title_bar.bind("<B1-Motion>", self.move_window)
#         self.title_bar.bind("<Button-1>", self.get_pos)

#         # Button to capture screenshot
#         self.capture_button = tk.Button(self, text="Capture Text (Press 'q')", command=self.capture_text, font=("Helvetica", 14), bg='#4CAF50', fg='white')
#         self.capture_button.pack(pady=10)

#         # Create a canvas and a scrollbar
#         self.canvas = tk.Canvas(self, background='#f0f0f0')
#         self.scrollable_frame = ttk.Frame(self.canvas)

#         self.scrollable_frame.bind(
#             "<Configure>",
#             lambda e: self.canvas.configure(
#                 scrollregion=self.canvas.bbox("all")
#             )
#         )

#         self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
#         self.canvas.pack(side="left", fill="both", expand=True)

#         # Bind mousewheel to scroll
#         self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
#         self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # For Linux systems
#         self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # For Linux systems

#         # Initialize variables
#         self.output = ""

#         # Custom font settings
#         bold_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
#         italic_font = tkfont.Font(family="Helvetica", size=10, slant="italic")
#         regular_font = tkfont.Font(family="Helvetica", size=10)

#         self.fonts = {
#             "bold": bold_font,
#             "italic": italic_font,
#             "regular": regular_font
#         }

#         # Start keyboard listener
#         self.start_keyboard_listener()

#     def start_keyboard_listener(self):
#         self.bind('<KeyPress-q>', self.capture_text_hotkey)

#     def capture_text_hotkey(self, event):
#         screenshot = ImageGrab.grab()
#         screenshot.save("screenshot.png")
#         screenshot.close()
#         self.process_image()

#     def capture_text(self):
#         screenshot = ImageGrab.grab()
#         screenshot.save("screenshot.png")
#         screenshot.close()
#         self.process_image()

#     def process_image(self):
#         img = cv2.imread('screenshot.png')
#         self.output = pytesseract.image_to_string(img)
#         self.tokenizer()

#     def tokenizer(self):
#         unprocessed = re.split(r"[^a-zA-Z]", self.output)
#         removeSpace = [ele for ele in unprocessed if ele.strip()]
#         processed = [x.lower() for x in removeSpace]
#         processed = [
#             word for word 
#             in processed 
#             if word not in stop_words and len(word) > 2 and word not in english_words and self.contains_vowel(word)
#         ]
#         self.remove_duplicates(processed)

#     def contains_vowel(self, word):
#         vowels = ['a', 'e', 'i', 'o', 'u']
#         for char in word.lower():
#             if char in vowels:
#                 return True
#         return False

#     def remove_duplicates(self, words_list):
#         seen = set()
#         unique_words_list = []
#         for word in words_list:
#             if word not in seen:
#                 seen.add(word)
#                 unique_words_list.append(word)
#         self.filter_by_database(unique_words_list, database.keys())

#     def filter_by_database(self, words_list, database_keys):
#         corrected_words = [self.autocorrect(word, database_keys) for word in words_list]
#         filtered_words = [word for word in corrected_words if word in database_keys]
#         self.display_results(filtered_words)

#     def autocorrect(self, word, dictionary_keys, max_distance=2):
#         min_distance = float('inf')
#         closest_match = word
#         for key in dictionary_keys:
#             dist = distance(word, key)
#             if dist < min_distance:
#                 min_distance = dist
#                 closest_match = key
#         if min_distance <= max_distance:
#             return closest_match
#         else:
#             return word

#     def display_results(self, corrected_words):
#         for widget in self.scrollable_frame.winfo_children():
#             widget.destroy()
        
#         for word in corrected_words:
#             if word in database:
#                 term_label_text = f"{word}"
#                 pronunciation_label_text = f"{database2.get(word, 'N/A')}"
#                 definition_label_text = f"{database[word]}"

#                 term_label = tk.Message(self.scrollable_frame, text=term_label_text, font=self.fonts["bold"], bg='#f0f0f0', width=350, anchor='w')
#                 pronunciation_label = tk.Message(self.scrollable_frame, text=pronunciation_label_text, font=self.fonts["italic"], bg='#f0f0f0', width=350, anchor='w')
#                 definition_label = tk.Message(self.scrollable_frame, text=definition_label_text, font=self.fonts["regular"], bg='#f0f0f0', width=350, anchor='w')

#                 term_label.pack(side='top', padx=10, pady=(5, 0), fill='x')
#                 pronunciation_label.pack(side='top', padx=10, pady=2, fill='x')

#                 separator = ttk.Separator(self.scrollable_frame, orient='horizontal')
#                 separator.pack(side='top', fill='x', padx=10, pady=0, ipady=0)  # Adjust padx to align with labels

#                 definition_label.pack(side='top', padx=10, pady=(0, 5), fill='x')

#     def _on_mousewheel(self, event):
#         if event.num == 4 or event.delta > 0:
#             self.canvas.yview_scroll(-1, "units")
#         elif event.num == 5 or event.delta < 0:
#             self.canvas.yview_scroll(1, "units")

#     def get_pos(self, event):
#         self.xwin = event.x
#         self.ywin = event.y

#     def move_window(self, event):
#         self.geometry(f'+{event.x_root - self.xwin}+{event.y_root - self.ywin}')

# if __name__ == "__main__":
#     app = DictionaryApp()
#     app.mainloop()

import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, ImageTk, Image
import pytesseract
import cv2
import pandas as pd
from nltk.corpus import stopwords
import re
import keyboard

# Set the path to tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load stop words
stop_words = set(stopwords.words('english'))

# Load databases
xls = pd.ExcelFile('Test.xlsx')
df = xls.parse(xls.sheet_names[0])
database = df.set_index(df.columns[0]).to_dict()[df.columns[1]]

xls2 = pd.ExcelFile('Pronounciation.xlsx')
df2 = xls2.parse(xls2.sheet_names[0])
database2 = df2.set_index(df2.columns[0]).to_dict()[df2.columns[1]]

def capture_and_process():
    # Capture screenshot
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.png")
    
    # Process image
    img = cv2.imread('screenshot.png')
    extractedString = pytesseract.image_to_string(img)
    unprocessed = re.split(r"[^a-zA-Z]", extractedString)
    removeSwords = [w for w in unprocessed if not w.lower() in stop_words]
    removeSpace = [ele for ele in removeSwords if ele.strip()]
    processed = [x.lower() for x in removeSpace]
    
    # Display terms, definitions, and pronunciations
    output_text.delete(1.0, tk.END)  # Clear previous text
    for key, value in database.items():
        if key in processed:
            output_text.insert(tk.END, f"Term: {key}\nDefinition: {database[key]}\nPronounciation: {database2[key]}\n\n")

def create_gui():
    global output_text
    
    # Create main window
    root = tk.Tk()
    root.title("Screenshot Dictionary")
    root.geometry("600x400")
    
    # Button to capture screenshot and process
    capture_button = tk.Button(root, text="Capture Screenshot", command=capture_and_process)
    capture_button.pack(pady=20)
    
    # Text area to display terms, definitions, and pronunciations
    output_text = tk.Text(root, wrap=tk.WORD)
    output_text.pack(expand=True, fill=tk.BOTH)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PIL import ImageGrab
import pytesseract
import re
import cv2
import pandas as pd
import os
import nltk
from nltk.corpus import stopwords

class DictionaryApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('dictUI.ui', self)
        self.setWindowTitle("Colloquials")
        self.capture_button.clicked.connect(self.capture_text)
        self.back_button.clicked.connect(self.go_back_to_page1)
        self.explore_button.clicked.connect(self.go_to_page3)
        self.sort_button.clicked.connect(self.sort_contents)
        self.search_button.clicked.connect(self.search_term)
        self.back_button2.clicked.connect(self.back_to_page1)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.viewport().installEventFilter(self)

        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            self.slang_dict = self.load_slang_dictionary('USPronounciation.xlsx', 'Term.xlsx', 'Type.xlsx')
            self.stop_words = set(stopwords.words('english'))
            self.unsorted_slang_dict = self.slang_dict.copy()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error during initialization: {e}")

    def load_slang_dictionary(self, pronunciation_file_path, definition_file_path, type_file_path):
        pronunciation_df = pd.read_excel(pronunciation_file_path)
        definition_df = pd.read_excel(definition_file_path)
        type_df = pd.read_excel(type_file_path)
        slang_dict = {}

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

    def capture_text(self):
        try:
            screenshot = ImageGrab.grab()
            screenshot.save("capture.png")
            screenshot.close()
            self.process_image()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to capture screenshot: {e}")

    def process_image(self):
        try:
            img = cv2.imread('capture.png')
            self.output = pytesseract.image_to_string(img)
            os.remove('capture.png')
            self.tokenizer()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to process image: {e}")

    def tokenizer(self):
        unprocessed = re.split(r"[^a-zA-Z]", self.output)
        removeSpace = [ele for ele in unprocessed if ele.strip()]
        processed = [x.lower() for x in removeSpace]
        processed = [word for word in processed if word not in self.stop_words and len(word) > 2]
        self.remove_duplicates(processed)

    def remove_duplicates(self, words_list):
        seen = set()
        unique_words_list = []
        for word in words_list:
            if word not in seen:
                seen.add(word)
                unique_words_list.append(word)
        self.filter_by_database(unique_words_list, self.slang_dict.keys())

    def filter_by_database(self, words_list, database_keys):
        filtered_words = [word for word in words_list if word in database_keys]
        if not filtered_words:
            self.display_no_slang_message()
        else:
            self.display_results(filtered_words)

    def display_results(self, filtered_words):
        self.stackedWidget.setCurrentIndex(1) 

        results_text = ""
        for word in filtered_words:
            data = self.slang_dict[word]
            results_text += self.format_slang_term(word, data)

        self.results_label.setText(results_text)

    def display_no_slang_message(self):
        self.stackedWidget.setCurrentIndex(1)
        self.results_label.setText("No slang words found in the dictionary.")

    def go_to_page3(self):
        self.stackedWidget.setCurrentIndex(2)
        self.populate_all_contents() 
        
    def populate_all_contents(self):
        content_text = ""
        for term, data in self.slang_dict.items():
            content_text += self.format_slang_term(term, data)
        self.all_contents.setText(content_text)

    def sort_contents(self):
        sorted_terms = sorted(self.slang_dict.keys())
        content_text = ""
        for term in sorted_terms:
            data = self.slang_dict[term]
            content_text += self.format_slang_term(term, data)
        self.all_contents.setText(content_text)

    def search_term(self):
        search_word = self.search_text.toPlainText().strip().lower()
        if search_word in self.slang_dict:
            term_data = self.slang_dict[search_word]
            content_text = self.format_slang_term(search_word, term_data)
            self.all_contents.setText(content_text)
        else:
            self.all_contents.setText(f"No results found for '{search_word}'")

    def go_back_to_page1(self):
        self.stackedWidget.setCurrentIndex(0)  

    def back_to_page1(self):
        if self.stackedWidget.currentIndex() == 2:  
            self.stackedWidget.setCurrentIndex(0)  
            self.populate_all_contents()  

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Wheel and source is self.scrollArea.viewport():
            delta = event.angleDelta().y()
            scrollBar = self.scrollArea.verticalScrollBar()
            scrollBar.setValue(scrollBar.value() - delta)
            return True
        return super().eventFilter(source, event)

    def format_slang_term(self, term, data):
        pronunciation = data['Pronunciation']
        definition = data['Definition']
        word_type = data['Type']
        combined_label_text = f"{pronunciation} · {word_type}"
        
        formatted_text = f"""
            <p style="font-size: 16px; font-weight: bold; color: #5EA563; line-height: 0.3">{term}</p>
            <p style="font-size: 11px; line-height: 0.5">{combined_label_text}</p>
            <hr style="border: none; line-height: 0.5; border-top: 1px solid #CFCFCF;">
            <p style="font-size: 14px;">{definition}</p>
            <br>
        """
        return formatted_text


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DictionaryApp()
    window.show()
    sys.exit(app.exec_())
    
    # pushhh

from PIL import ImageGrab
import keyboard
import pytesseract
import re
import cv2
from pandas import ExcelFile
from Levenshtein import distance
from nltk.corpus import stopwords
import nltk

# Download the stopwords from NLTK
nltk.download('stopwords')
nltk.download('words')

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Excel database to dict
xls = ExcelFile('Test.xlsx')
df = xls.parse(xls.sheet_names[0])
database = df.set_index(df.columns[0]).to_dict()[df.columns[1]]

xls2 = ExcelFile('Pronounciation.xlsx')
df2 = xls2.parse(xls2.sheet_names[0])
database2 = df2.set_index(df2.columns[0]).to_dict()[df2.columns[1]]

# Set of English words
english_words = set(nltk.corpus.words.words())

# List of stop words
stop_words = set(stopwords.words('english'))

def imageText():
    img = cv2.imread('screenshot.png')
    global output
    output = pytesseract.image_to_string(img)
    tokenizer()

def tokenizer():
    global processed
    unprocessed = re.split(r"[^a-zA-Z]", output)
    removeSpace = [ele for ele in unprocessed if ele.strip()]
    processed = [x.lower() for x in removeSpace]

    # Remove stop words, single letters, two-letter words, English words, and non-vowel words
    processed = [
        word for word in processed 
        if word not in stop_words and len(word) > 2 and word not in english_words and contains_vowel(word)
    ]
    
    print("Processed words:", processed)
    remove_duplicates(processed)

def contains_vowel(word):
    vowels = ['a', 'e', 'i', 'o', 'u']
    for char in word.lower():
        if char in vowels:
            return True
    return False

def remove_duplicates(words_list):
    seen = set()
    unique_words_list = []
    for word in words_list:
        if word not in seen:
            seen.add(word)
            unique_words_list.append(word)
    
    print("Unique words:", unique_words_list)
    filter_by_database(unique_words_list, database.keys())


def filter_by_database(words_list, database_keys):
    filtered_words = [word for word in words_list if word in database_keys]
    print("Filtered words by database:", filtered_words)
    compare(filtered_words)

def autocorrect(word, dictionary_keys, max_distance=2):
    min_distance = float('inf')
    closest_match = word
    for key in dictionary_keys:
        dist = distance(word, key)
        if dist < min_distance:
            min_distance = dist
            closest_match = key
    if min_distance <= max_distance:
        return closest_match
    else:
        return word

def compare(corrected_words):
    corrected = [autocorrect(word, database.keys()) for word in corrected_words]
    print("Corrected words:", corrected)
    for word in corrected:
        if word in database:
            print("Term:", word, "Definition:", database[word], "Pronunciation:", database2.get(word, "N/A"))

while True:
    try:
        if keyboard.is_pressed('q'):
            screenshot = ImageGrab.grab()
            screenshot.save("screenshot.png")
            screenshot.close()
            imageText()
            break
    except:
        break

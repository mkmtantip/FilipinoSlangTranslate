from PIL import ImageGrab
import keyboard
import pytesseract
import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import cv2
from pandas import *
from Levenshtein import distance


#Excel database to dict 
xls = ExcelFile('Test.xlsx')
df = xls.parse(xls.sheet_names[0])
database = df.set_index(df.columns[0]).to_dict()[df.columns[1]]

xls2 = ExcelFile('Pronounciation.xlsx')
df2 = xls2.parse(xls2.sheet_names[0])
database2 = df2.set_index(df2.columns[0]).to_dict()[df2.columns[1]]

            
def imageText():
    img = cv2.imread('screenshot.png')
    global output
    output = pytesseract.image_to_string(img)
    tokenizer()
        
def tokenizer():
    global processed
    unprocessed = re.split(r"[^a-zA-Z]", output) #just splits into spaces 
    removeSpace = [ele for ele in unprocessed if ele.strip()] #removes spaces
    processed = [x.lower() for x in removeSpace]
    print(processed)
    compare()
    
def compare():
    for key, value in database.items():
        if key in processed:
            print("Term:", key,"Definition:", database[key],"Pronounciation: ", database2[key])
            
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
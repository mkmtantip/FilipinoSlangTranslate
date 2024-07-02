from PIL import ImageGrab
import keyboard
import pytesseract
import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import cv2
from pandas import *

#Excel database to dict 
xls = ExcelFile('Test.xlsx')
df = xls.parse(xls.sheet_names[0])
database = df.to_dict()            
            
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

#kailangan ng smth autocorrect 
#compared and outputs
def compare():
    # sum(database[key] if key in database else 0 for key in database)
    for key, value in database.items():
        if key in processed:
            print(key, value)

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
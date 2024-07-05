from PIL import ImageGrab
import keyboard
import pytesseract
import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import cv2
from pandas import *
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))
#Excel database to dict 
xls = ExcelFile('Test.xlsx')
df = xls.parse(xls.sheet_names[0])
database = df.set_index(df.columns[0]).to_dict()[df.columns[1]]

xls2 = ExcelFile('Pronounciation.xlsx')
df2 = xls2.parse(xls2.sheet_names[0])
database2 = df2.set_index(df2.columns[0]).to_dict()[df2.columns[1]]
2

def function(finalOutput): 
    img = cv2.imread('screenshot.png')
    extractedString = pytesseract.image_to_string(img)
    unprocessed = re.split(r"[^a-zA-Z]", extractedString) #just splits into spaces 
    removeSwords = [w for w in unprocessed if not w.lower() in stop_words] #removes stop words
    removeSpace = [ele for ele in removeSwords if ele.strip()] #removes spaces
    processed = [x.lower() for x in removeSpace]
    print(processed)
    
    for key, value in database.items():
        if key in processed:
            finalOutput = print("Term:", key,"Definition:", database[key],"Pronounciation: ", database2[key])
    
    return finalOutput
    

while True:
    try:
        if keyboard.is_pressed('1'):
            screenshot = ImageGrab.grab() #dito kayo maglagay ng snipping function sa ImageGrab.grab() kapag may nahanap kayo 
            screenshot.save("screenshot.png")
            function(screenshot)
        elif keyboard.is_pressed('2'):
            screenshot.close()
            break
    except:
        break
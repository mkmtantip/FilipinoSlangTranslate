import re
import nltk
from nltk.corpus import stopwords
# def clean_text(text):
#     # Pattern to match symbols, two-letter words, and singular letter words
#     pattern = r'\W+|\b\w{1,2}\b'
    
#     # Replace matched patterns with an empty string
#     cleaned_text = re.sub(pattern, '', text)
    
#     return cleaned_text

stop_words = set(stopwords.words('english'))

# def removeDigits(text):
#     pattern = '\w*\d\w*'
#     cleaned_text = re.sub(pattern, '', text)
#     return cleaned_text

def tokenizer(text):
    # global processed
    # removed = removeDigits(original_text)
    # print(removed)
    unprocessed = re.split(r'[^a-zA-Z]', original_text) #just splits into spaces 
    print(unprocessed)
    removeSwords = [w for w in unprocessed if w is not None and not w.lower() in stop_words] #removes stop words
    removeSpace = [ele for ele in removeSwords if ele.strip()] #removes spaces
    processed = [x.lower() for x in removeSpace]
    print(processed)
    return processed

# Example usage
original_text = "Hello, World! It's a beautiful day. A quick brown fox jumps over the lazy dog. Nh Nh3213 Slayx22 nhkjkkkk fb ffs Slayyyyyy"
test = tokenizer(original_text)
print(test)


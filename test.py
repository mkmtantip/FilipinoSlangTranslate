import re

target_string = "My name is maximum$#$#$#4 and my luck numbers are 12 45 78"
# split on white-space 
word_list = re.split(r"[^a-zA-Z]", target_string)
word_list_stripped = [ele for ele in word_list if ele.strip()]
print(word_list_stripped)
word_list_lowered = [x.lower() for x in word_list_stripped]
print(word_list_lowered)

# Output ['My', 'name', 'is', 'maximums', 'and', 'my', 'luck', 'numbers', 'are', '12', '45', '78']

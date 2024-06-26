import pandas as pd

xls = pd.ExcelFile('Test.xlsx') #dataset goes here
test = xls.parse(xls.sheet_names[0]) 
print(test.to_dict())



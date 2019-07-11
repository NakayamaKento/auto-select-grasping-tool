import csv
# https://qiita.com/motoki1990/items/0274d8bcf1a97fe4a869

csvname = 'test.csv'
path = './../csv/' + csvname

csv_file = open(path, "r", encoding="utf_8-sig", errors="", newline="" )
f = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)	#リスト形式

header = next(f)
print(header)
for row in f:
    #rowはList
    #row[0]で必要な項目を取得することができる
    print(row)

#git test


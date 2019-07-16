import pprint
import csv
# https://qiita.com/motoki1990/items/0274d8bcf1a97fe4a869

####### 設計パラメータ取得 #######

	####### 保存形式 ##################
	# ['No', 'Name ', 'Fitted shapes', 'Open width', 'Min finger length', 'Slant median', 'Curvature radius median']
	###################################

csvname = 'median.csv'	#読み込むファイルごとに変更
path = './../csv/' + csvname

csv_file = open(path, "r", encoding="utf_8-sig", errors="", newline="" )
f = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)	#リスト形式

###################################
two_finger_slant = []
two_finger_curv = []
three_finger = []

header = next(f)
#print(header)
##### 2指か3指か、傾斜か曲率かを識別し、別々に格納 ##########
for row in f:
    #rowはList
    #row[0]で必要な項目を取得することができる
	#print(row)
	if row[2] == "box":
		if row[5] != "N/A":
			two_finger_slant.append(row)
		else:
			two_finger_curv.append(row)
	else:	
		three_finger.append(row)

###### 2指の傾斜について、総当たりで使えるやつを探す 
###### まずは結果を格納するリストを作成
grasping_tool_two_slant = []
stroke_two = 48 ### SMCの2指ハンド
phy = 5


for index_tool, tool in enumerate(two_finger_slant):
	test = []
	for index_part, part in enumerate(two_finger_slant):
		if float(tool[3]) - stroke_two/2 < float(part[3]) and float(tool[3]) + stroke_two/2 > float(part[3]):
			if float(tool[4]) > float(part[4])/2:
				if float(tool[5]) - phy < float(part[5]) and float(tool[5]) + phy > float(part[5]):
					test.append(True)
					continue
		test.append( False)
	grasping_tool_two_slant.append(test)

pprint.pprint(two_finger_slant)
pprint.pprint( grasping_tool_two_slant)

###### 2指の曲率について、総当たりを考える
grasping_tool_two_curv = []
curv = 5

for index_tool, tool in enumerate(two_finger_curv):
	test = []
	for index_part, part in enumerate(two_finger_curv):
		if float(tool[3]) - stroke_two/2 < float(part[3]) and float(tool[3]) + stroke_two/2 > float(part[3]):
			if float(tool[4]) > float(part[4])/2:
				if float(tool[6]) - curv < float(part[6]) and float(tool[6]) + curv > float(part[6]):
					test.append(True)
					continue
		test.append( False)
	grasping_tool_two_curv.append(test)

pprint.pprint(two_finger_curv)
pprint.pprint(grasping_tool_two_curv)

###### 3指について、総当たりを考える
grasping_tool_three = []
stroke_three = 8

for index_tool, tool in enumerate(three_finger):
	test = []
	for index_part, part in enumerate(three_finger):
		if float(tool[3]) - stroke_three/2 < float(part[3]) and float(tool[3]) + stroke_three/2 > float(part[3]):
			if float(tool[4]) > float(part[4])/2:
				test.append(True)
				continue
		test.append( False)
	grasping_tool_three.append(test)

pprint.pprint(three_finger)
pprint.pprint(grasping_tool_three)


#print("two_finger_slant")
#print(two_finger_slant)
#print("two_finger_curv")
#print(two_finger_curv)
#print("three finger")
#print(three_finger)

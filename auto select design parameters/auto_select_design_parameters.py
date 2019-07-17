import pprint
import csv
import copy
# https://qiita.com/motoki1990/items/0274d8bcf1a97fe4a869

### 最小の組み合わせを確認する関数 ###
def Check_min_combnation(grasping_tool):
	return Check(grasping_tool, 0)

def Check(grasping_tool, index):
	if len(grasping_tool) <= index:
		return 0
	check_list = [False] * len(grasping_tool[0])
	tool_list = copy.deepcopy(grasping_tool)
	del tool_list[index]
		
	for tool_index, tool in enumerate(tool_list):
		for part_index, part in enumerate(check_list):
			if part_index == 0:
				check_list[part_index] = True
				continue
			if tool_list[tool_index][part_index] == True:
				check_list[part_index] = True
	for item in check_list:
		if item == False:
			index += 1
			return Check(grasping_tool, index)

	del grasping_tool[index]
	return Check(grasping_tool, index)



####### 設計パラメータ取得 #######

	####### 保存形式 ##################
	# ['No', 'Name ', 'Fitted shapes', 'Open width', 'Min finger length', 'Slant median', 'Curvature radius median']
	###################################

csvname = 'median.csv'	#読み込むファイルごとに変更
path = './../csv/' + csvname	#相対パスで記述

csv_file = open(path, "r", encoding="utf_8-sig", errors="", newline="" )
f = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)	#読み込み方 -> リスト形式

###################################
###### 2指か3指か、傾斜か曲率かを識別し、別々に格納 ##########
two_finger_slant = []
two_finger_curv = []
three_finger = []

header = next(f)
print(header)
for row in f:
    #rowはList
    #row[0]で必要な項目を取得することができる
	#print(row)
	if row[2] == "box":	#選択した図形が直方体か円柱か
		if row[5] != "N/A":	#傾斜パラメータ（slant）に値があるかどうか
			two_finger_slant.append(row)
		else:
			two_finger_curv.append(row)
	else:	
		three_finger.append(row)

###### 2指の傾斜について、総当たりで使えるやつを探す 
###### まずは結果を格納するリストを作成
grasping_tool_two_slant = []
stroke_two = 48 ### SMCの2指ハンド
phy = 5	### 傾斜の幅、前後に5度与える

## ストローク、指の長さ、傾斜の順で条件を満たすか確認する、結果を真偽で格納
for index_tool, tool in enumerate(two_finger_slant):
	pool = []
	pool.append(tool[0])
	for index_part, part in enumerate(two_finger_slant):
		if float(tool[3]) - stroke_two/2 < float(part[3]) and float(tool[3]) + stroke_two/2 > float(part[3]):
			if float(tool[4]) > float(part[4])/2:
				if float(tool[5]) - phy < float(part[5]) and float(tool[5]) + phy > float(part[5]):
					pool.append(True)
					continue
		pool.append( False)
	grasping_tool_two_slant.append(pool)

pprint.pprint(two_finger_slant)
pprint.pprint( grasping_tool_two_slant)
print()
print("output min combination")
Check_min_combnation(grasping_tool_two_slant)
pprint.pprint(grasping_tool_two_slant)
print()
###### 2指の曲率について、総当たりを考える
grasping_tool_two_curv = []
curv = 5	### 曲率の幅、前後に5mm与える

## ストローク、指の長さ、曲率の順で条件を満たすか確認する、結果を真偽で格納
for index_tool, tool in enumerate(two_finger_curv):
	pool = []
	pool.append(tool[0])
	for index_part, part in enumerate(two_finger_curv):
		if float(tool[3]) - stroke_two/2 < float(part[3]) and float(tool[3]) + stroke_two/2 > float(part[3]):
			if float(tool[4]) > float(part[4])/2:
				if float(tool[6]) - curv < float(part[6]) and float(tool[6]) + curv > float(part[6]):
					pool.append(True)
					continue
		pool.append( False)
	grasping_tool_two_curv.append(pool)

pprint.pprint(two_finger_curv)
pprint.pprint(grasping_tool_two_curv)
print()

print("output min combination")
Check_min_combnation(grasping_tool_two_curv)
pprint.pprint(grasping_tool_two_curv)
print()

###### 3指について、総当たりを考える
grasping_tool_three = []
stroke_three = 8	# SMCの3指ハンドのストローク

## ストローク、指の長さの順で条件を満たすか確認する、結果を真偽で格納
for index_tool, tool in enumerate(three_finger):
	pool = []
	pool.append(tool[0])
	for index_part, part in enumerate(three_finger):
		if float(tool[3]) - stroke_three/2 < float(part[3]) and float(tool[3]) + stroke_three/2 > float(part[3]):
			if float(tool[4]) > float(part[4])/2:
				pool.append(True)
				continue
		pool.append( False)
	grasping_tool_three.append(pool)

pprint.pprint(three_finger)
pprint.pprint(grasping_tool_three)
print()

print("output min combination")
Check_min_combnation(grasping_tool_three)
pprint.pprint(grasping_tool_three)
print()

#print("two_finger_slant")
#print(two_finger_slant)
#print("two_finger_curv")
#print(two_finger_curv)
#print("three finger")
#print(three_finger)

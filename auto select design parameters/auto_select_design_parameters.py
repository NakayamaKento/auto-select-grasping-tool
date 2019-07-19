import pprint
import sys
import csv
import copy
# https://qiita.com/motoki1990/items/0274d8bcf1a97fe4a869

sys.setrecursionlimit(100000)


### 最小の組み合わせを確認する関数 ###
def Check_min_combnation(grasping_tool):
	return Check(grasping_tool, 0, 0)

def Check(grasping_tool, index, times):
	times += 1
	if len(grasping_tool) <= index:
		print("再帰呼び出しおわり")
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

	# 判定結果を整理、Falseのままが１つでもあったら消さずに次に進む
	for item in check_list:
		if item == False:
			index += 1
			del tool_list
			return Check(grasping_tool, index, times)
	# 判定結果で消してもいいなら、消してから次に進む
	del grasping_tool[index]
	del tool_list
	return Check(grasping_tool, index, times)


### パラメータの中から最大の値を出力する関数 ###
def Max_parameter(grasping_tool, para_num):
	max = 0.0
	for tool in grasping_tool:
		if max < float(tool[para_num]):
			max = float(tool[para_num])
	return max

### パラメータの中から最小の値を出力する関数 ###
def Min_parameter(grasping_tool, para_num):
	min = 1000000	
	for tool in grasping_tool:
		if min > float(tool[para_num]):
			min = float(tool[para_num])
	return min


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
	if row[2] == "box":	#選択した図形が直方体か円柱か
		if row[5] != "N/A":	#傾斜パラメータ（slant）に値があるかどうか
			two_finger_slant.append(row)
		else:
			two_finger_curv.append(row)
	else:	
		three_finger.append(row)

###### 2指の傾斜について、しらみつぶしで探す 
###### まずは結果を格納するリストを作成
grasping_tool_two_slant = []
stroke_two = 48.0 ### SMCの2指ハンド
phy = 5.0	### 傾斜の幅、前後に5度与える

##### 次に、それぞれのパラメータの探索範囲（最大値と最小値）を決定
stroke_slant_min = Min_parameter(two_finger_slant, 3) - stroke_two/2
if stroke_slant_min < 0:
	stroke_slant_min = 0
stroke_slant_max = Max_parameter(two_finger_slant, 3) + stroke_two/2
finger_slant_min = Min_parameter(two_finger_slant, 4) / 2
finger_slant_max = Max_parameter(two_finger_slant, 4) * 1.5
slant_min = 0.0
slant_max = Max_parameter(two_finger_slant, 5) + phy
grasping_tool_slant = []

print("stroke_min, max : " + str(stroke_slant_min) + ", " + str(stroke_slant_max))
print("finger_min, max : " + str(finger_slant_min) + ", " + str(finger_slant_max))
print("slant_min, max : " + str(slant_min) + ", " + str(slant_max))

##### で、その値をもとに把持ツールパラメータ一覧を作成
No = 0
stroke_slant = stroke_slant_min
finger_slant = finger_slant_min
slant = slant_min

while stroke_slant <= stroke_slant_max:
	while finger_slant <= finger_slant_max:
		while slant <= slant_max:
			grasping_tool_slant.append([No, stroke_slant, finger_slant, slant])
			slant += 1.0
			No += 1
		slant = slant_min
		finger_slant += 10.0
	finger_slant = finger_slant_min
	stroke_slant += 4

print("Create " + str(len(grasping_tool_slant)) + " tools")

## ストローク、指の長さ、傾斜の順で条件を満たすか確認する、結果を真偽で格納
for index_tool, tool in enumerate(grasping_tool_slant):
	flag = 0
	pool = []
	pool.append(tool[0])
	for index_part, part in enumerate(two_finger_slant):
		if tool[1] - stroke_two/2 < float(part[3]) and tool[1] + stroke_two/2 > float(part[3]):	#ストローク確認
			if tool[2] > float(part[4])/2 and tool[2] < float(part[4])*2:	#指の長さ確認
				if tool[3] - phy < float(part[5]) and tool[3] + phy > float(part[5]):	#傾斜確認
					pool.append(True)
					flag =1
					continue
		pool.append( False)
	if flag == 0:
		continue
	grasping_tool_two_slant.append(pool)

pprint.pprint(two_finger_slant)
#pprint.pprint( grasping_tool_two_slant)
print()
print("output min combination")
Check_min_combnation(grasping_tool_two_slant)
pprint.pprint(grasping_tool_two_slant)
for tool in grasping_tool_two_slant:
	print(grasping_tool_slant[tool[0]])
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
#pprint.pprint(grasping_tool_two_curv)
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

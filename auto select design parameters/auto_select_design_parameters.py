import pprint
import math
import sys
import csv
import copy
from operator import itemgetter
# https://qiita.com/motoki1990/items/0274d8bcf1a97fe4a869

sys.setrecursionlimit(100000)

######################################
######### 関数羅列ゾーン #############
######################################

### 最小の組み合わせを確認する関数 ###
### 再帰的に実行する回数がめっちゃ多いから、メモリに気を付ける ###
def Check_min_combnation(tool_TF):
	return Check(tool_TF, 0)

def Check(tool_TF, index):	#index行目が不必要かどうかを判断する
	if len(tool_TF) <= index:	#確認するTFリストがなければ終わり
		return 0
	check_list = [False] * len(tool_TF[0])
	tool_list = copy.deepcopy(tool_TF)
	
	del tool_list[index]	#index行目を消してみる

	for tool_index, tool in enumerate(tool_list):
		for part_index, part in enumerate(check_list):
			if part_index == 0 or part_index == 1:	#check_listの0番目の要素はNoのとこやからそこは問答無用でTrueにしとく
				check_list[part_index] = True
				continue
			if tool_list[tool_index][part_index] == True:	#他のパラメータでカバーできているか確認
				check_list[part_index] = True

	# 判定結果を整理、Falseのままが１つでもあったら消さずに次に進む
	for item in check_list:
		if item == False:
			index += 1
			del tool_list
			return Check(tool_TF, index)
	# 判定結果で消してもいいなら、消してから次に進む
	del tool_TF[index]
	del tool_list
	return Check(tool_TF, index)


### パラメータの中から最大の値を出力する関数 ###
def Max_parameter(tool_para, para_num):
	max = 0.0
	for tool in tool_para:
		if max < float(tool[para_num]):
			max = float(tool[para_num])
	return max

### パラメータの中から最小の値を出力する関数 ###
def Min_parameter(tool_para, para_num):
	min = 1000000.0	# 適当に大きい値を初期値とする
	for tool in tool_para:
		if min > float(tool[para_num]):
			min = float(tool[para_num])
	return min

### 傾斜と指の長さから最小のストロークを求める関数 ###
def calc_slant_stroke(slant, finger, defo_stroke):
	return round( 2 * finger * math.tan(math.radians(slant/2) ) ) + defo_stroke/2

####################################
##### 関数一覧終わり！！ ###########
####################################


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
two_slant_part = []
two_curv_part = []
three_part = []

header = next(f)
print(header)

for row in f:
	if row[2] == "box":	#選択した図形が直方体か円柱か
		if row[5] != "N/A":	#傾斜パラメータ（slant）に値があるかどうか
			two_slant_part.append(row)
		else:
			two_curv_part.append(row)
	else:	
		three_part.append(row)

###### 2指の傾斜について、しらみつぶしで探す 
###### まずは結果を格納するリストを作成
tool_TF_slant = []
#stroke_two = 48.0 ### SMCの2指ハンド
stroke_two = 60.0 ### THKの電気ハンド
phy = 5.0	### 傾斜の幅、前後に5度与える

##### 次に、それぞれのパラメータの探索範囲（最大値と最小値）を決定
##### ストロークはマイナスになったら計算数が大くなるだけやから、無視する
stroke_slant_min = Min_parameter(two_slant_part, 3) - stroke_two/2
if stroke_slant_min < 0:	#マイナスになったら計算数が大くなるだけやから、無視する
	stroke_slant_min = 0
stroke_slant_max = Max_parameter(two_slant_part, 3) + stroke_two/2
finger_slant_min = Min_parameter(two_slant_part, 4) / 2
finger_slant_max = Max_parameter(two_slant_part, 4) * 1.5
slant_min = 0.0
slant_max = Max_parameter(two_slant_part, 5) + phy
tool_para_slant = []

##### で、その値をもとに把持ツールパラメータ一覧を作成
##### 刻み幅は d_slant, d_finger, d_stroke で管理（指とストロークは他のやつでも共通の値）
No = 0
stroke_slant = stroke_slant_min
finger_slant = finger_slant_min
slant = slant_min
d_slant = 1.0
d_finger = 10.0
d_stroke = stroke_two / 12

while slant <= slant_max:
	while finger_slant <= finger_slant_max:
		while stroke_slant <= stroke_slant_max:
			tool_para_slant.append([No, stroke_slant, finger_slant, slant])
			stroke_slant += d_stroke
			No += 1
		finger_slant += d_finger
		stroke_slant = calc_slant_stroke(slant, finger_slant, stroke_two)
	finger_slant = finger_slant_min
	slant += d_slant

print("Create " + str(len(tool_para_slant)) + " tools of slant")

## ストローク、指の長さ、傾斜の順で条件を満たすか確認する、結果を真偽で格納
## 全部 偽 やったらいらんから flagで管理
## 保存形式は [No, num of T, TF, TF, ... ]
for index_tool, tool in enumerate(tool_para_slant):
	flag = 0
	pool = []
	pool.append(tool[0])	# Noを保存
	pool.append(0)			# Trueの数を格納
	for index_part, part in enumerate(two_slant_part):
		if tool[1] - stroke_two/2 < float(part[3]) and tool[1] + stroke_two/2 > float(part[3]):	#ストローク確認
			if tool[2] > float(part[4])/2 and tool[2] < float(part[4])*2:	#指の長さ確認
				if tool[3] - phy < float(part[5]) and tool[3] + phy > float(part[5]):	#傾斜確認
					pool.append(True)
					pool[1] += 1	# Trueの数を追加
					flag =1
					continue
		pool.append( False)
	if flag == 0:
		continue
	tool_TF_slant.append(pool)

pprint.pprint(two_slant_part)
#pprint.pprint( tool_TF_slant)
print()
print("output min combination")
tool_TF_slant.sort(key=itemgetter(1))	# Trueの数をでソートする
Check_min_combnation(tool_TF_slant)
pprint.pprint(tool_TF_slant)
# 生き残ったパラメータをNoから出力
for tool in tool_TF_slant:
	print(tool_para_slant[tool[0]])
print()

# メモリ省エネのために使用済みリストを削除
del tool_TF_slant
del tool_para_slant

###### 2指の曲率について、しらみつぶしを考える
tool_TF_curv = []
curv_two = 5.0	### 曲率の幅、前後に5mm与える

##### 次に、それぞれのパラメータの探索範囲（最大値と最小値）を決定
##### ストロークはマイナスになったら計算数が大くなるだけやから、無視する
stroke_curv_min = Min_parameter(two_curv_part, 3) - stroke_two/2
if stroke_curv_min < 0:	#マイナスになったら計算数が大くなるだけやから、無視する
	stroke_curv_min = 0
stroke_curv_max = Max_parameter(two_curv_part, 3) + stroke_two/2
finger_curv_min = Min_parameter(two_curv_part, 4) / 2
finger_curv_max = Max_parameter(two_curv_part, 4) * 1.5
curv_min = Min_parameter(two_curv_part, 6) - curv_two
curv_max = Max_parameter(two_curv_part, 6) + curv_two
tool_para_curv = []

##### で、その値をもとに把持ツールパラメータ一覧を作成
##### 刻み幅は d_curv, d_finger, d_stroke で管理（指とストロークは他のやつでも共通の値）
No = 0
stroke_curv = stroke_curv_min
finger_curv = finger_curv_min
curv = curv_min
d_curv = 1.0

while stroke_curv <= stroke_curv_max:
	while finger_curv <= finger_curv_max:
		while curv <= curv_max:
			tool_para_curv.append([No, stroke_curv, finger_curv, curv])
			curv += d_curv
			No += 1
		curv = curv_min
		finger_curv += d_finger
	finger_curv = finger_curv_min
	stroke_curv += d_curv

print("Create " + str(len(tool_para_curv)) + " tools of curv")

## ストローク、指の長さ、曲率の順で条件を満たすか確認する、結果を真偽で格納
## 全部 偽 やったらいらんから flagで管理
## 保存形式は [No, num of T, TF, TF, ... ]
for index_tool, tool in enumerate(tool_para_curv):
	flag = 0
	pool = []
	pool.append(tool[0])	# Noを保存
	pool.append(0)			# Trueの数を格納
	for index_part, part in enumerate(two_curv_part):
		if tool[1] - stroke_two/2 < float(part[3]) and tool[1] + stroke_two/2 > float(part[3]):	#ストローク確認
			if tool[2] > float(part[4])/2 and tool[2] < float(part[4])*2:	#指の長さ確認
				if tool[3] - curv_two < float(part[6]) and tool[3] + curv_two > float(part[6]):	#曲率確認
					pool.append(True)
					pool[1] += 1	# Trueの数を追加
					flag = 1
					continue
		pool.append( False)
	if flag == 0:
		continue
	tool_TF_curv.append(pool)

pprint.pprint(two_curv_part)
#pprint.pprint(tool_TF_curv)
print()

print("output min combination")
tool_TF_curv.sort(key=itemgetter(1))	# Trueの数をでソートする
Check_min_combnation(tool_TF_curv)
pprint.pprint(tool_TF_curv)
# 生き残ったパラメータをNoから出力
for tool in tool_TF_curv:
	print(tool_para_curv[tool[0]])
print()

# メモリ省エネのために使用済みリストを削除
del tool_TF_curv
del tool_para_curv



###### 3指について、しらみつぶしを考える
tool_TF_three = []
stroke_three = 8.0	# SMCの3指ハンドのストローク

##### 次に、それぞれのパラメータの探索範囲（最大値と最小値）を決定
##### ストロークはマイナスになったら計算数が大くなるだけやから、無視する
stroke_three_min = Min_parameter(three_part, 3) - stroke_three/2
if stroke_three_min < 0:	#マイナスになったら計算数が大くなるだけやから、無視する
	stroke_three_min = 0
stroke_three_max = Max_parameter(three_part, 3) + stroke_three/2
finger_three_min = Min_parameter(three_part, 4) / 2
finger_three_max = Max_parameter(three_part, 4) * 1.5
tool_para_three = []

##### で、その値をもとに把持ツールパラメータ一覧を作成
##### 刻み幅は d_finger, d_stroke で管理（指とストロークは他のやつでも共通の値）
No = 0
stroke_three_para = stroke_three_min
finger_three = finger_three_min
d_three = 0.5
d_finger = 5.0

while stroke_three_para <= stroke_three_max:
	while finger_three <= finger_three_max:
		tool_para_three.append([No, stroke_three_para, finger_three])
		No += 1
		finger_three += d_finger
	finger_three = finger_three_min
	stroke_three_para += d_three

print("Create " + str(len(tool_para_three)) + " tools of three")



## ストローク、指の長さの順で条件を満たすか確認する、結果を真偽で格納## 全部 偽 やったらいらんから flagで管理
## 保存形式は [No, num of T, TF, TF, ... ]
for index_tool, tool in enumerate(tool_para_three):
	flag = 0
	pool = []
	pool.append(tool[0])	# Noを保存
	pool.append(0)			# Trueの数を格納
	for index_part, part in enumerate(three_part):
		if tool[1] - stroke_three/2 < float(part[3]) and tool[1] + stroke_three/2 > float(part[3]):	#ストローク確認
			if tool[2] > float(part[4])/2 and tool[2] < float(part[4])*3:	#指の長さ確認
				flag = 1
				pool.append(True)
				pool[1] += 1	# Trueの数を追加
				continue
		pool.append( False)
	if flag == 0:
		continue
	tool_TF_three.append(pool)

pprint.pprint(three_part)
#pprint.pprint(tool_TF_three)
print()

print("output min combination")
tool_TF_three.sort(key=itemgetter(1))	# Trueの数をでソートする
Check_min_combnation(tool_TF_three)
pprint.pprint(tool_TF_three)
# 生き残ったパラメータをNoから出力
for tool in tool_TF_three:
	print(tool_para_three[tool[0]])
print()

# メモリ省エネのために使用済みリストを削除
del tool_TF_three
del tool_para_three

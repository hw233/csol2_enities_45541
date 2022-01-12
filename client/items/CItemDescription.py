# -*- coding: gb18030 -*-


class CItemDescription:
	"""
	"""
	DesPos = {
				"name"						:	(0 , 0 ),	#装备名
				"creator"					:	(1 ,   ),	#打造者名字
				"eq_upper"					:	(2 ,   ),	#飞升者名字
				"eq_intensifyLevel"			:	(3 ,   ),	#装备强化等级(星星的数量)

				"bindType"					:	(4 , 0 ),	#绑定类型
				"eq_obey"					:	(4 , 1 ),   #认主类型
				"onlyLimit"					:	(5 , 0 ),	#是否唯一
			#	"canNotSell"				:	(5 , 1 ),	#是否可以出售
			#	"eq_wieldType"				:	(6 , 1 ),	#装备的位置(双手)
				"type"						:	(6 , 0 ),   #装备的类型(长弓,双手剑....)
				"tm_grade"					:	(6 , 1 ),	#法宝的品级
				"reqClasses"				:	(7 ,   ),	#装备该物品需要的职业
				"reqLevel"					:	(8 , 0 ),	#装备该物品需要的等级
				"itemreqLevel"				:	(8 , 0 ),	#使用该物品需要的等级 由于和武器的装备位置是相同 但是两个属性是不会同时出现的 所以用同一个位置代替
				"itemLevel"					:	(8 , 1 ),	#法宝的等级
				"reqGender"					:	(9 ,   ),	#装备该物品需要的性别
				"reqCredit"					:	(11 ,   ),	#装备该物品需要的声望
				"bookPotential"				:	(11 ,   ),	#潜能书所存储潜能


				"Attribute"					:	(12 ,  ),	#物品的基本属性(+攻击多少 防御多少......)
				"intensify"					:	(13 ,  ),	#强化后增加的属性(加强:物理攻击力 +XX .....)
				"eq_hardiness"				:	(15,   ),   #耐久度
				"eq_extraEffect"			:	(16,   ),	#装备附加属性(如 +X力量 +X智力 这几条是一个整体)
				"eq_createEffect"			:	(17,   ),	#装备灌注属性(如 +X力量 +X智力 这几条是一个整体)
				"tm_extraEffect"			:	(18,   ),	#法宝的品级属性
				"tm_flawEffect"				:   (19,   ),	#法宝的破绽属性
				"spell"						:	(20,   ),   #物品使用的效果(技能)


				"suitInfo"					:	(21,   ),   #套装的穿戴情况( XX套装(X/7) 什么套装 穿了几件)
				"suitChild0"					:	(22,   ),	#套装1
				"suitChild1"					:	(23,   ),	#套装2
				"suitChild2"					:	(24,   ),	#套装3
				"suitChild3"					:	(25,   ),	#套装4
				"suitChild4"					:	(26,   ),	#套装5

				"eq_suitEffect"				:	(27,   ),   #套装属性


				"bj_extraStone"				:	(28,   ),	#装备上的孔
				"bj_extraEffect"				:	(29,   ),	#镶嵌附加的属性
				"bj_slotLocation"				:	(30,   ),	#镶嵌附加的属性 

				"em_material"				:	(31,   ),	#需要的材料
				"tm_skillName"				:	(32, 0 ),	#法宝技能
				"tm_skillLevel"				:	(32, 1 ),	#法宝技能等级
				"goldYuanbao"				:	(33,   ),	#金元宝

				"ch_teleportRecord"		:	(37,   ),	#传送点记录信息
				"godweaponskill"			:	(37,   ),	# 神器技能
				"godweaponskilldes"		:	(38,   ),	# 神器技能说明
				"describe1"					:	(39,   ),	#额外的描述信息1
				"describe2"					:	(40,   ),	#额外的描述信息2
				"describe3"					:	(41,   ),	#额外的描述信息3
				"useDegree"				:	(42,   ),	#使用次数
				"warIntegral"				:	(43,   ), 	#战场积分
				"cp_itemDes"				:	(44,   ),	#合成后物品的描述信息
				"lifeType"					:	(45,   ),	#物品的剩余使用时间
				"springUsedCD"			:	(46,   ),	#物品CD剩余时间
				"silverYuanbao"			:	(47,   ),	#银元宝
			}

	def __init__(self ):
		self.Description = {}	#存储生成的描述信息
		self.DesSeveral = []	#记录哪些key是由多条描述构成的

	def Clear(self):
		"""
		清除上次残留的信息
		"""
		self.Description = {}

	def SetDescription(self, key ,info):
		"""
		设置和添加描述
		@param	key  : 该项的key
		@type	key  : str
		@param	info : 该项的描述信息(已经格式化好的)
		@type	info : str
		return :	   BOOL 表示是否添加成功
		"""
		pos = self.DesPos.get(key) 										#获取该项属性在描述框中显示的位置
		if not pos:														#这个不应该出现的
			return False
		ds = self.Description.get(pos[0])								#获取该位置的描述
		if not ds:														#如果该位置无描述
			if len(pos)==1:												#如果只有行数没有列数 表示该信息占一行
				self.Description[pos[0]] = [info]						#如果是第一列 那么直接设定
			else:														
				self.Description[pos[0]] = [info," "]					#把描述直接设置在第一列
		else:
			if len(pos)==1:
				return
			if pos[1] == 0:												#判断该描述是几列
				self.Description[pos[0]][0] = info						#如果是第一列 那么直接设定
			elif pos[1] == 1:
				self.Description[pos[0]][1] = info						#如果是第二列 那么设定到第二列
		return True

	def SetDesSeveral( self, key , infolist):
		"""
		设置和添加几行的描述
		@param	key  : 该项的key
		@type	key  : str
		@param	infolist : 该key的描述信息 由多个列表组成 用于一次加入多条信息(已经格式化好的)
		@type	infolist : list
		return :	   BOOL 表示是否添加成功
		"""
		if not infolist:
			return False

		pos = self.DesPos.get(key)
		if not pos:
			return False
		self.Description[pos[0]] = []
		self.DesSeveral.append(pos[0])
		self.Description[pos[0]] = infolist
		return True

	def	GetDescription(self ):
		"""
		获取物品的所有描述信息
		return: List  排列好的物品的描述信息
		"""
		if not self.Description:
			return []
		keys = self.Description.keys()
		keys.sort()
		description = []
		self.DesSeveral = set(self.DesSeveral) #去掉重复加入的

		for key in keys:
			if key not in self.DesSeveral:
				description.append( self.Description[key] )
			else:
				for info in self.Description[key]:
					description.append( info )
		self.Description = {}
		self.DesSeveral = []
		return description

		"""
		index = 0
		count = 0
		for key in keys:
			if key < self.frame1[ index ]:	#如果小于第一个框的话 直接添加数据
				description.append( self.Description[key] )
				count += 1
			else:	#如果已经超过第一个框了 那么加入分割线(空的list值表示分割)
				if count: #如果在该框内没有加入信息 那么不加入分割框
					description.append( [] )
				count = 0
				index += 1
		self.Description = {}
		return description
		"""




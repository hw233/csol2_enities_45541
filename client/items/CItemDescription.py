# -*- coding: gb18030 -*-


class CItemDescription:
	"""
	"""
	DesPos = {
				"name"						:	(0 , 0 ),	#װ����
				"creator"					:	(1 ,   ),	#����������
				"eq_upper"					:	(2 ,   ),	#����������
				"eq_intensifyLevel"			:	(3 ,   ),	#װ��ǿ���ȼ�(���ǵ�����)

				"bindType"					:	(4 , 0 ),	#������
				"eq_obey"					:	(4 , 1 ),   #��������
				"onlyLimit"					:	(5 , 0 ),	#�Ƿ�Ψһ
			#	"canNotSell"				:	(5 , 1 ),	#�Ƿ���Գ���
			#	"eq_wieldType"				:	(6 , 1 ),	#װ����λ��(˫��)
				"type"						:	(6 , 0 ),   #װ��������(����,˫�ֽ�....)
				"tm_grade"					:	(6 , 1 ),	#������Ʒ��
				"reqClasses"				:	(7 ,   ),	#װ������Ʒ��Ҫ��ְҵ
				"reqLevel"					:	(8 , 0 ),	#װ������Ʒ��Ҫ�ĵȼ�
				"itemreqLevel"				:	(8 , 0 ),	#ʹ�ø���Ʒ��Ҫ�ĵȼ� ���ں�������װ��λ������ͬ �������������ǲ���ͬʱ���ֵ� ������ͬһ��λ�ô���
				"itemLevel"					:	(8 , 1 ),	#�����ĵȼ�
				"reqGender"					:	(9 ,   ),	#װ������Ʒ��Ҫ���Ա�
				"reqCredit"					:	(11 ,   ),	#װ������Ʒ��Ҫ������
				"bookPotential"				:	(11 ,   ),	#Ǳ�������洢Ǳ��


				"Attribute"					:	(12 ,  ),	#��Ʒ�Ļ�������(+�������� ��������......)
				"intensify"					:	(13 ,  ),	#ǿ�������ӵ�����(��ǿ:�������� +XX .....)
				"eq_hardiness"				:	(15,   ),   #�;ö�
				"eq_extraEffect"			:	(16,   ),	#װ����������(�� +X���� +X���� �⼸����һ������)
				"eq_createEffect"			:	(17,   ),	#װ����ע����(�� +X���� +X���� �⼸����һ������)
				"tm_extraEffect"			:	(18,   ),	#������Ʒ������
				"tm_flawEffect"				:   (19,   ),	#��������������
				"spell"						:	(20,   ),   #��Ʒʹ�õ�Ч��(����)


				"suitInfo"					:	(21,   ),   #��װ�Ĵ������( XX��װ(X/7) ʲô��װ ���˼���)
				"suitChild0"					:	(22,   ),	#��װ1
				"suitChild1"					:	(23,   ),	#��װ2
				"suitChild2"					:	(24,   ),	#��װ3
				"suitChild3"					:	(25,   ),	#��װ4
				"suitChild4"					:	(26,   ),	#��װ5

				"eq_suitEffect"				:	(27,   ),   #��װ����


				"bj_extraStone"				:	(28,   ),	#װ���ϵĿ�
				"bj_extraEffect"				:	(29,   ),	#��Ƕ���ӵ�����
				"bj_slotLocation"				:	(30,   ),	#��Ƕ���ӵ����� 

				"em_material"				:	(31,   ),	#��Ҫ�Ĳ���
				"tm_skillName"				:	(32, 0 ),	#��������
				"tm_skillLevel"				:	(32, 1 ),	#�������ܵȼ�
				"goldYuanbao"				:	(33,   ),	#��Ԫ��

				"ch_teleportRecord"		:	(37,   ),	#���͵��¼��Ϣ
				"godweaponskill"			:	(37,   ),	# ��������
				"godweaponskilldes"		:	(38,   ),	# ��������˵��
				"describe1"					:	(39,   ),	#�����������Ϣ1
				"describe2"					:	(40,   ),	#�����������Ϣ2
				"describe3"					:	(41,   ),	#�����������Ϣ3
				"useDegree"				:	(42,   ),	#ʹ�ô���
				"warIntegral"				:	(43,   ), 	#ս������
				"cp_itemDes"				:	(44,   ),	#�ϳɺ���Ʒ��������Ϣ
				"lifeType"					:	(45,   ),	#��Ʒ��ʣ��ʹ��ʱ��
				"springUsedCD"			:	(46,   ),	#��ƷCDʣ��ʱ��
				"silverYuanbao"			:	(47,   ),	#��Ԫ��
			}

	def __init__(self ):
		self.Description = {}	#�洢���ɵ�������Ϣ
		self.DesSeveral = []	#��¼��Щkey���ɶ����������ɵ�

	def Clear(self):
		"""
		����ϴβ�������Ϣ
		"""
		self.Description = {}

	def SetDescription(self, key ,info):
		"""
		���ú��������
		@param	key  : �����key
		@type	key  : str
		@param	info : �����������Ϣ(�Ѿ���ʽ���õ�)
		@type	info : str
		return :	   BOOL ��ʾ�Ƿ���ӳɹ�
		"""
		pos = self.DesPos.get(key) 										#��ȡ��������������������ʾ��λ��
		if not pos:														#�����Ӧ�ó��ֵ�
			return False
		ds = self.Description.get(pos[0])								#��ȡ��λ�õ�����
		if not ds:														#�����λ��������
			if len(pos)==1:												#���ֻ������û������ ��ʾ����Ϣռһ��
				self.Description[pos[0]] = [info]						#����ǵ�һ�� ��ôֱ���趨
			else:														
				self.Description[pos[0]] = [info," "]					#������ֱ�������ڵ�һ��
		else:
			if len(pos)==1:
				return
			if pos[1] == 0:												#�жϸ������Ǽ���
				self.Description[pos[0]][0] = info						#����ǵ�һ�� ��ôֱ���趨
			elif pos[1] == 1:
				self.Description[pos[0]][1] = info						#����ǵڶ��� ��ô�趨���ڶ���
		return True

	def SetDesSeveral( self, key , infolist):
		"""
		���ú���Ӽ��е�����
		@param	key  : �����key
		@type	key  : str
		@param	infolist : ��key��������Ϣ �ɶ���б���� ����һ�μ��������Ϣ(�Ѿ���ʽ���õ�)
		@type	infolist : list
		return :	   BOOL ��ʾ�Ƿ���ӳɹ�
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
		��ȡ��Ʒ������������Ϣ
		return: List  ���кõ���Ʒ��������Ϣ
		"""
		if not self.Description:
			return []
		keys = self.Description.keys()
		keys.sort()
		description = []
		self.DesSeveral = set(self.DesSeveral) #ȥ���ظ������

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
			if key < self.frame1[ index ]:	#���С�ڵ�һ����Ļ� ֱ���������
				description.append( self.Description[key] )
				count += 1
			else:	#����Ѿ�������һ������ ��ô����ָ���(�յ�listֵ��ʾ�ָ�)
				if count: #����ڸÿ���û�м�����Ϣ ��ô������ָ��
					description.append( [] )
				count = 0
				index += 1
		self.Description = {}
		return description
		"""




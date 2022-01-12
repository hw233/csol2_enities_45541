# -*- coding: gb18030 -*-
# $Id: PetEpitome.py,v 1.30 2008-08-19 09:40:01 huangdong Exp $
#
"""
implement pet epitome type

2007/07/01: writen by huangyongwei
2007/11/17: rewriten by huangyongwei and rename it from "PetEpitomeType.py" to "PetEpitome.py"
"""


import BigWorld
import csarithmetic
import csdefine
import csconst
import Love3
from copy import copy
from bwdebug import *
from cscollections import MapList
from PetFormulas import formulas
from CellPetDict import CellPetEpitome


# --------------------------------------------------------------------
# global
# --------------------------------------------------------------------
# -----------------------------------------------------
# def 中定义，并且保存到数据库的属性（Persistent == True）
# -----------------------------------------------------
_saveAttrs = MapList()						# 所有需要保存的属性
_saveAttrs["ownerDBID"] = int				# 所属的角色的数据库 ID
_saveAttrs["className"] = str				# 配置文件中的 Entity 类别 ID
_saveAttrs["mapMonster"] = str				# 对应的 momnster 的 entity 类别 ID
_saveAttrs["modelNumber"] = str				# 模型号
_saveAttrs["uname"] = str					# 默认名字
_saveAttrs["name"] = str					# 自定义名字
_saveAttrs["gender"] = int					# 性别
_saveAttrs["species"] = int					# 辈分＋类别

_saveAttrs["level"] = int					# 等级
_saveAttrs["HP"] = int						# 生命
_saveAttrs["MP"] = int						# 法力
_saveAttrs["EXP"] = int						# 经验

_saveAttrs["e_corporeity"] = int			# 强化的体制值
_saveAttrs["e_strength"] = int				# 强化的力量值
_saveAttrs["e_intellect"] = int				# 强化的智力值
_saveAttrs["e_dexterity"] = int				# 强化的敏捷值

_saveAttrs["ec_corporeity"] = int			# 体制强化次数
_saveAttrs["ec_strength"] = int				# 力量强化次数
_saveAttrs["ec_intellect"] = int			# 智力强化次数
_saveAttrs["ec_dexterity"] = int			# 敏捷强化次数
_saveAttrs["ec_free"] = int					# 自由强化次数

#_saveAttrs["baseNimbus"] = int				# 灵值基础值
_saveAttrs["ability"] = int					# 成长度
_saveAttrs["nimbus"] = int					# 当前灵值
_saveAttrs["calcaneus"] = int				# 根骨
_saveAttrs["stamp"] = int					# 印记
_saveAttrs["isBinded"] = int				# 是否绑定，不能使用bool，因为此转换的对象是db中读取的字符串数据。16:30 2009-11-27，wsf

_saveAttrs["character"] = int				# 性格
_saveAttrs["life"] = int					# 寿命
_saveAttrs["joyancy"] = int					# 快乐度
_saveAttrs["procreated"] = int				# 是否已经繁殖（csdefine.py 中有三个值可选：未繁殖、正在繁殖、已繁殖）

_saveAttrs["absorbableEXPLevelValue"] = int	# 宠物这一级已经吸取的经验
_saveAttrs["absorbableEXP"] = long			# 可吸收的经验值
_saveAttrs["absorbDate"] = long				# 上次吸收经验值的日期

# -----------------------------------------------------
# def 中有定义，但不保存到数据库的属性（Persistent == False）
# -----------------------------------------------------
_unsaveAttrs = []
_unsaveAttrs.append( "takeLevel" )			# 携带等级
_unsaveAttrs.append( "databaseID" )			# 数据库 ID
_unsaveAttrs.append( "attrSkillBox" )		# 技能列表

# 宠物二级属性
_secondaryAttrs = []
_secondaryAttrs.append( "corporeity" )		# 体制
_secondaryAttrs.append( "strength" )		# 力量
_secondaryAttrs.append( "intellect" )		# 智力
_secondaryAttrs.append( "dexterity" )		# 敏捷

# -----------------------------------------------------
# 只在 Epitome 中用到，Pet.def 中不需要定义的属性
# -----------------------------------------------------
_tempAttrs = []								# 宠物临时属性
_tempAttrs.append( "mapPetID" )				# 对应的 entityID（如果出征的话），如果没出征则为 0
_tempAttrs.append( "isInVend" )				# 宠物是否在摆摊中
_tempAttrs.append( "vendSellPrice" )		# 宠物摆摊出售价格

# -----------------------------------------------------
# Epitome 的所有属性
# -----------------------------------------------------
_allAttrs = \
	_saveAttrs.keys() + \
	_unsaveAttrs + \
	_secondaryAttrs + \
	_tempAttrs								# 宠物所有的属性

# -----------------------------------------------------
# 需要发送到客户端，向客户端公开的属性
# -----------------------------------------------------
_sendingAttrs = copy( _allAttrs )			# 要发送到客户端（客户端可见）的宠物属性
_sendingAttrs.remove( "ownerDBID" )			# 不发送所属玩家的数据库 ID 到客户端（因为客户端可以找到自己角色的 databaseID 因此没有必要）
_sendingAttrs.remove( "className" )			# 不发送配置文件中的 enttiy 标记 ID 到客户端
_sendingAttrs.remove( "e_corporeity" )		# 不发送体制强化值到客户端
_sendingAttrs.remove( "e_strength" )		# 不发送力量强化值到客户端
_sendingAttrs.remove( "e_intellect" )		# 不发送智力强化值到客户端
_sendingAttrs.remove( "e_dexterity" )		# 不发送敏捷强化值到客户端
_sendingAttrs.remove( "absorbableEXP" )		# 不发送经验吸收值到客户端
_sendingAttrs.remove( "absorbDate" )		# 不发送上一次经验吸收时间到客户端

# -----------------------------------------------------
# 需要更新到cell的属性
# -----------------------------------------------------
_sendingCellAttrs = ["databaseID", "species", "level", \
					"className", "mapMonster", "ability", \
					"life", "joyancy", "takeLevel", \
					"stamp", "procreated", "gender", \
					"isBinded",
					]

# --------------------------------------------------------------------
# exclude sql command methods
# --------------------------------------------------------------------
def _queryPetsSkills( strPetDBIDs, callback ) :
	"""
	查找一组宠物的技能 ID
	"""
	def onQuery( rest, rows, errStr ) :
		if errStr :
			ERROR_MSG( "query pet's( %i ) skills fail: %s" % errStr )
			callback( {} )
		else :
			skills = {}
			for skillInfo in rest :
				petID, skillID = int( skillInfo[0] ), int( skillInfo[1] )
				if petID in skills :
					skills[petID].append( skillID )
				else :
					skills[petID] = [skillID]
			callback( skills )

	sql = "select parentID, sm_value from tbl_Pet_attrSkillBox where parentID in %s" % strPetDBIDs
	INFO_MSG( "\nquery pet's skills:\n" + sql + "\n" )
	BigWorld.executeRawDatabaseCommand( sql, onQuery )

def queryPets( ownerDBID, petDBIDs, callback ) :
	sql = "select id%s from tbl_Pet where sm_ownerDBID = %i and id in %s"
	strAttrs = ""
	for attrName, attrType in _saveAttrs.items() :
		strAttrs += ", sm_%s" % attrName
	strdbids = str( tuple( [int( id ) for id in petDBIDs] ) )			# remove character "L" in long type id
	if len( petDBIDs ) == 1 :
		strdbids = strdbids.replace( ",", "" )
	sql = sql % ( strAttrs, ownerDBID, strdbids )
	INFO_MSG( "\n\t" + sql + "\n" )

	petEpitomes = MapList()
	def onQuerySkills( skills ) :
		for id, epitome in petEpitomes.items() :
			epitome.updateAttr( "attrSkillBox", skills.get( id, [] ) )
		callback( True, petEpitomes )

	def onQuery( rest, rows, errStr ) :
		if errStr :
			ERROR_MSG( "read database fail when query pets:\n\t%s" % errStr )
			callback( False, {} )
		else :
			for petQuery in rest :
				epitome = PetEpitome.getEpitomeByQuery( petQuery )
				petEpitomes[long( petQuery[0] )] = epitome
			_queryPetsSkills( strdbids, onQuerySkills )
	BigWorld.executeRawDatabaseCommand( sql, onQuery )

def queryFosterPets( petDBIDs, callback ) :
	sql = "select id%s from tbl_Pet where id in %s"
	strAttrs = ""
	for attrName, attrType in _saveAttrs.items() :
		strAttrs += ", sm_%s" % attrName
	strdbids = str( tuple( [int( id ) for id in petDBIDs] ) )			# remove character "L" in long type id
	if len( petDBIDs ) == 1 :
		strdbids = strdbids.replace( ",", "" )
	sql = sql % ( strAttrs, strdbids )
	INFO_MSG( "\n\t" + sql + "\n" )

	petEpitomes = MapList()
	def onQuerySkills( skills ) :
		for id, epitome in petEpitomes.items() :
			epitome.updateAttr( "attrSkillBox", skills.get( id, [] ) )
		callback( True, petEpitomes )

	def onQuery( rest, rows, errStr ) :
		if errStr :
			ERROR_MSG( "read database fail when query pets:\n\t%s" % errStr )
			callback( False, {} )
		else :
			for petQuery in rest :
				epitome = PetEpitome.getEpitomeByQuery( petQuery )
				petEpitomes[long( petQuery[0] )] = epitome
			_queryPetsSkills( strdbids, onQuerySkills )
	BigWorld.executeRawDatabaseCommand( sql, onQuery )

# -----------------------------------------------------
def _updatePetAttrs( petDBID, attrs, callback ) :
	"""
	更新需要保持到数据库的宠物属性（模块内调用）
	@type			petDBID  : INT64
	@param			petDBID  : 宠物数据库 ID
	@type			attrs	 : list
	@param			attrs	 : 要更新的属性和属性值列表
	@type			callback : callable object
	@param			callback : 更新属性回调，它必须包含一个参数：
							   1：更新属性成功
							   0：更新属性失败，原因是属性不存在
							   -1：更新属性失败，原因是写入数据库失败（未知原因，很可能是 dbmgr 挂了）
	"""
	sql = "update tbl_Pet set "
	count = 0
	for name, value in attrs.items() :
		if name not in _saveAttrs : continue
		if type( value ) is str : value = "'%s'" % BigWorld.escape_string( value )
		sql += ( "sm_%s=%s," % ( name, value ) )
		count += 1
	if count == 0 :
		callback( 1 )
		return

	sql = "%s where id = %i" % ( sql[:-1], petDBID )
	INFO_MSG( "\n\t" + sql + "\n" )

	def onUpdateAttr( rest, rows, errStr ) :
		if errStr is not None :
			DEBUG_MSG( "update attribute %s fail!" % attrs.keys() )
			callback( -1 )
		elif rows <= 0 :
			DEBUG_MSG( "the pet you wanted to update its attributes( %s ) is not exist!" % attrs.keys() )
			callback( 0 )
		else :
			callback( 1 )
	BigWorld.executeRawDatabaseCommand( sql, onUpdateAttr )


# --------------------------------------------------------------------
# implement pet epitome class
# --------------------------------------------------------------------
class PetEpitome :
	def __init__( self ) :
		# -----------------------------------
		# def 中定义，并且保存到数据库的属性
		# -----------------------------------
		self.__ownerDBID = 0
		self.__className = ""
		self.__mapMonster = ""
		self.__modelNumber = ""
		self.__uname = ""
		self.__name = ""
		self.__gender = csdefine.GENDER_MALE
		self.__species = csdefine.PET_HIERARCHY_GROWNUP | csdefine.PET_TYPE_STRENGTH

		self.__level = 1
		self.__HP = 0
		self.__MP = 0
		self.__EXP = 0

		self.__e_corporeity = 0
		self.__e_strength = 0
		self.__e_intellect = 0
		self.__e_dexterity = 0

		self.__ec_corporeity = 0
		self.__ec_strength = 0
		self.__ec_intellect = 0
		self.__ec_dexterity = 0
		self.__ec_free = 0

		self.__ability = 0
		self.__nimbus = 0
		self.__calcaneus = 0
		self.__stamp = 0
		self.__isBinded = False

		self.__character = csdefine.PET_CHARACTER_SUREFOOTED
		self.__life = 65535
		self.__joyancy = 100
		self.__procreated = False

		self.__absorbableEXPLevelValue = 0	# 宠物这一级已经吸取的经验
		self.__absorbableEXP = 0	# 宠物每一天可吸取的经验值上限
		self.__absorbDate = 0		# 宠物每一天可吸取的经验值上限有效期time.time()

		# -----------------------------------
		# def 中有定义，但不保存到数据库的属性
		# -----------------------------------
		self.__takeLevel = 0
		self.__databaseID = 0
		self.__attrSkillBox = []

		# 二级属性
		self.__corporeity = 0
		self.__strength = 0
		self.__intellect = 0
		self.__dexterity = 0

		# -----------------------------------
		# 只在 Epitome 中用到，Pet.def 中不需要定义的属性
		# -----------------------------------
		self.__mapPetID = 0
		self.__isInVend = False		# 宠物是否在摆摊中
		self.__vendSellPrice = 0	# 宠物摆摊出售价格


	@staticmethod
	def getEpitomeByQuery( petQuery ) :
		"""
		通过数据库中查询出来的数据，生成一个 Epitome 实例
		通常在角色进入世界时，初始化其宠物使用
		@type				petQuery : list
		@param				petQuery : 宠物属性信息列表
		"""
		epitome = PetEpitome()
		for idx, ( attrName, attrType ) in enumerate( _saveAttrs.items() ) :
			value = attrType( petQuery[idx + 1] )
			epitome.updateAttr( attrName, value )
		epitome.updateAttr( "databaseID", long( petQuery[0] ) )					# 更新数据库 ID
		mapMonster = epitome.getAttr( "mapMonster" )							# 对应的怪物的 className
		monsterScript = Love3.g_objFactory.getObject( mapMonster )				# 对应的怪物

		# 14:52 2009-10-22,wsf，防止策划配错宠物配置的临时解决方案：宠物配置不存在引发异常前输出日志，以便查找问题。
		if monsterScript is None:
			ERROR_MSG( "--->>>npcMonster.xml不存在宠物( %s )配置." % mapMonster )

		epitome.updateAttr( "takeLevel", monsterScript.takeLevel )				# 更新携带等级
		species = epitome.getAttr( "species" )
		level = epitome.getAttr( "level" )
		nimbus = epitome.getAttr( "nimbus" )
		sndAttrValues = formulas.getSndProperties( species, level, nimbus )
		for attr in _secondaryAttrs :											# 更新所有二级属性
			e_value = epitome.getAttr( "e_" + attr )
			sndAttrValue = sndAttrValues[attr] + e_value
			epitome.updateAttr( attr, sndAttrValue )
		return epitome


	# ----------------------------------------------------------------
	# 公开属性
	# ----------------------------------------------------------------
	@property
	def databaseID( self ) :
		"""
		宠物的数据库 ID
		"""
		return self.__databaseID

	@property
	def level( self ):
		"""
		宠物等级
		"""
		return self.__level

	@property
	def species( self ):
		"""
		宠物类别和宠物成长年龄等级
		"""
		return self.__species

	@property
	def modelNumber( self ):
		"""
		宠物模型
		"""
		return self.__modelNumber


	# ----------------------------------------------------------------
	# mathods for packing / un packing
	# ----------------------------------------------------------------
	def getDictFromObj( self, epitome ) :
		dict = {}
		for attrName in _sendingAttrs :
			dict[attrName] = epitome.getAttr( attrName )
		return dict

	def createObjFromDict( self, dict ) :
		epitome = PetEpitome()
		for attrName, value in dict.items() :
			epitome.updateAttr( attrName, value )
		return epitome

	def isSameType( self, obj ) :
		return isinstance( obj, PetEpitome )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getAttr( self, attrName ) :
		"""
		获取宠物属性
		"""
		fullName = "_PetEpitome__" + attrName
		if hasattr( self, fullName ) :
			return getattr( self, fullName )
		else :
			ERROR_MSG( "pet epitome has no attribute: '%s'" % attrName )
		return None

	def getDisplayName( self ) :
		"""
		获取宠物全名称
		"""
		return formulas.getDisplayName( self.__species, self.__uname, self.__name )

	# ---------------------------------------
	def getCellPetEpitome( self ) :
		"""
		获取宠物公开给 cell 的部分数据（对应 alias.xml 中定义的：CELL_PET）
		"""
		cellPetEpitome = CellPetEpitome()
		for attrName in _sendingCellAttrs:
			setattr( cellPetEpitome, attrName, getattr( self, "_PetEpitome__" + attrName ) )

		return cellPetEpitome

	def getStoredPetDict( self ) :
		"""
		获取要存储到宠物仓库中的宠物属性字典
		"""
		storedDict = {}
		storedDict["databaseID"] = self.databaseID
		storedDict["name"] = self.getDisplayName()
		storedDict["level"] = self.level
		storedDict["species"] = self.species
		storedDict["modelNumber"] = self.modelNumber
		return storedDict

	# -------------------------------------------------
	def updateAttr( self, attrName, value, owner = None, callback = None ) :
		"""
		更新宠物属性
		@type				attrName : str
		@param				attrName : 属性名称
		@type				value	 : type of attribute
		@param				value	 : 属性值
		@type				owner	 : Role
		@param				owner	 : 宠物所属的角色
									   注意：如果传入这个值，则属性的更新将会发送到所属角色的客户端，否则不发送
											这些属性必须是 _sendingAttrs 中列出的属性
		@type				callback : callable object
		@param				callback : 更新属性回调
									   注意：如果传入一个回调，则要将属性更改同时保存到数据库
											这些属性必须是 _saveAttrs 中列出的属性
									   callback 必须包含一个参数：
									   1：更新属性成功
									   0：更新属性失败，原因是属性不存在
									   -1：更新属性失败，原因是写入数据库失败（未知原因，很可能是 dbmgr 挂了）
		"""
		if owner is None and callback is not None :									# 如果只传入 callback 而不传入 owner
			raise "if callback argument is not None, you must tell me the owner!"	# 则抛出异常

		fullName = "_PetEpitome__" + attrName
		if not hasattr( self, fullName ) :											# 判断属性是否存在
			ERROR_MSG( "pet epitome has no attribute: '%s'" % attrName )
			if callback is not None :
				callback( 0 )
			return

		if callback is None :														# 不需要写入数据库
			setattr( self, fullName, value )
			if hasattr( owner, "client" ) and owner.client is not None :
				owner.client.pcg_onUpdatePetEpitomeAttr( self.__databaseID, attrName, value )
			if hasattr( owner, "cell" ) and attrName in _sendingCellAttrs:
				owner.cell.pcg_onUpdatePetEpitomeAttr( self.__databaseID, attrName, value )
			return

		def onUpdateAttr( res ) :
			callback( res )
			if res <= 0 : return
			setattr( self, fullName, value )
			if owner is not None and hasattr( owner, "client" ) :
				owner.client.pcg_onUpdatePetEpitomeAttr( self.__databaseID, attrName, value )
			if hasattr( owner, "cell" ) and attrName in _sendingCellAttrs:
				owner.cell.pcg_onUpdatePetEpitomeAttr( self.__databaseID, attrName, value )
		_updatePetAttrs( self.databaseID, { attrName : value }, onUpdateAttr )		# 写入数据库

	def updateByPet( self, pet, owner = None ) :
		"""
		更新 epitome 中的所有属性为给定宠物的属性
		一般宠物回收时调用
		"""
		attrsDict = pet.cellData
		if type( attrsDict ) is not dict :
			attrsDict = attrsDict.getDict()
		for attrName in _allAttrs :									# 更新所有属性到客户端
			if attrName in _tempAttrs :								# 排除临时属性
				continue
			oldValue = self.getAttr( attrName )
			if attrName in attrsDict :								# cell 属性
				value = pet.cellData[attrName]
				if oldValue != value :
					self.updateAttr( attrName, value, owner )
			elif hasattr( pet, attrName ) :							# base 属性
				value = getattr( pet, attrName )
				if oldValue != value :
					self.updateAttr( attrName, value, owner )
			else :
				ERROR_MSG( "pet's cellData is not contain attribute: '%s'" % attrName )

	def updateByDict( self, dict, owner = None, callback = None ) :
		"""
		更新一组属性
		@type				owner	 : Role
		@param				owner	 : 宠物所属的角色
									   注意：如果传入这个值，则属性的更新将会发送到所属角色的客户端，否则不发送
											这些属性必须是 _sendingAttrs 中列出的属性
		@type				callback : 更新属性回调
									   注意：如果传入一个回调，则要将属性更改同时保存到数据库
											这些属性必须是 _saveAttrs 中列出的属性
		@param				callback :
		"""
		if owner is None and callback is not None :
			raise "if callback argument is not None, you must tell me the owner!"

		if callback is None :
			for attrName, value in dict.items() :
				self.updateAttr( attrName, value, owner )
			return

		def onUpdateAttrs( res ) :
			callback( res )
			if res < 0 : return
			for attrName, value in dict.items() :
				self.updateAttr( attrName, value, owner )
		_updatePetAttrs( self.databaseID, dict, onUpdateAttrs )


# --------------------------------------------------------------------
# implement active pet information class
# --------------------------------------------------------------------
class ActivePet :
	def getDictFromObj( self, actPet ) :
		return actPet

	def createObjFromDict( self, dict ) :
		return dict

	def isSameType( self, obj ) :
		return True


# --------------------------------------------------------------------
# pickle instances
# --------------------------------------------------------------------
instance = PetEpitome()
actPetInstance = ActivePet()

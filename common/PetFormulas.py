# -*- coding: gb18030 -*-
#
# $Id: PetFormulas.py,v 1.34 2008-08-21 09:12:25 huangyongwei Exp $

"""
pet property radix value reader

2007/10/24: writen by huangyongwei
"""

import time
import math
import random
import Math
import Language
import csdefine
import csconst
import csarithmetic
import ShareTexts

from bwdebug import *
from cscollections import MapList
from LevelEXP import RoleLevelEXP
from LevelEXP import PetLevelEXP
from config.pet import armor_radix
from config.pet import magic_armor_radix
from config.pet import PetLevelProperties
from config.pet import PetNimbusExp
from config.pet import PetAbility
from config.pet import PetJoyancyEffectConfig

class PetDatas :
	__hierarchiesMaps = {}
	__hierarchiesMaps[csdefine.PET_HIERARCHY_GROWNUP]	= "grownup"			# 成年
	__hierarchiesMaps[csdefine.PET_HIERARCHY_INFANCY1]	= "infancy1"		# 一代
	__hierarchiesMaps[csdefine.PET_HIERARCHY_INFANCY2]	= "infancy2"		# 二代

	__typesMaps = {}
	__typesMaps[csdefine.PET_TYPE_STRENGTH]				= "strength"		# 力量型
	__typesMaps[csdefine.PET_TYPE_SMART]				= "smart"			# 敏捷型
	__typesMaps[csdefine.PET_TYPE_INTELLECT]			= "intellect"		# 智力型
	__typesMaps[csdefine.PET_TYPE_BALANCED]				= "balanced"		# 均衡型

	__stringMapType = {}
	__stringMapType["strength"	]			= csdefine.PET_TYPE_STRENGTH		# 力量型
	__stringMapType["smart"]				= csdefine.PET_TYPE_SMART			# 敏捷型
	__stringMapType["intellect"]				= csdefine.PET_TYPE_INTELLECT	# 智力型
	__stringMapType["balanced"]				= csdefine.PET_TYPE_BALANCED		# 均衡型

	__sndAttrNames = ["corporeity", 										# 体质属性
					  "strength", 											# 力量属性
					  "intellect", 											# 智力属性
					  "dexterity" ] 										# 敏捷属性

	__petGettingMap = {}
	__petGettingMap[csdefine.PET_GET_CATCH]						= "normalCatch"			# 一般捕兽器捕捉
	__petGettingMap[csdefine.PET_GET_SUPER_CATCH]				= "suCatch"				# 万能捕兽器捕捉
	__petGettingMap[csdefine.PET_GET_CATHOLICON]				= "catholicon"			# 还童丹
	__petGettingMap[csdefine.PET_GET_PROPAGATE]					= "propagate"			# 繁殖
	__petGettingMap[csdefine.PET_GET_SUPER_CATHOLICON]			= "suCatholicon"		# 超级还童丹
	__petGettingMap[csdefine.PET_GET_RARE_CATHOLICON]			= "rearCatholicon"		# 珍稀还童丹
	__petGettingMap[csdefine.PET_GET_SUPER_RARE_CATHOLICON]		= "suRearCatholicon"	# 超级珍稀还童丹


	def __init__( self ) :
		self.__fixedECounts = {}								# { 宠物类别 : { "corporeity" : 体质值, "strength" : 力量值, "intellect" : 智力值, "dexterity" : 敏捷值 } }
		self.__armorRadies = armor_radix.Datas					# 宠物防御基础值：{ 宠物类别 : { 宠物等级 : 防御力 } }
		self.__magicArmorRadies = magic_armor_radix.Datas		# 宠物法术防御基础值：{ 宠物类别 : { 宠物等级 : 防御力 } }

		self.__levelProperties = PetLevelProperties.Datas		# { ( 宠物级别, 宠物类别 ) : { 属性1:属性值1, ... }, ... }，宠物的不同类型和级别对应不同的属性值
		self.__nimbusLevelProperties = {}						# { ( 宠物灵值级别, 宠物类别 ) : { 属性1:属性值1, ... }, ... }，宠物不同的灵值级别对应不同的属性值
		self.__nimbusLevelExp = PetNimbusExp.Datas				# { 宠物灵值级别:宠物根骨值, ... }，宠物不同灵值级别对应的根骨值

		# { key1:{ 成长度:概率}, key2:{ 成长度:概率}, ... }，key为长度为7的字符串，由此成长度对应的宠物类型、备份、获得方式、携带等级组合而成
		# 第一位为印记，第二位为备份，第三、四位为
		self.__abilityData = PetAbility.Datas

		self.__joyancyData = PetJoyancyEffectConfig.Datas

		self.__loadFixedEnhanceCounts( )
		self.__loadNimbusLevelProperties( )
	# ----------------------------------------------------------------
	def getLevelProperties( self, level, petType ):
		"""
		获得级别和类型对应的属性值
		"""
		try:
			return self.__levelProperties[ ( level, petType ) ]
		except KeyError:
			ERROR_MSG( "level( %i ),petType( %i ) is not exist." % ( level, petType ) )
			return None

	def getNimbusLevelProperties( self, nimbusLevel, petType ):
		"""
		获得灵值级别和类型对应的属性值
		"""
		try:
			return self.__nimbusLevelProperties[ ( nimbusLevel, petType ) ]
		except KeyError:
			ERROR_MSG( "level( %i ),petType( %i ) is not exist." % ( nimbusLevel, petType ) )
			return None

	def getCalcaneusMax( self, nimbus ):
		"""
		获得灵性级别对应的最大根骨值
		"""
		try:
			return self.__nimbusLevelExp[ nimbus ]
		except KeyError:
			ERROR_MSG( "没有对应灵性级别( %i )的根骨值。" % nimbus )
			return 0

	def getAbility( self, key ):
		"""
		根据宠物的携带等级、辈份、获取类型、印记 获得宠物的成长度
		"""
		try:
			abilityList = self.__abilityData[key]
		except KeyError:
			ERROR_MSG( "相应成长度不存在，Key:%s." % key )
			return 0

		rate = random.random()
		for ability, abilityRate in abilityList:
			if rate > abilityRate:
				continue
			return ability

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __loadFixedEnhanceCounts( self ) :
		"""
		加载各类宠物强化时，二级属性的加值
		"""
		sect = Language.openConfigSection( "config/pet/fixed_enhance_count.xml" )
		for hierachy, strHierachy in self.__hierarchiesMaps.iteritems() :
			for ptype, strType in self.__typesMaps.iteritems() :
				species = hierachy | ptype
				tag = "%s_%s" % ( strHierachy, strType )
				subSect = sect[tag]
				props = {}
				for propName in self.__sndAttrNames :
					props[propName] = subSect.readFloat( propName )
				self.__fixedECounts[species] = props

	def __loadNimbusLevelProperties( self ):
		"""
		加载不同宠物灵值级别和类型对应的属性值配置
		"""
		section = Language.openConfigSection( "config/pet/PetNimbusLevelProperties.xml" )
		for subSection in section.values():
			nimbuslevel = subSection.readInt( "nimbusLevel" )
			petType = self.__stringMapType[ subSection.readString( "petType" ) ]
			corporeity = subSection.readFloat( "corporeity" )
			intellect = subSection.readFloat( "intellect" )
			strength = subSection.readFloat( "strength" )
			dexterity = subSection.readFloat( "dexterity" )
			if not self.__levelProperties.has_key( ( nimbuslevel, petType ) ):
				self.__nimbusLevelProperties[ ( nimbuslevel, petType ) ] = {}
			self.__nimbusLevelProperties[ ( nimbuslevel, petType ) ] = { "corporeity":corporeity, "intellect":intellect, "strength":strength, "dexterity":dexterity }

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSndAttrRadix( self, petType, level, nimbus, attrName ) :
		"""
		获取二级属性值
		"""
		levelProperties = self.getLevelProperties( level, petType )
		nimbusProperties = self.getNimbusLevelProperties( nimbus, petType )
		try:
			return levelProperties[attrName] + nimbusProperties[attrName]
		except:
			return 0

	def getFixedEnhanceCount( self, species, propName, level ) :
		"""
		获取各等级下强化宠物的灵值
		@type				species	 : MACRO DEFINATION
		@param				species	 : defined in csdefine.py
		@type				propName : str
		@param				propName : property's name
		@type				level	 : int
		@param				level	 : the pet's level
		@rtype						 : int
		@return						 : the number of enhance time
		"""
		radix = self.__fixedECounts[species][propName]
		return int( round( radix * level ) )

	def getPhysicsArmorRadies( self, petType, level, ability ):
		"""
		根据宠物类型和级别获得物理防御基础值
		"""
		return self.__armorRadies[ self.__typesMaps[ petType ] ][ level ] * ability * 0.01

	def getMagicArmorRadies( self, petType, level, ability ):
		"""
		根据宠物类型和级别获得法术防御基础值
		"""
		return self.__magicArmorRadies[ self.__typesMaps[ petType ] ][ level ] * ability * 0.01

	def getJoyancyEffect( self, joyancy ):
		"""
		根据宠物快乐度获取影响基础属性值
		"""
		return self.__joyancyData.get( joyancy, 0.0 )

# --------------------------------------------------------------------
# implement formula class
# --------------------------------------------------------------------
class Formulas :
	__inst = None

	def __init__( self ) :
		assert Formulas.__inst is None
		self.__petDatas = PetDatas()

		self.__trainRadix = {}				# 代练时，获得的经验值与等级关系的基数

		self.__hitSpecRadix = {}			# 宠物物理攻击力规格参数（计算攻击力时用到）
		self.__hitSpeeds = {}				# 不同类型宠物的攻击速度
		self.__flipDPS = {}					# 不同类别宠物的 dps 波动值

		self.__magicHitRadix = {}			# 法术攻击力基础参数

		# ----------------------------------
		self.__doubleRadies = {}			# 暴击率基础参数表
		self.__doubleMaters = {}			# 暴击率底数

		self.__magicDoubleRadies = {}		# 法术暴击率
		self.__magicDoubleMaters = {}		# 法术暴击率底数

		self.__dodgeRadies = {}				# 闪避率基础参数
		self.__dodgeMaters = {}				# 闪避率底数

		self.__resistRadies = {}			# 招架率基数表
		self.__resistMaters = {}			# 招架率底数

		self.__aboutDexterityParam = {}
		self.__aboutIntellectParam = {}
		self.__aboutStrengthParam = {}

		self.__enhanceValue_Free = None
		self.__enhanceValue_Commmon = {}
		self.initialize( )


	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = Formulas()
		return SELF.__inst


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initialize( self ) :
		"""
		初始化宠物公式基础值
		"""
		# -----------------------------------
		# 初始化宠物代练获得的经验值等级基数
		# -----------------------------------
		tmpRadix = [ 3.1, 7.4, 11.5, 15.2, 18.2, 20.8, 22.9, 24.6, 25.8, 27, 28, 28.8, 29.4, 29.9, 30.3 ]
		for level in xrange( RoleLevelEXP.getMaxLevel() + 1 ):
			self.__trainRadix[ level ] = tmpRadix[ int( ( level - 1 ) / 10 ) ]

		# -----------------------------------
		# 初始化宠物规格参数
		# -----------------------------------
		self.__hitSpecRadix[csdefine.PET_HIERARCHY_GROWNUP]		= 1.0
		self.__hitSpecRadix[csdefine.PET_HIERARCHY_INFANCY1]	= 1.0
		self.__hitSpecRadix[csdefine.PET_HIERARCHY_INFANCY2]	= 1.0

		# -----------------------------------
		# 初始化宠物攻击速度
		# -----------------------------------
		self.__hitSpeeds[csdefine.PET_TYPE_STRENGTH]	= 1.0
		self.__hitSpeeds[csdefine.PET_TYPE_BALANCED]	= 1.0
		self.__hitSpeeds[csdefine.PET_TYPE_SMART]		= 1.0
		self.__hitSpeeds[csdefine.PET_TYPE_INTELLECT]	= 1.0

		# -----------------------------------
		# 初始化宠物物理 DPS 波动
		# -----------------------------------
		self.__flipDPS[csdefine.PET_TYPE_STRENGTH]	= 0.15
		self.__flipDPS[csdefine.PET_TYPE_BALANCED]	= 0.15
		self.__flipDPS[csdefine.PET_TYPE_SMART]		= 0.15
		self.__flipDPS[csdefine.PET_TYPE_INTELLECT]	= 0.15

		# -----------------------------------
		# 初始化宠物法术攻击基础
		# -----------------------------------
		self.__magicHitRadix[csdefine.PET_TYPE_STRENGTH]	= 0.02
		self.__magicHitRadix[csdefine.PET_TYPE_BALANCED]	= 0.02
		self.__magicHitRadix[csdefine.PET_TYPE_SMART]		= 0.02
		self.__magicHitRadix[csdefine.PET_TYPE_INTELLECT]	= 0.0213

		# -----------------------------------
		# 初始化宠物物理暴击率、法术暴击率、闪避率、招架率计算公式参数表。9:14 2009-3-5,wsf
		# -----------------------------------
		# 有关敏捷
		self.__aboutDexterityParam[ csdefine.PET_TYPE_STRENGTH ] = ( 0.01, 15, [ 2.2, 3, 4, 4.8, 8.2 ] )
		self.__aboutDexterityParam[ csdefine.PET_TYPE_BALANCED ] = ( 0.01, 22.5, [ 3.2, 4.5, 6, 7.3, 12.3 ] )
		self.__aboutDexterityParam[ csdefine.PET_TYPE_INTELLECT ] = ( 0.01, 15, [ 2.1, 3, 4, 4.8, 8.2 ] )
		self.__aboutDexterityParam[ csdefine.PET_TYPE_SMART ] = ( 0.01, 37.5, [ 5.4, 7.5, 10, 12, 20.3 ] )
		# 有关智力
		self.__aboutIntellectParam[ csdefine.PET_TYPE_STRENGTH ] = ( 0.01, 7.5, [ 1.1, 1.5, 2, 2.4, 4.1 ] )
		self.__aboutIntellectParam[ csdefine.PET_TYPE_BALANCED ] = ( 0.01, 22.5, [ 3.3, 4.5, 6, 7.2, 12.2 ] )
		self.__aboutIntellectParam[ csdefine.PET_TYPE_INTELLECT ] = ( 0.01, 52.5, [ 7.6, 10.5, 14, 16.9, 28.6 ] )
		self.__aboutIntellectParam[ csdefine.PET_TYPE_SMART ] = ( 0.01, 7.5, [ 1.1, 1.5, 2, 2.4, 4.1 ] )
		# 有关力量
		self.__aboutStrengthParam[ csdefine.PET_TYPE_STRENGTH ] = ( 0.01, 30, [ 4.3, 6, 8, 9.7, 16.3 ] )
		self.__aboutStrengthParam[ csdefine.PET_TYPE_BALANCED ] = ( 0.01, 22.5, [ 3.25, 4.5, 6, 7.3, 12.3 ] )
		self.__aboutStrengthParam[ csdefine.PET_TYPE_INTELLECT ] = ( 0.01, 7.5, [ 1.1, 1.5, 2, 2.4, 4.1 ] )
		self.__aboutStrengthParam[ csdefine.PET_TYPE_SMART ] = ( 0.01, 22.5, [ 3.2, 4.5, 6, 7.3, 12.3 ] )

		#强化属性/兑换参数
		self.__enhanceValue_Commmon = {
		csdefine.PET_TYPE_STRENGTH:{"strength":(9.354,0.338),"corporeity":(10.458,0.378),"dexterity":(4.667,0.169),"intellect":(4.667,0.169)},
		csdefine.PET_TYPE_BALANCED:{"strength":(7.308,0.264),"corporeity":(7.308,0.264),"dexterity":(7.308,0.264),"intellect":(7.308,0.264)},
		csdefine.PET_TYPE_SMART:{"strength":(6.948,0.251),"corporeity":(6.078,0.220),"dexterity":(11.580,0.418),"intellect":(4.632,0.167)},
		csdefine.PET_TYPE_INTELLECT:{"strength":(5.032,0.182),"corporeity":(4.113,0.149),"dexterity":(5.032,0.182),"intellect":(15.096,0.545)}}
		self.__enhanceValue_Free = ( 16.251, 0.587 )
	# -------------------------------------------------
	@staticmethod
	def secondToStrTime( seconds ) :
		"""
		将秒转化为：XX 小时 XX 分钟
		@type				seconds : INT64
		@param				seconds : time specifies in second
		@rtype						: str
		@return						: time in hour and minute
		"""
		seconds = int( seconds )
		hours = seconds / 3600
		minutes = ( seconds % 3600 ) / 60
		strHours = strMinutes = ""
		if hours > 0 :
			return "%d %s" % ( hours, ShareTexts.CHTIME_HOUR )
		if minutes > 0 :
			return "%d %s" % ( minutes, ShareTexts.CHTIME_MINUTE )
		return strHours + strMinutes


	# -------------------------------------------------
	# 直接从 PetDatas 中获取数据的方法（其实 petData 应该跟 formula 合并在一起的，设计的时候没有考虑周到，作了这个多余之举）
	# -------------------------------------------------
	def getSndProperties( self, species, level, nimbusLevel ):
		"""
		获取级别和类型对应的属性值
		"""
		petType = self.getType( species )
		propDict = {}
		propDict1 = self.__petDatas.getLevelProperties( level, petType )
		propDict2 = self.__petDatas.getNimbusLevelProperties( nimbusLevel, petType )
		propDict["corporeity"] = propDict1["corporeity"] + propDict2["corporeity"]
		propDict["strength"] = propDict1["strength"] + propDict2["strength"]
		propDict["intellect"] = propDict1["intellect"] + propDict2["intellect"]
		propDict["dexterity"] = propDict1["dexterity"] + propDict2["dexterity"]
		return propDict

	def getAbility( self, takeLevel, hierarchy, catchType, stamp ):
		"""
		根据宠物的携带等级、辈份、获取类型、印记 获得宠物的成长度
		"""
		return self.__petDatas.getAbility( self.getAbilityKey( takeLevel, hierarchy, catchType, stamp ) )

	def getStamp( self, catchType ):
		"""
		根据宠物的获得方式得到宠物的印记
		系统：csdefine.PET_STAMP_SYSTEM；手写：csdefine.PET_STAMP_MANUSCRIPT
		目前只有蛋生宠物会是手写，且宠物印记第一次生成后就不再变化。
		"""
		if catchType in [ csdefine.PET_GET_EGG1, csdefine.PET_GET_EGG2, csdefine.PET_GET_EGG3 ]:
			return csdefine.PET_STAMP_MANUSCRIPT
		else:
			return csdefine.PET_STAMP_SYSTEM

	def getAbilityKey( self, takeLevel, hierarchy, catchType, stamp ):
		"""
		根据宠物的携带等级、辈份、获取类型、印记 生成相应的成长度关键字字符串

		这个字符串的意义是：
			第一个字符表示宠物的类型（手写或者系统）；
			第二个字符表示宠物的备份；第三、四位表示宠物的生成类型；
			最后三位表示宠物的携带等级。
		"""
		sCatchType = str( catchType )
		while len( sCatchType ) < 2:	# 不足2位则前置补0
			sCatchType = "0" + sCatchType
		sTakeLevel = str( takeLevel )
		while len( sTakeLevel ) < 3:	# 不足3位则前置补0
			sTakeLevel = "0" + sTakeLevel

		return str( stamp ) + str( hierarchy ) + sCatchType + sTakeLevel

	def getSndAttrRadix( self, species, level, nimbus, attrName ) :
		"""
		获取二级属性基值
		@ptype				species  : MACRO DEFINATION
		@param				species  : defined in csdefined
		@ptype				ptype    : MACRO DEFINATION
		@param				ptype	 : defined in csdefined
		@ptype				level	 : INT8
		@param				level	 : level of the pet
		@ptype				attrName : str
		@param				attrName : property name: ( corporeity, catholicon, rareCatholicon, propagate )
		@rtype						 : int
		@return						 : property values
		"""
		petType = self.getType( species )
		return self.__petDatas.getSndAttrRadix( petType, level, nimbus, attrName )

	def getFixedEnhanceCount( self, species, propName, level ) :
		"""
		获取强化时的灵值
		@type				species	 : MACRO DEFINATION
		@param				species	 : defined in csdefine.py
		@type				propName : str
		@param				propName : property's name
		@type				level	 : int
		@param				level	 : the pet's level
		@rtype						 : int
		@return						 : the number of enhance time
		"""
		return self.__petDatas.getFixedEnhanceCount( species, propName, level )

	def getPhysicsArmorRadies( self, species, level, ability ):
		"""
		根据宠物类型和级别获得物理防御基础值
		"""
		ptype = self.getType( species )
		return self.__petDatas.getPhysicsArmorRadies( ptype, level, ability )

	def getMagicArmorRadies( self, species, level, ability ):
		"""
		根据宠物类型和级别获得法术防御基础值
		"""
		ptype = self.getType( species )
		return self.__petDatas.getMagicArmorRadies( ptype, level, ability )


	# -------------------------------------------------
	# 宠物初始化的基础属性值的获取
	# -------------------------------------------------
	@staticmethod
	def getKeepingCount( reinBibleCount ) :
		"""
		获取可携带宠物的总数量
		@type		reinBibleCount : int
		@param		reinBibleCount : the number of rein bible
		@rtype					   : int
		@return					   : the number of pet can be keep
		"""
		return 3 + reinBibleCount

	def getSndAttrValue( self, attrName, species, level, nimbus ) :
		"""
		获取二级属性值
		@type				attrName : str
		@param				attrName : secondary attribute name
		@type				species	 : hierarchy combine with type of the pet
		@param				species	 : UINT8
		@type				level	 : int
		@param				level	 : level of the pet
		@rtype						 : int
		@return						 : second attribute value
		"""
		return self.getSndAttrRadix( species, level, nimbus, attrName )

	@staticmethod
	def getCharacter() :
		"""
		随机取得宠物的性格
		@rtype					: MACRO DEFINATION
		@rettun					: csdeine.PET_CHARACTER_SUREFOOTED
										  PET_CHARACTER_CLOVER
										  PET_CHARACTER_CANNILY
										  PET_CHARACTER_BRAVE
										  PET_CHARACTER_LIVELY
		"""
		charas = [csdefine.PET_CHARACTER_SUREFOOTED,
				  csdefine.PET_CHARACTER_CLOVER,
				  csdefine.PET_CHARACTER_CANNILY,
				  csdefine.PET_CHARACTER_BRAVE,
				  csdefine.PET_CHARACTER_LIVELY]
		count = len( charas )
		return csarithmetic.getRandomElement( charas, count * [1] )


	# -------------------------------------------------
	# 宠物属性损耗的计算
	# -------------------------------------------------
	@staticmethod
	def getTickLifeDecreasement( hierarchy ) :
		"""
		获取寿命随时间的折减值
		@type			hierarchy : MACRO DEFINATION
		@param			hierarchy : defined in csdefine.py
		@rtype					  : int
		@return					  : wastage
		"""
		if hierarchy == csdefine.PET_HIERARCHY_GROWNUP :
			return 20
		elif hierarchy == csdefine.PET_HIERARCHY_INFANCY1 :
			return 25
		return 30

	@staticmethod
	def getLostBellLifeDecreasement() :
		"""
		获取宠物战败时，寿命的折减值
		@rtype					: int
		@return					: value
		"""
		return 300

	# ---------------------------------------
	@staticmethod
	def getConjureJoyancyLimit() :
		"""
		获取允许出征的最小快乐度
		@rtype					: int
		return					: joyancy value
		"""
		return 50

	@staticmethod
	def getTickJoyancyDecreasement() :
		"""
		get joyancy wastage in each time segment
		@rtype					  : int
		@return					  : wastage
		"""
		return 2

	@staticmethod
	def getLostBellJoyancyDecreasement() :
		"""
		获取宠物战败时，快乐度的折减值
		@rtype					: int
		@return					: value
		"""
		return 10

	@staticmethod
	def getTradeJoyancyDecreasement() :
		"""
		获取交易时的寿命折减
		@rtype					: int
		@return					: value
		"""
		return 60


	# ---------------------------------------
	# 捕捉宠物用到的公式
	# ---------------------------------------
	@staticmethod
	def getCatchedPetHierarchy( catchType ) :
		"""
		捕捉宠物时随机获取宠物的辈分
		"""
		if catchType == csdefine.PET_GET_EGG3:
			return csdefine.PET_HIERARCHY_INFANCY2
		elif catchType == csdefine.PET_GET_EGG2:
			return csdefine.PET_HIERARCHY_INFANCY1
		elif catchType == csdefine.PET_GET_EGG1:
			return csdefine.PET_HIERARCHY_GROWNUP

		hierarchies = [csdefine.PET_HIERARCHY_GROWNUP, csdefine.PET_HIERARCHY_INFANCY1]
		return csarithmetic.getRandomElement( hierarchies, [97, 3] )


	# ---------------------------------------
	# 合成宠物用到的公式
	# ---------------------------------------
	@staticmethod
	def getCombinePetCost() :
		"""
		获取很成宠物时，需要的金钱数量
		@rtype					: int
		@return					: cost
		"""
		return 2000

	# ---------------------------------------
	# 繁殖宠物用到的公式
	# ---------------------------------------
	@staticmethod
	def getProcreatePetCost() :
		"""
		获取繁殖宠物时需要的花费
		@rtype					: int
		@return					: cost
		"""
		return 100000

	@staticmethod
	def getProcreateTime() :
		"""
		获取繁殖时间，固定为csconst.PET_PROCREATE_NEED_TIME
		"""
		return csconst.PET_PROCREATE_NEED_TIME

	@staticmethod
	def getProcreateLifeDecreasement() :
		"""
		获取繁殖时，宠物的寿命折减
		@rtype					: int
		@return					: life descreasement
		"""
		return csconst.PET_PROCREATE_LIFT_NEED


	# ---------------------------------------
	# 代练用到的公式
	# ---------------------------------------
	@staticmethod
	def getCommonGemActicateCost() :
		"""
		获取激活普通宝石需要的花费
		@rtype						: int
		@return						: cost
		"""
		return csconst.GEM_HIRE_PAY

	@staticmethod
	def getTrainGemActivateCost() :
		"""
		获取激活代练宝石需要的花费
		@rtype						: int
		@return						: cost
		"""
		return 1000

	@staticmethod
	def getTrainTime( points ) :
		"""
		获取代练时间
		@type				points : int
		@param				points : point in game
		@rtype					   : int
		@return					   : time specifies with second
		"""
		return points * 180							# 1 hour equals to 20 points

	@staticmethod
	def getTrainPoints( ttime ) :
		"""
		通过代练时间获取代练点
		@type				ttime : INT64
		@pararm				ttime : train time
		@rtype					  : int
		@return					  : count of the points
		"""
		return int( ttime * 20 / 3600.0 )

	def getTrainEXP( self, ownerLevel, trainType, duration ) :
		"""
		获取代练后得到的经验值
		@type			ownerLevel : UINT8
		@param			ownerLevel : level of the pet's owner
		@type			trainType  : MACRO DEFINATION
		@param			trainType  : the pet's train type defined in csdefine.py
		@type			duration   : int
		@param			duration   : how long the training persisting( specified by seconds )
		@rytpe					   : int
		@return					   : gained exp value
		"""
		minutes = duration / 60.0
		radix = self.__trainRadix[ ownerLevel ]
		expMin = int( round( radix * minutes * ( 1 - 0.1 ) ) )
		expMax = int( round( radix * minutes * ( 1 + 0.1 ) ) )
		exp = random.randint( expMin, expMax )

		if trainType == csdefine.PET_TRAIN_TYPE_HARD:
			exp *= 1.7

		return int( round( exp ) )

	@staticmethod
	def getAbsorbExpUpper( level ) :	# wsf add,11:14 2008-7-31
		"""
		由宠物等级获得宠物当天能过喂养的经验值上限
		@type				level : UINT16
		@pararm				level : 宠物级别
		@rtype					  : int
		@return					  : count of the points
		"""
		return int( PetLevelEXP.getEXPMax( level ) * 1.3 )


	# ---------------------------------------
	# 宠物仓库用到的公式
	# ---------------------------------------
	@staticmethod
	def getStorageCost( stype, times ) :
		"""
		获取寄存宠物所需要的花费
		@type				stype : MACRO DEFINATION
		@param				stype : storage type defined in csdefine.py
		@rtype					  : UINT32
		@return					  : gold cost
		"""
		costs = {}
		costs[csdefine.PET_STORE_TYPE_LARGE] = 200
		costs[csdefine.PET_STORE_TYPE_SMALL] = 100
		return costs[stype]*times


	# ---------------------------------------
	# 宠物强化用到的公式
	# ---------------------------------------
	@staticmethod
	def getFreeEnhanceCount( level ) :
		"""
		获取指定等级下自由强化的总次数（当前等级下，自由强化次数超过此次数，则不能再使用自由强化）
		@type				level : UINT8
		@param				level : the pet's level
		@rtyle					  : int
		@return					  : enahnce times
		"""
		return int( round( level * 0.587 ) )

	@staticmethod
	def getEnhanceEffect( isCurse ) :
		"""
		获取强化效果
		@type				isCurse		 : bool
		@param				isCurse		 : whether use curse item
		"""
		if isCurse == True : return 5
		return csarithmetic.getRandomElement( [3, 4, 5], [4, 4, 2] )


	def getEnhanceValue( self, species, etype, attrName, count ):
		ptype = self.getType( species )
		if etype == csdefine.PET_ENHANCE_FREE:												# 如果是自由强化
			attrParam  = self.__enhanceValue_Free[0]
			transParam = self.__enhanceValue_Free[1]
		else:
			attrParam  = self.__enhanceValue_Commmon[ptype][attrName][0]
			transParam = self.__enhanceValue_Commmon[ptype][attrName][1]
		maxValue = max( int( attrParam * 1.5 ** ( 0.1 * count / transParam - 1.0 ) - attrParam * 1.5 ** ( 0.1 * ( count - 1 ) / transParam - 1.0 ) ), 5 )
		minValue = int( maxValue * 0.8 )
		return ( minValue , maxValue )

	# -------------------------------------------------
	# 关于宠物种类判断的公式和方法
	# -------------------------------------------------
	@staticmethod
	def getHierarchy( species ) :
		"""
		获取宠物辈分
		@type			species : MACRO DEFINATION
		@param			species : defined in csdefine.py
		@rtype					: MACRO DEFINATION
		@return					: hierarchy
		"""
		return species & csdefine.PET_HIERARCHY_MASK

	@staticmethod
	def getRejuvenesceHierarchy( hierarchy ):
		"""
		获取宠物还童后的辈份

		@type hierarchy :	INT16
		@param hierarchy :	还童前的辈份
		@rtype:	INT16
		@return:	还童后的辈份
		"""
		if hierarchy == csdefine.PET_HIERARCHY_GROWNUP:
			hierarchy = csdefine.PET_HIERARCHY_INFANCY1
		return hierarchy

	@staticmethod
	def getType( species ) :
		"""
		获取宠物类别
		@type			species : MACRO DEFINATION
		@param			species : defined in csdefine.py
		@rtype					: MACRO DEFINATION
		@return					: type
		"""
		return species & csdefine.PET_TYPE_MASK

	@staticmethod
	def isHierarchy( species, hierarchy ) :
		"""
		判断某宠物是否时指定的辈分
		@type			species : MACRO DEFINATION
		@param			species : defined in csdefine.py
		@param					: hierarchy
		@rtype					: bool
		@return					: if it is hierarchy return true
		"""
		return Formulas.getHierarchy( species ) == hierarchy

	@staticmethod
	def isType( species, ptype ) :
		"""
		判定宠物是否是指定的类型
		@type			species : MACRO DEFINATION
		@param			species : defined in csdefine.py
		@type					: MACRO DEFINATION
		@param					: type
		@rtype					: bool
		@return					: if it is ptype return true
		"""
		return Formulas.getType( species ) == ptype


	# -------------------------------------------------
	# 关于宠物灵值的公式
	# -------------------------------------------------
	@staticmethod
	def getMaxNimbus( level ) :
		"""
		获取宠物当前等级下的灵性最大级别
		@ptype			hierarchy	: MACRO DEFINATION
		@param			hierarchy	: defined in csdefined
		@type			level		: UINT8
		@param			level		: the pet's level
		@rtype						: nimbus upper limit
		"""
		return level / 3

	def abilityToCalcaneus( self, ability ):
		"""
		成长度转化为根骨值

		@param ability : 成长度
		@type ability : INT32
		"""
		return ability * 100

	def calcaneusToNimbus( self, maxNimbus, currNimbus, calcaneus ) :
		"""
		将根骨转化为灵值等级
		@type			maxNimbus	: UINT8
		@param			maxNimbus	: nimbus's upper limit
		@type			currNimbus	: UINT8
		@param			currNimbus	: cureent nimbus
		@type			calcaneus	: INT32
		@param			calcaneus	: calcaneus
		@rtype						: tuple
		@return						: ( nimbus, remainder calcaneus )
		"""
		while calcaneus > 0 :
			if currNimbus >= maxNimbus :
				return ( currNimbus, 0 )
			nextCalcaneus = formulas.getCalcaneusMax( currNimbus )
			leaveCalcaneus = calcaneus - nextCalcaneus
			if leaveCalcaneus >= 0 :
				calcaneus = leaveCalcaneus
				currNimbus += 1
			if leaveCalcaneus <= 0 :
				break
		return ( currNimbus, calcaneus )

	def getCalcaneusMax( self, nimbus ) :
		"""
		获取当前的灵值等级下的根骨最大值（当根骨超过该值后，灵值等级升一级）
		@type			nimbus : UINT8
		@param			nimbus : nimbus
		@rtype				   : INT32
		@return				   : calcaneus value
		"""
		return self.__petDatas.getCalcaneusMax( nimbus )

	# -------------------------------------------------
	# 宠物快乐度公式
	# -------------------------------------------------
	def getJoyancyEffect( self, joyancy ) :
		"""
		获取快乐度对宠物物理和法术防御力的影响
		@type				joyancy : UINT8
		@param				joyancy : current joyancy value
		@rtype						: float
		@return						: effect
		"""
		return self.__petDatas.getJoyancyEffect( joyancy )

	# -------------------------------------------------
	# 宠物战斗属性计算公式
	# -------------------------------------------------
	@staticmethod
	def getBaseHPMax( corporeity, ability, level ):
		"""
		获取HP最大值基础值

		@type				corporeity  : int
		@param				corporeity  : 宠物体质
		@type				ability : int
		@param				ability : 宠物成长度

		体质*10 + 成长度* 8.4 * 1.5 ** ( 0.1 * level - 1 )
		"""
		return corporeity * 10 + ability * 8.4 * 1.5 ** ( 0.1 * level - 1 )

	@staticmethod
	def getBaseMPMax( intellect, ability, level ):
		"""
		获取MP最大值基础值

		@type				corporeity  : int
		@param				corporeity  : 宠物体质
		@type				ability : int
		@param				ability : 宠物成长度

		智力*10 + 成长度* 8.4 * 1.5 ** ( 0.1 * level - 1 )
		"""
		return intellect * 10 + ability * 8.4 * 1.5 ** ( 0.1 * level - 1 )

	@staticmethod
	def getBasePhysicsDPS( species, ability, strength, dexterity, level ) :
		"""
		获取基础物理 DPS
		@type				species	  : MSCRO DEFINATION
		@param				species	  : 宠物种类
		@type				strength  : int
		@param				strength  : 宠物力量
		@type				dexterity : int
		@param				dexterity : 宠物敏捷

		力量型（战士）
		基础物理DPS（基础值）=成长度*力量*0.025 + 20*1.5^(0.1*lv - 1)
		平衡型（剑客）
		基础物理dps（基础值）=成长度*（力量*0.02+敏捷*0.02） + 25*1.5^(0.1*lv - 1)
		敏捷型（射手）
		基础物理dps（基础值）=成长度* (力量 * 0.01 + 敏捷 * 0.02) + 25.75 * 1.5 ^ (0.1 * Lv - 1)
							  成长度*（力量*0.0024+敏捷*0.02）+ 21.25*1.5^(0.1*lv - 1)
		智力型（法师）
		基础物理dps（基础值）=成长度 *力量*0.02 +  20*1.5^(0.1*lv - 1)
		"""
		ptype = Formulas.getType( species )
		if ptype == csdefine.PET_TYPE_STRENGTH:
			return ability * strength * 0.025 + 20 * 1.5 ** ( 0.1 * level - 1 )
		elif ptype == csdefine.PET_TYPE_BALANCED:
			return ability *  0.02 * ( strength  + dexterity  ) + 25 * 1.5 ** ( 0.1 * level - 1 )
		elif ptype == csdefine.PET_TYPE_SMART:
			return ability * ( strength * 0.01 + dexterity * 0.02 ) + 25.75 * 1.5 ** ( 0.1 * level - 1 )
		elif ptype == csdefine.PET_TYPE_INTELLECT:
			return ability * strength * 0.02 + 20 * 1.5 ** ( 0.1 * level - 1 )
		raise "pet type %i is not exist!" % ptype

	# ---------------------------------------
	def getHitSpeed( self, species ) :
		"""
		获取基础攻击速度
		@type				species : MSCRO DEFINATION
		@param				species : 宠物种类
		"""
		return self.__hitSpeeds[self.getType( species )]

	def getMinDamage( self, species, dps ) :
		"""
		获取基础最小物理攻击力
		@type				species : MSCRO DEFINATION
		@param				species : 宠物种类
		@type				dps		: int
		@param				dps		: 物理 dps

		宠物物理攻击力（基础值）= dps*攻击速度
		得出攻击力（计算值）之后，在攻击目标的时候：
		最小攻击力=攻击力*（1-dps波动）
		最大攻击力=攻击力*（1+dps波动）
		"""
		ptype = self.getType( species )
		baseDamage = dps * self.__hitSpeeds[ptype]	# 物理攻击力
		return baseDamage * ( 1 - self.__flipDPS[ptype] )

	def getMaxDamage( self, species, dps ) :
		"""
		获取基础最大物理攻击力
		@type				species : MSCRO DEFINATION
		@param				species : 宠物种类
		@type				dps		: int
		@param				dps		: 物理 dps
		"""
		ptype = self.getType( species )
		baseDamage = dps * self.__hitSpeeds[ptype]	# 物理攻击力
		return baseDamage * ( 1 + self.__flipDPS[ptype] )

	def getMagicDamage( self, ability, species, intellect, level ) :
		"""
		获取基础法术攻击力

		智力型
		宠物法术攻击力（基础值）=成长度*智力*0.0213 + 27.5 * 1.5 ** ( 0.1 * level - 1 )
		力量型、均衡型、敏捷型
		宠物法术攻击力（基础值）=成长度*智力*0.02 + 20 * 1.5 ** ( 0.1 * level - 1 )
		"""
		ptype = self.getType( species )
		if ptype == csdefine.PET_TYPE_INTELLECT:
			return ability * intellect  * self.__magicHitRadix[ptype] +  27.5 * 1.5 ** ( 0.1 * level - 1 )
		else:
			return ability * intellect  * self.__magicHitRadix[ptype] +  20 * 1.5 ** ( 0.1 * level - 1 )

	# ---------------------------------------
	@staticmethod
	def __getLevelSeg( lv ) :
		"""
		获取等级分段( 从 0 开始 )
		@type					lv : int
		@param					lv : 宠物等级
		@rtype					   : int
		@return					   : 等级所属的等级段
		"""
		return ( lv - 1 ) / 30

	@staticmethod
	def __getlevelBaseValue( lv ) :
		"""
		获取等级分段值( 1～30 : lv - 1 )、( 31 ～ 60 : lv - 30 ) ……
		@type					lv : int
		@param					lv : 宠物等级
		@rtype					   : int
		@return					   : 等级所属的等级参数值
		"""
		if lv <= 30 :
			return lv - 1
		return lv - ( Formulas.__getLevelSeg( lv ) * 30 )

	def getDoubleHitProbability( self, species, level, dexterity, ability ) :
		"""
		获取物理基础暴击率
		@type				species	  : MACRO DEFINATION
		@param				species	  : 宠物种类
		@type				level	  : int
		@param				level	  : 宠物等级
		@type				dexterity : MACRO DEFINATION
		@param				dexterity : 敏捷值
		"""
		if level < 1 or level > PetLevelEXP.getMaxLevel() :
			ERROR_MSG( "the pet's level is less than 1 or large than max level!" )
			return 0

		ptype = self.getType( species )
		if ptype == csdefine.PET_TYPE_STRENGTH:
			return 0.03 + 0.12 * ability * dexterity /( 7600 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_BALANCED:
			return 0.05 + 0.2 * ability * dexterity /( 11875 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_SMART:
			return 0.06 + 0.24 * ability * dexterity /( 18817 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_INTELLECT:
			return 0.02 + 0.08 * ability * dexterity /( 8133 * 1.5 ** ( 0.1 * level - 1 ) )
		else:
			return 0


	def getMagicDoubleHitProbability( self, species, level, intellect, ability ) :
		"""
		获取法术基础暴击率
		@type				species	  : MACRO DEFINATION
		@param				species	  : 宠物种类
		@type				level	  : int
		@param				level	  : 宠物等级
		@type				intellect : MACRO DEFINATION
		@param				intellect : 智力
		"""
		if level < 1 or level > PetLevelEXP.getMaxLevel() :
			ERROR_MSG( "the pet's level is less than 1 or large than max level!" )
			return 0

		ptype = self.getType( species )
		if ptype == csdefine.PET_TYPE_STRENGTH:
			return 0.02 + 0.08 * ability * intellect /( 7600 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_BALANCED:
			return 0.05 + 0.2 * ability * intellect /( 11875 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_SMART:
			return 0.03 + 0.12 * ability * intellect /( 7527 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_INTELLECT:
			return 0.056 + 0.224 * ability * intellect /( 24531 * 1.5 ** ( 0.1 * level - 1 ) )
		else:
			return 0

	def getDodgeProbability( self, species, level, dexterity, ability ) :
		"""
		获取物理基础闪避率
		@type				species	  : MACRO DEFINATION
		@param				species	  : 宠物种类
		@type				level	  : int
		@param				level	  : 宠物等级
		@type				dexterity : MACRO DEFINATION
		@param				dexterity : 敏捷值

		0.03 + 0.12 * 成长度 * 敏捷 / (7600*1.5^(0.1*Lv - 1))
		0.03 + 0.12 * 成长度 * 敏捷 / (11875*1.5^(0.1*Lv - 1))
		0.03 + 0.12 * 成长度 * 敏捷 / (18817*1.5^(0.1*Lv - 1))
		0.03 + 0.12 * 成长度 * 敏捷 / (8177*1.5^(0.1*Lv - 1))
		"""
		if level < 1 or level > PetLevelEXP.getMaxLevel() :
			ERROR_MSG( "the pet's level is less than 1 or large than max level!" )
			return 0

		ptype = self.getType( species )
		if ptype == csdefine.PET_TYPE_STRENGTH:
			return 0.03 + 0.12 * ability * dexterity /( 7600 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_BALANCED:
			return 0.03 + 0.12 * ability * dexterity /( 11875 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_SMART:
			return 0.03 + 0.12 * ability * dexterity /( 18817 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_INTELLECT:
			return 0.03 + 0.12 * ability * dexterity /( 8177 * 1.5 ** ( 0.1 * level - 1 ) )
		else:
			return 0

	def getResistProbability( self, species, level, strength, ability ) :
		"""
		获取招架率
		@type				species	  : MACRO DEFINATION
		@param				species	  : 宠物种类
		@type				level	  : int
		@param				level	  : 宠物等级
		@type				strength : MACRO DEFINATION
		@param				strength : 力量

		0.07 + 0.28 * 成长度 * 力量 / (15200*1.5^(0.1*Lv - 1))
		0.04 + 0.16 * 成长度 * 力量 / (11875*1.5^(0.1*Lv - 1))
		0.026 + 0.104 * 成长度 * 力量 / (11290*1.5^(0.1*Lv - 1))
		0.032 + 0.128 * 成长度 * 力量 / (8177*1.5^(0.1*Lv - 1))
		"""
		if level < 1 or level > PetLevelEXP.getMaxLevel() :
			ERROR_MSG( "the pet's level is less than 1 or large than max level!" )
			return 0
		ptype = self.getType( species )
		if ptype == csdefine.PET_TYPE_STRENGTH:
			return 0.07 + 0.28 * ability * strength /( 15200 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_BALANCED:
			return 0.04 + 0.16 * ability * strength /( 11875 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_SMART:
			return 0.026 + 0.104 * ability * strength /( 11290 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_INTELLECT:
			return 0.032 + 0.128 * ability * strength /( 8177 * 1.5 ** ( 0.1 * level - 1 ) )
		else:
			return 0


	def __getProbability( self, paramData, property, denominator, level, ability ):
		"""
		根据属性和参数字典计算出物理暴击、法术暴击、闪避率、招架率，9:14 2009-3-5，wsf

		举例公式为：物理暴击率 = 1%+[宠物当前敏捷-15-2.2*29-3*30-4*30-4.8*30-8.2*（lv-120）] *成长度*3/1000000
		"""
		commonParam1 = paramData[ 0 ]
		commonParam2 = paramData[ 1 ]
		propertyParamList = paramData[ 2 ]

		count = level / 30		# 计算需要几个参数
		restLevel = level % 30	# 计算最后的等级段

		if count == 0:			# 如果等级段在1-29级，根据公式特殊处理
			restLevel -= 1
		if level == 30:			# 如果刚好是30级，根据公式特殊处理
			count = 0
			restLevel -= 1

		result1 = property - commonParam2

		# 30 - ( index ==0 and 1 or 0 )，如果宠物大于等于30级，propertyParamList第一个参数乘29
		for index in xrange( count ):
			result1 -= propertyParamList[ index ] * ( 30 - ( index == 0 and 1 or 0 ) )
		# restLevel * propertyParamList[ count - 1 ]，宠物级别除30的余数乘propertyParamList最后一个参数
		if count >= 5:
			result2 = 0
		else:
			result2 = restLevel * propertyParamList[ count ]
		return commonParam1 + ( result1 - result2 ) * ability * 3 / denominator

	# -------------------------------------------------
	# 其他公式
	# -------------------------------------------------
	@staticmethod
	def getDisplayName( species, uname, name ) :
		"""
		获取宠物显示的名称
		@type			species : MACRO DEFINATION
		@param			species : defined.py
		@type			uname	: str
		@param			uname	: uname
		@type			name	: str
		@param			name	: custom name
		@rtype					: str
		@return					: display name
		"""
		if name.strip() != "" : return name
		hierarchies = {}
		hierarchies[csdefine.PET_HIERARCHY_GROWNUP] = ShareTexts.PET_GROWNUP_DSP_NAME
		hierarchies[csdefine.PET_HIERARCHY_INFANCY1] = ShareTexts.PET_INFANCY1_DSP_NAME
		hierarchies[csdefine.PET_HIERARCHY_INFANCY2] = ShareTexts.PET_INFANCY2_DSP_NAME
		hierarchy = Formulas.getHierarchy( species )
#		return hierarchies[hierarchy] % uname
		return uname		# CSOL-11994 宠物uname不再与辈分等混淆在一起

	@staticmethod
	def getAddedEXP( currLevel, currEXP, value ) :
		"""
		获得 EXP 后将其转化为等级和剩余 EXP 值
		@type			currLevel : UINT8
		@param			currLevel : current level
		@type			currEXP	  : INT32
		@param			currEXP	  : current exp
		@type			value	  : INT32
		@param			value	  : the added exp value
		@rtype					  : tuple
		@return					  : ( new level, new exp )
		"""
		exp = currEXP + value
		expMax = PetLevelEXP.getEXPMax( currLevel )
		while exp >= expMax :
			exp -= expMax
			currLevel += 1
			expMax = PetLevelEXP.getEXPMax( currLevel )
			if expMax <= 0 :
				ERROR_MSG( "error exp max: %d" % expMax )
				break
		if currLevel > csconst.PET_LEVEL_UPPER_LIMIT :
			currLevel = csconst.PET_LEVEL_UPPER_LIMIT
			exp = PetLevelEXP.getEXPMax( currLevel )
		return currLevel, exp

	@staticmethod
	def getPosition( rolePos, roleYaw ) :
		"""
		获取宠物跟随玩家的位置
		@type				rolePos : Vector3
		@param				rolePos : the owner's position
		@type				roleYaw : float
		@param				roleYaw : the own's yaw
		@rtype						: Vector3
		@param						: the pet's postion apart from its owner
		"""
		return rolePos	# 直接返回玩家的坐标
		rx, ry, rz = rolePos
		keepDistance = csconst.PET_ROLE_KEEP_DISTANCE - 1.0
		x = rx + keepDistance * math.sin( roleYaw + math.pi/2 )
		z = rz + keepDistance * math.cos( roleYaw + math.pi/2 )
		return Math.Vector3( x, ry, z )



# --------------------------------------------------------------------
# global instances
# --------------------------------------------------------------------
formulas  = Formulas.instance()

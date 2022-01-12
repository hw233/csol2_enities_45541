# -*- coding: gb18030 -*-
# $Id: PetEpitome.py,v 1.58 2008-09-05 01:44:03 zhangyuxing Exp $
#
"""
implement pet epitome type

2007/07/01: writen by huangyongwei
2007/11/17: rewriten by huangyongwei and rename it from "PetEpitomeType.py" to "PetEpitome.py"
"""

import math
import BigWorld
import csdefine
import csstatus
import csconst
import csstring
import Const
import items as itemObject
import event.EventCenter as ECenter
import ShareTexts
from bwdebug import *
from LevelEXP import PetLevelEXP
from PetFormulas import formulas
from gbref import rds
from ItemsFactory import ObjectItem
from items.ItemDataList import ItemDataList

g_items = ItemDataList.instance()


# 宠物规格对应的计算常数
hierarchyMapVal = {	csdefine.PET_HIERARCHY_GROWNUP  : 1,	\
					csdefine.PET_HIERARCHY_INFANCY1 : 1.5,	\
					csdefine.PET_HIERARCHY_INFANCY2 : 2,	\
					}

# 宠物类型对应的攻击速度常数
typeMapHitSpeed = { csdefine.PET_TYPE_STRENGTH  : 1, \
					csdefine.PET_TYPE_BALANCED  : 1, \
					csdefine.PET_TYPE_SMART     : 1.5, \
					csdefine.PET_TYPE_INTELLECT : 1, \
					}

def calcProperty( baseVal, extraVal, percentVal, value ):
	"""
	创世基础计算总公式
	计算值=（基础值+附加值）*（1+加成）+加值
	@param baseVal: 基础值
	@param extraVal: 附加值
	@param percentVal: 加成
	@param value: 加值
	"""
	return ( baseVal + extraVal ) * ( 1 + percentVal ) + value



# --------------------------------------------------------------------
# implement pet epitome class
# --------------------------------------------------------------------
class PetEpitome :
	def __init__( self ) :
		self.__databaseID = 0
		self.__uname = ""
		self.__name = ""
		self.__modelNumber = ""
		self.__gender = csdefine.GENDER_MALE
		self.__species = csdefine.PET_HIERARCHY_GROWNUP | csdefine.PET_TYPE_STRENGTH	# 成年的力量型

		self.__level = 1
		self.__HP = 0
		self.__MP = 0
		self.__EXP = 0

		self.__corporeity = 0	# 体质
		self.__strength = 0		# 力量
		self.__intellect = 0	# 智力
		self.__dexterity = 0	# 敏捷

		self.__ec_corporeity = 0
		self.__ec_strength = 0
		self.__ec_intellect = 0
		self.__ec_dexterity = 0
		self.__ec_free = 0

		self.__ability = 0	# 基本灵气值？
		self.__nimbus = 0		# 灵气
		self.__calcaneus = 0	# 根骨
		self.__isBinded = 0  # 是否被绑定

		self.__character = csdefine.PET_CHARACTER_SUREFOOTED	# 性格，稳重的
		self.__procreated = False	# 生殖
		self.__life = 65535
		self.__joyancy = 100
		self.__attrSkillBox = []

		self.__mapPetID = 0
		self.__isCurse = False
		self.__isInVend = False		# 宠物是否在摆摊中
		self.__vendSellPrice = 0	# 宠物摆摊出售价格

		self.__takeLevel	= 0		# 可携带等级


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def databaseID( self ) :
		return self.__databaseID

	@property
	def name( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.getName()
		return formulas.getDisplayName( self.species, self.__uname, self.__name )

	@property
	def gender( self ) :
		return self.__gender

	@property
	def modelNumber( self ) :
		if self.hierarchy == csdefine.PET_HIERARCHY_INFANCY2:
			return self.__modelNumber + Const.PET_ATTACH_MODELNUM
		return self.__modelNumber

	@property
	def species( self ) :	# 类别？
		entity = self.getEntity()
		if entity is not None :
			return entity.species
		return self.__species

	@property
	def hierarchy( self ) :	# 辈分？
		return self.species & csdefine.PET_HIERARCHY_MASK

	@property
	def ptype( self ) :
		return self.species & csdefine.PET_TYPE_MASK

	# ---------------------------------------
	@property
	def level( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.level
		return self.__level

	@property
	def HP( self ) :
		entity = self.getEntity()
		hp = self.__HP
		if entity is not None :
			hp = entity.getHP()
		else:
			return self.HPMax
		return min( hp, self.HPMax )

	@property
	def HPMax( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.getHPMax()
		return formulas.getBaseHPMax(self.corporeity, self.__ability, self.__level)

	@property
	def MP( self ) :
		entity = self.getEntity()
		mp = self.__MP
		if entity is not None :
			mp = entity.getMP()
		else:
			return self.MPMax
		return min( mp, self.MPMax )

	@property
	def MPMax( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.getMPMax()
		return formulas.getBaseMPMax(self.intellect, self.__ability, self.__level)

	@property
	def EXP( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.EXP
		return self.__EXP

	@property
	def EXPMax( self ) :
		return PetLevelEXP.getEXPMax( self.level )

	# ---------------------------------------
	@property
	def corporeity( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.corporeity
		return self.__corporeity

	@property
	def strength( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.strength
		return self.__strength

	@property
	def intellect( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.intellect
		return self.__intellect

	@property
	def dexterity( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.dexterity
		return self.__dexterity

	# -----------------------------
	@property
	def corporeityRadix( self ) :
		return formulas.getSndAttrValue( "corporeity", self.species, self.level, self.nimbus )

	@property
	def strengthRadix( self ) :
		return formulas.getSndAttrValue( "strength", self.species, self.level, self.nimbus )

	@property
	def intellectRadix( self ) :
		return formulas.getSndAttrValue( "intellect", self.species, self.level, self.nimbus )

	@property
	def dexterityRadix( self ) :
		return formulas.getSndAttrValue( "dexterity", self.species, self.level, self.nimbus )

	# -----------------------------
	# 使用过的次数
	@property
	def ec_corporeity( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.ec_corporeity
		return self.__ec_corporeity

	@property
	def ec_strength( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.ec_strength
		return self.__ec_strength

	@property
	def ec_intellect( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.ec_intellect
		return self.__ec_intellect

	@property
	def ec_dexterity( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.ec_dexterity
		return self.__ec_dexterity

	# 剩余的次数
	@property
	def ecrm_corporeity( self ) :
		return formulas.getFixedEnhanceCount( self.species, "corporeity", self.level ) - self.ec_corporeity

	@property
	def ecrm_strength( self ) :
		return formulas.getFixedEnhanceCount( self.species, "strength", self.level ) - self.ec_strength

	@property
	def ecrm_intellect( self ) :
		return formulas.getFixedEnhanceCount( self.species, "intellect", self.level ) - self.ec_intellect

	@property
	def ecrm_dexterity( self ) :
		return formulas.getFixedEnhanceCount( self.species, "dexterity", self.level ) - self.ec_dexterity

	# -----------------------------
	# 自由强化
	# 使用过的次数
	@property
	def ec_free( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.ec_free
		return self.__ec_free

	# 剩余次数
	@property
	def ecrm_free( self ) :											  	# add by gjx 2009-3-27
		return formulas.getFreeEnhanceCount( self.level ) - self.ec_free

	# ---------------------------------------
	@property
	def ability( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.ability
		return self.__ability

	@property
	def isBinded( self ) :
		return self.__isBinded

	@property
	def nimbus( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.nimbus
		return self.__nimbus

	@property
	def nimbusMax( self ) :
		return formulas.getMaxNimbus( self.level )

	@property
	def calcaneus( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.calcaneus
		return self.__calcaneus

	@property
	def calcaneusMax( self ) :
		return formulas.getCalcaneusMax( self.nimbus )

	# ---------------------------------------
	@property
	def character( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.character
		return self.__character

	@property
	def procreated( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.procreated
		return self.__procreated

	@property
	def life( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.life
		return self.__life

	@property
	def lifeMax( self ) :
		return csconst.PET_LIFE_UPPER_LIMIT

	@property
	def joyancy( self ) :
		entity = self.getEntity()
		if entity is not None :
			return entity.joyancy
		return self.__joyancy

	@property
	def joyancyMax( self ) :
		return csconst.PET_JOYANCY_UPPER_LIMIT

	# ---------------------------------------
	@property
	def conjured( self ) :
		return self.__mapPetID > 0

	# -------------------------------------------------
	@property
	def strGender( self ) :
		return ShareTexts.GENDER_MALE if self.__gender == csdefine.GENDER_MALE else ShareTexts.GENDER_FEMALE

	@property
	def strSpecies( self ) :
		return csconst.pet_ch_species[self.species]

	@property
	def strCharacter( self ) :
		return Const.pet_ch_characters[self.character]

	@property
	def strJoyancy( self ) :
		if self.joyancy < 60 :
			return ShareTexts.PET_JOYANCY_ANGRY
		if self.joyancy < 70 :
			return ShareTexts.PET_JOYANCY_DEPRESSED
		if self.joyancy < 80 :
			return ShareTexts.PET_JOYANCY_NORMAL
		return ShareTexts.PET_JOYANCY_WELL

	@property
	def strProcreated( self ) :
		return self.procreated  and ShareTexts.QUERY_YES or ShareTexts.QUERY_NO

	@property
	def skills( self ) :
		entity = self.getEntity()
		if entity is not None :
			return BigWorld.player().pcg_getPetSkillList()
		return self.__attrSkillBox[:]

	# -------------------------------------------------
	@property
	def resistGiddyProbability( self ) :	# 抵抗眩晕
		entity = self.getEntity()
		if entity is not None :
			return entity.resist_giddy_probability
		return 0.05

	@property
	def resistFixProbability( self ) :	# 抵抗混乱
		entity = self.getEntity()
		if entity is not None :
			return entity.resist_fix_probability
		return 0.05

	@property
	def resistChenmoProbability( self ) :	# 抵抗定身
		entity = self.getEntity()
		if entity is not None :
			return entity.resist_chenmo_probability
		return 0.05

	@property
	def resistSleepProbability( self ) :	# 抵抗睡眠
		entity = self.getEntity()
		if entity is not None :
			return entity.resist_sleep_probability
		return 0.05

	# 物理战斗属性
	@property
	def damage( self ):	# 物理伤害值
		entity = self.getEntity()
		if entity is not None :
			return int( ( entity.damage_min + entity.damage_max ) / 2 )
		percent = 1 + formulas.getJoyancyEffect( self.joyancy ) # 加上快乐度的影响
		dps = formulas.getBasePhysicsDPS( self.species, self.ability, self.strength, self.dexterity, self.level ) * percent
		minDamage = int ( formulas.getMinDamage( self.species, dps ) )
		maxDamage = int ( formulas.getMaxDamage( self.species, dps ) )
		return int( ( minDamage + maxDamage ) / 2 )

	@property
	def armor( self ):	# 物理防御
		entity = self.getEntity()
		if entity is not None :
			return entity.armor
		percent = 1 + formulas.getJoyancyEffect( self.joyancy ) # 加上快乐度的影响
		return max( int( math.ceil( formulas.getPhysicsArmorRadies( self.species, self.level, self.ability ) * percent ) ), 0 )

	@property
	def double_hit_probability( self ):	# 物理倍击概率
		entity = self.getEntity()
		if entity is not None :
			return entity.double_hit_probability
		return formulas.getDoubleHitProbability( self.species, self.level, self.dexterity, self.ability )

	@property
	def resist_hit_probability( self ):	# 抵抗物理攻击概率
		entity = self.getEntity()
		if entity is not None :
			return entity.resist_hit_probability
		return formulas.getResistProbability( self.species, self.level, self.strength, self.ability )

	# 法术战斗属性
	@property
	def magic_damage( self ):	# 法术伤害
		entity = self.getEntity()
		if entity is not None :
			return entity.magic_damage
		percent = 1 + formulas.getJoyancyEffect( self.joyancy ) # 加上快乐度的影响
		return  int( math.ceil( formulas.getMagicDamage( self.ability, self.species, self.intellect, self.level ) * percent ) )

	@property
	def magic_armor( self ):	# 法术防御
		entity = self.getEntity()
		if entity is not None :
			return entity.magic_armor
		percent = 1 + formulas.getJoyancyEffect( self.joyancy ) # 加上快乐度的影响
		return max( int( math.ceil( formulas.getMagicArmorRadies( self.species, self.level, self.ability ) * percent ) ), 0 )

	@property
	def dodge_probability( self ):	# 闪避概率
		entity = self.getEntity()
		if entity is not None :
			return entity.dodge_probability
		return formulas.getDodgeProbability( self.species, self.level, self.dexterity, self.ability )

	@property
	def magic_double_hit_probability( self ):	# 法术倍击概率
		entity = self.getEntity()
		if entity is not None :
			return entity.magic_double_hit_probability
		return formulas.getMagicDoubleHitProbability( self.species, self.level, self.intellect, self.ability )

	@property
	def isInVend( self ) :
		return self.__isInVend

	@property
	def vendSellPrice( self ) :
		return self.__vendSellPrice

	@property
	def takeLevel( self ):
		entity = self.getEntity()
		if entity is not None:
			return entity.takeLevel
		return self.__takeLevel

	# ----------------------------------------------------------------
	# mathods for packing / un packing
	# ----------------------------------------------------------------
	def getDictFromObj( self, epitome ) :
		return self.__dict__

	def createObjFromDict( self, dict ) :
		epitome = PetEpitome()
		for attrName, value in dict.items() :
			epitome.onUpdateAttr( attrName, value, True )
		return epitome

	def isSameType( self, obj ) :
		return isinstance( obj, PetEpitome )

	# ----------------------------------------------------------------
	# callback methods
	# ----------------------------------------------------------------
	def onUpdateAttr( self, attrName, value, isInit = False ) :
		fullName = "_PetEpitome__" + attrName
		if not hasattr( self, fullName ) : return
		oldValue = getattr( self, fullName )
		setattr( self, fullName, value )
		if isInit : return
		notifier = getattr( self, "set_" + attrName, None )
		if notifier is not None :
			notifier( oldValue )

	# -------------------------------------------------
	def set_name( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "name" )

	def set_species( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "species" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "nimbusMax" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "strengthRadix" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "intellectRadix" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "dexterityRadix" )
		if self.name == "" :
			self.set_name( "" )

	def set_level( self, old ) :
		if self.level == old : return
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "level" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "EXPMax" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "nimbusMax" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "calcaneusMax" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "strengthRadix" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "intellectRadix" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "dexterityRadix" )
		ECenter.fireEvent( "EVT_ON_PET_LEVEL_CHANGE", self.databaseID, self.level )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ecrm_corporeity" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ecrm_strength" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ecrm_dexterity" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ecrm_intellect" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ecrm_free" )

	def set_HP( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "HP" )

	def set_MP( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "MP" )

	def set_EXP( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "EXP" )

	def set_corporeity( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "corporeity" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "HPMax" )

	def set_strength( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "strength" )

	def set_intellect( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "intellect" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "MPMax" )

	def set_dexterity( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "dexterity" )

	def set_ec_corporeity( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ec_corporeity" )

	def set_ec_strength( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ec_strength" )

	def set_ec_intellect( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ec_intellect" )

	def set_ec_dexterity( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ec_dexterity" )

	def set_ec_free( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ec_free" )

	def set_baseNimbus( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "nimbus" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "calcaneusMax" )

	def set_nimbus( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "nimbus" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "calcaneusMax" )

	def set_calcaneus( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "calcaneus" )

	def set_character( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "character" )

	def set_procreated( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "procreated" )

	def set_life( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "life" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "lifeMax" )

	def set_joyancy( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "joyancy" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "joyancyMax" )

	def set_mapPetID( self, old ) :
		if self.__mapPetID > 0 :
			ECenter.fireEvent( "EVT_ON_PET_CONJURED", self.databaseID )
		else :
			ECenter.fireEvent( "EVT_ON_PET_WITHDRAWED", self.databaseID )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "resistGiddyProbability" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "resistFixProbability" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "resistChenmoProbability" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "resistSleepProbability" )
		# 战斗属性
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "damage" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "armor" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "double_hit_probability" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "resist_hit_probability" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "magic_damage" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "magic_armor" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "dodge_probability" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "magic_double_hit_probability" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "takeLevel" )

	def set_isBinded( self, old ):
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "isBinded" )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getEntity( self ) :
		return BigWorld.entities.get( self.__mapPetID, None )

	# -------------------------------------------------
	def rename( self, newName ) :
		player = BigWorld.player()
		if player.pcg_isActPet( self.databaseID ):
			player.statusMessage( csstatus.PET_RENAME_FAIL_ACTIVITY )
			return
		illegalWord = rds.wordsProfanity.searchNameProfanity( newName )
		if illegalWord is not None :
			player.statusMessage( csstatus.PET_RENAME_FAIL_ILLEGAL_WORD, illegalWord )
		elif len( csstring.toWideString( newName ) ) > csconst.PET_NAME_MAX_LENGTH :
			player.statusMessage( csstatus.PET_RENAME_FAIL_OVERLONG )
		else :
			player.cell.pcg_renamePet( self.databaseID, newName )

	def conjure( self ) :
		player = BigWorld.player()
		playerLevel = player.level
		if self.conjured :
			player.statusMessage( csstatus.PET_CONJURE_FAIL_CONJURED )
		elif playerLevel < self.__takeLevel:			#  玩家低于宠物可挈带等级也不能召唤 by姜毅
			player.statusMessage( csstatus.SKILL_PET_NOT_TAKE_LEVEL )
		elif playerLevel < self.level - csconst.PET_CONJURE_OVER_LEVEL :
			player.statusMessage( csstatus.PET_CONJURE_FAIL_LESS_LEVEL )
		elif self.life <= 0 :
			player.statusMessage( csstatus.PET_CONJURE_FAIL_LESS_LIFE )
		elif self.joyancy < formulas.getConjureJoyancyLimit() :
			player.statusMessage( csstatus.PET_CONJURE_FAIL_LESS_JOYANCY, formulas.getConjureJoyancyLimit() )
		elif player.isSunBathing():
			player.statusMessage( csstatus.PET_CONJURE_FAIL_SUN_BATHING )
		elif player.getState() == csdefine.ENTITY_STATE_DANCE or player.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:
			player.statusMessage( csstatus.JING_WU_SHI_KE_CANNOT_CONJURED )
		elif player.effect_state & csdefine.EFFECT_STATE_PROWL:
			player.statusMessage( csstatus.PET_CONJURE_FAIL_SNAKE )
		elif player.effect_state & csdefine.EFFECT_STATE_WATCHER:
			player.statusMessage( csstatus.PET_CONJURE_FAIL_WATCHER )
		elif player.pcg_getActPet() and player.pcg_getActPet().state == csdefine.ENTITY_STATE_FIGHT:
			player.statusMessage( csstatus.PET_CONJURE_FAIL_IN_FIGHT )
		else :
			BigWorld.player().cell.pcg_conjurePet( self.databaseID )

	def conjureForAutoFight( self, player ):
		"""
		自动战斗自动召唤用接口 by 姜毅
		"""
		playerLevel = player.level
		if self.conjured:
			return -1
		elif playerLevel < self.__takeLevel:
			return csstatus.SKILL_PET_NOT_TAKE_LEVEL
		elif playerLevel < self.level - csconst.PET_CONJURE_OVER_LEVEL:
			return csstatus.PET_CONJURE_FAIL_LESS_LEVEL
		elif self.life <= 0:
			return -1
		elif self.joyancy < formulas.getConjureJoyancyLimit():
			return csstatus.PET_JOY_NOT_ENOUGH
		elif player.isSunBathing():
			return -1
		elif player.getState() == csdefine.ENTITY_STATE_DANCE or player.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:
			return -1
		else :
			player.cell.pcg_conjurePet( self.databaseID )
		return 1

	def withdraw( self ) :
		if not self.conjured :
			BigWorld.player().statusMessage( csstatus.PET_WITHDRAW_FAIL_NOT_OUT )
		else :
			BigWorld.player().cell.pcg_withdrawPet()

	def free( self ) :
		BigWorld.player().cell.pcg_freePet( self.databaseID )

	def enhance( self, etype, attrName, isCurse, stoneItemUid, symbolItemUid ) :
		if not self.conjured :
			BigWorld.player().statusMessage( csstatus.PET_ENHANCE_FAIL_NOT_OUT )
		else :
			BigWorld.player().cell.pcg_enhancePet( etype, attrName, isCurse, stoneItemUid, symbolItemUid )

	def addLife( self ) :
		player = BigWorld.player()
		if self.life == self.lifeMax:
			player.statusMessage( csstatus.SKILL_PET_LIFE_FILL )
			return

		item = None
		for itemID in csconst.PET_ADD_LIFE_ITEMS:
			findItem = player.findItemFromNKCK_( itemID )
			if findItem:
				item = findItem
				break
		if item is None:
			player.statusMessage( csstatus.SKILL_PET_LIFE_ITEM_NO_EXIST )
			return
		player.cell.pcg_addLife( self.databaseID )

	def addJoyancy( self ) :
		"""
		驯养
		"""
		player = BigWorld.player()
		if self.joyancy >= 100:
			player.statusMessage( csstatus.SKILL_PET_JOYANCY_FILL )
			return

		index = ( self.level - 1 ) / 30			# 计算宠物应该使用哪类布娃娃 分为5类,每30级为一类 如 60级 属于2类(索引为1)
		itemID = csconst.pet_joyancy_items[index]
		item = player.findItemFromNKCK_( itemID )# 布娃娃
		if item:
			player.cell.pcg_addJoyancy( self.databaseID )
		else:
			player.statusMessage( csstatus.SKILL_PET_JOYANCY_ITEM_NO_EXIST ,g_items.id2name( itemID ) )

	def addJoyanceForAutoFight( self, player ):
		"""
		自动战斗用驯养接口 by 姜毅
		"""
		if self.joyancy >= 100: return
		index = ( self.level - 1 ) / 30			# 计算宠物应该使用哪类布娃娃 分为5类,每30级为一类 如 60级 属于2类(索引为1)
		itemID = csconst.pet_joyancy_items[index]
		item = player.findItemFromNKCK_( itemID )# 布娃娃
		if item:
			player.cell.pcg_addJoyancy( self.databaseID )
		else:
			return False
		return True

	def getStoneInfo( self, attrName ):
		"""
		获个强化属性对应魂魄石信息
		"""
		stoneInfo = None
		maxQuality = -1
		player = BigWorld.player()
		itemlist = csconst.pet_enhance_stones.get( attrName, () )
		for itemID in itemlist :
			items = player.findItemsByIDFromNKCK( itemID )
			for item in items :
				if not item.isFull() : continue
				itemInfo = ObjectItem( item )
				quality = itemInfo.quality
				if quality > maxQuality :		# 查找最高品质的
					stoneInfo = itemInfo
					maxQuality = quality
		return stoneInfo

	def getSymbolInfo( self ): # 获得精炼符，点化符信息
		player = BigWorld.player()
		for itemID in csconst.PET_SMELT_ITEMS:
			item = player.findItemFromNKCK_( itemID )
			if item: return ObjectItem( item )
		return None

	# ------------------------------- wsf add 12:13 2008-6-4 ---------------------------
	def getLevelMap( self ):
		"""
		根据等级获得计算暴击、法术暴击、躲避、招架概率的公式所对应的级别

		return: 120 or 90 or 60 or 30 or 1
		"""
		if self.level > 150:
			DEBUG_MSG( "目前还没有对大于150级的宠物的计算公式。" )
			return 120
		if self.level <= 30 :
			return 1
		return ( ( self.level - 1 ) / 30 ) * 30

# --------------------------------------------------------------------
# pickle instances
# --------------------------------------------------------------------
instance = PetEpitome()

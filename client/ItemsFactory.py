# -*- coding: gb18030 -*-
#
# $Id: ItemsFactory.py,v 1.49 2008-08-20 09:39:30 fangpengjun Exp $

"""
implement items( kitbagitem, skillitem, buffitem, quickbaritem ) factory

2007/04/28 : writen by huangyongwei
"""

import os
import re
import math
import time
import Const

import csol
import BigWorld
import Math
import csdefine
import csstatus
import csconst
import TextFormatMgr
import skills
import event.EventCenter as ECenter
import SkillTargetObjImpl
import GUIFacade
import ShareTexts
import config.client.labels.ItemsFactory as lbs_ItemsFactory

from bwdebug import *
from AbstractTemplates import Singleton
from LivingConfigMgr import LivingConfigMgr
from gbref import rds
from Time import Time

from guis import util
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine

lvcMgr = LivingConfigMgr.instance()

from TongSkillResearchData import TongSkillResearchData
tongSkillResearch = TongSkillResearchData.instance()

from LabelGather import labelGather
import config.client.labels.GUIFacade as lbDatas
from GUIFacade.LearnSkillFacade import LearningSkill
from config.skill.SkillTeachData import Datas as skTeachDatas
from config.skill.Skill.SkillDataMgr import Datas as skDatas
import TongDatas
tongSkillDatas = TongDatas.tongSkill_instance()

_icon_mapping_36 = util.getIconMapping( ( 36, 36 ) )

# 快捷栏中技能对目标相关非法的条件列表 (决定变暗的条件)
SKILL_STATE_LIST = [
						csstatus.SKILL_UNKNOW,
						csstatus.SKILL_CANT_CAST,
						csstatus.SKILL_TOO_FAR,
						csstatus.SKILL_TOO_NEAR,
						#csstatus.SKILL_CAST_ENTITY_ONLY,
						csstatus.SKILL_CAST_ENTITY_LEVE_MIN,
						csstatus.SKILL_CAST_ENTITY_LEVE_MAX,
						csstatus.SKILL_CANT_ITEM_ONLY,
						csstatus.SKILL_CAST_OBJECT_INVALID,
						csstatus.SKILL_CAST_OBJECT_NOT_ENEMY,
						csstatus.SKILL_OUTOF_MANA,
						csstatus.SKILL_MISSING_ITEM,
						csstatus.SKILL_INTONATING,
						csstatus.SKILL_NOT_READY,
						csstatus.SKILL_WEAPON_EQUIP_REQUIRE,
						csstatus.SKILL_ITEM_INTONATING,
						csstatus.SKILL_ITEM_NOT_READY,
						csstatus.SKILL_NOT_IN_POSTURE,
						csstatus.GROUND_STATUS_NEEDED,
						csstatus.SKILL_OUTOF_VITALITY,
						csstatus.SKILL_OUTOF_HP,
						csstatus.SKILL_OUTOF_CombatCount,
						csstatus.SKILL_IN_DEAD,
						csstatus.CIB_MSG_TEMP_CANT_USE_ITEM,
						csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT,
						csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP,
						csstatus.SKILL_IN_CAST_BAD_STATE_DUMB,
						csstatus.SKILL_IN_CAST_BAD_STATE_FIX,
]
def getValidIcon( iconPath ):
	defIcon = "icons/tb_yw_sj_005.dds"
	exts = [".dds", ".tga"]
	f = os.path.splitext( iconPath )
	if len( f ) < 2 : return defIcon
	for ext in exts :
		icon = f[0] + ext
		if csol.resourceExists( icon ) :
			return icon
	return defIcon

class ItemsFactory( Singleton ) :
	def __init__( self ) :
		Singleton.__init__( self )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getActionSkillItems( self ) :
		"""
		获取所有行为技能
		"""
		itemInfos = []
		for skID in csconst.SKILL_ID_ACTIONS :
			try:
				baseItem = skills.getSkill( skID )
				itemInfos.append( SkillItem( baseItem ) )
			except:
				ERROR_MSG( "actionSkill %d not found。" % skID )
				continue
		return itemInfos


# ------------------------------------------------------------------------------
# implement item information base class
# ------------------------------------------------------------------------------
class ItemInfo( object ) :

	def __init__( self, baseItem ) :
		object.__init__( self )

		self.id_ = 0
		self.name_ = ""
		self.activeState_ = 0
		self.update( baseItem )				# map the base item


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isActive( self ):
		return self.activeState_ == 0

	def update( self, baseItem ) :
		"""
		update the item
		@type			baseItem : the base item
		@param			baseItem : the mapping base item
		@return					 : None
		"""
		assert baseItem is not None
		self.__baseItem = baseItem

	def isCooldownType( self, cooldownType ) :
		"""
		indicate whether the item is in cooldown state
		@type			cooldownType :
		@param			cooldownType :
		@rtype						 : bool
		@return						 : if it is in cooldown state, it will return true
		"""
		return False

	def validTarget( self ):
		"""
		判断该Item是否能够对 receiver 起作用
		"""
		return csstatus.SKILL_GO_ON

	def query( self, attrName, defValue = None ) :
		"""
		query attribute value
		@type			attrName : str
		@param			attrName : attribute name
		@type			defValue : all types
		@param			defValue : if query nothing, it will be returned
		@rtype					 : all types
		@return					 : attribute value you wanted to query
		"""
		try :
			return self.baseItem.query( attrName, defValue )
		except AttributeError :
			return defValue

	# -------------------------------------------------
	def getCooldownInfo( self ) :
		"""
		获取 cooldown 信息
		@rtype				: tuple
		@return				: ( cooldown 的剩余时间，cooldown 的剩余百分比 )
		"""
		player = BigWorld.player()
		if not player.isPlayer() : return 0, 0
		spell = self.getSpell()
		if spell is None or not spell.getType() in csconst.BASE_SKILL_TYPE_SPELL_LIST: return 0, 0
		totalTime, endTime = spell.getCooldownData( player )
		leaveTime = endTime - Time.time()
		if leaveTime <= 0 or totalTime <= 0 : return 0, 0
		leaveRate = leaveTime * 1.0 / totalTime
		return leaveTime, leaveRate

	def checkUseStatus( self ) :
		"""
		检查可使用的情况
		"""
		return self.__baseItem.checkUseStatus( BigWorld.player() )

	# -------------------------------------------------
	def spellable( self ) :
		return True

	def getSpell( self ) :
		return None

	def spell( self ) :
		"""
		spell item
		"""
		pass

	def spellToSelf( self ) :
		"""
		spell item to self
		"""
		pass

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def baseItem( self ) :
		return self.__baseItem

	# ---------------------------------------
	@property
	def id( self ) :
		return self.id_

	@property
	def name( self ) :
		return self.name_

	@property
	def icon( self ) :
		global _icon_mapping_36
		return ( "", _icon_mapping_36 )

	@property
	def description( self ) :
		return ""

	@property
	def countable( self ) :
		return False

	@property
	def amount( self ) :
		return 0


# --------------------------------------------------------------------
# implement kitbag item class
# --------------------------------------------------------------------
class ObjectItem( ItemInfo ) :
	def __init__( self, baseItem ) :
		ItemInfo.__init__( self, baseItem )

		self.price_ = 0						# price of the object item

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, baseItem ) :
		ItemInfo.update( self, baseItem )
		self.id_ = baseItem.id
		self.name_ = baseItem.name
		self.price_ = baseItem.getPrice()

	# -------------------------------------------------
	def isCooldownType( self, cooldownType ) :
		self.baseItem.isCooldownType( cooldownType )

	def validTarget( self ):
		"""
		判断该Item是否能够对 targetEntity 起作用
		"""
		target = BigWorld.player().targetEntity
		spellID = self.query( "spell", None )
		if spellID is None : return csstatus.SKILL_GO_ON
		skillCastObjCondition = skills.getSkill( spellID ).getCastObject()
		player = BigWorld.player()
		target = SkillTargetObjImpl.createTargetObjEntity( skillCastObjCondition.convertCastObject( player, target ) )
		state = skills.getSkill( spellID ).useableCheck( player, target )
		if state in SKILL_STATE_LIST:
			return state
		return csstatus.SKILL_GO_ON

	def getSpell( self ) :
		spellID = self.query( "spell", None )
		if spellID is None : return None
		return skills.getSkill( spellID )

	def spell( self ) :
		tempItems = BigWorld.player().findItemsByIDFromNKCK( self.baseItem.id )
		tempAmount = tempItems[0].getAmount()
		tempItem = self.baseItem
		if len( tempItems ) > 1:
			for item in tempItems:
				if item.getAmount() < tempAmount and item.getAmount()>0 :
					tempItem = item
		GUIFacade.autoUseKitbagItem( tempItem )

	def spellToSelf( self ) :
		"""
		spell item to self
		"""
		self.spell()

	def getCooldownInfo( self ) :
		player = BigWorld.player()
		if not player.isPlayer() : return 0, 0
		spell = self.getSpell()
		if spell is None or not (spell.getType() == csdefine.BASE_SKILL_TYPE_ITEM): # 物品对应的技能类型一定是BASE_SKILL_TYPE_ITEM
			return 0, 0

		totalTime, endTime = 0, 0
		springUsedCD = self.baseItem.query( "springUsedCD", {} )
		for cd in springUsedCD:
			cdData = player.getCooldown( cd )
			t = cdData[1]
			e = cdData[3]
			if e > Time.time() and e > endTime :
				totalTime, endTime = t, e

		springUsedCD = self.baseItem.query( "springIntonateOverCD", {} )
		for cd in springUsedCD:
			cdData = player.getCooldown( cd )
			t = cdData[1]
			e = cdData[3]
			if e > Time.time() and e > endTime :
				totalTime, endTime = t, e

		leaveTime = endTime - Time.time()
		if leaveTime <= 0 or totalTime <= 0 : return 0, 0
		leaveRate = leaveTime * 1.0 / totalTime
		return leaveTime, leaveRate


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def kitbagID( self ) :
		kitbag = self.kitbag
		if kitbag is None : return None
		return kitbag

	@property
	def kitbag( self ) :
		return self.baseItem.getOrder()/csdefine.KB_MAX_SPACE

	@property
	def orderID( self ) :
		return self.baseItem.getOrder()%csdefine.KB_MAX_SPACE

	@property
	def uid( self ) :
		return self.baseItem.getUid()

	@property
	def icon( self ) :
		global _icon_mapping_36
		icon = self.baseItem.icon()
		return ( getValidIcon( icon ), _icon_mapping_36 )

	@property
	def description( self ) :
		return self.baseItem.description( BigWorld.player() )

	@property
	def countable( self ) :
		return True

	@property
	def amount( self ) :
		return self.baseItem.getAmount()

	# ---------------------------------------
	@property
	def price( self ) :
		return self.baseItem.getPrice()

	@property
	def isEquip( self ) :
		return self.baseItem.isEquip()

	@property
	def hardiness( self ) :
		if not self.isEquip : return 1
		return self.baseItem.query( "eq_hardiness", 1 )

	@property
	def hardinessMax( self ) :
		if not self.isEquip : return 1
		return float( self.baseItem.query( "eq_hardinessMax", 1 ) )

	@property
	def eq_hardinessLimit( self ) :
		if not self.isEquip : return 1
		return float( self.baseItem.query( "eq_hardinessLimit", 1 ) )

	@property
	def quality( self ):
		return self.baseItem.getQuality()

	@property
	def level( self ):
		return self.baseItem.getLevel()

	@property
	def reqLevel( self ):
		return self.baseItem.getReqLevel()

	@property
	def itemType( self ):
		return self.baseItem.getType()

	@property
	def invoiceType( self ): #NPC商品类型
		return self.baseItem.query( "invoiceType", 0 )

	@property
	def intensifyLevel( self ):
		return  self.baseItem.query( "eq_intensifyLevel", 0 )

# --------------------------------------------------------------------
# implement skill item class
# --------------------------------------------------------------------
class SkillItem( ItemInfo ) :
	def __init__( self, baseItem ) :
		ItemInfo.__init__( self, baseItem )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, baseItem ) :
		ItemInfo.update( self, baseItem )
		self.id_ = baseItem.getID()
		self.name_ = baseItem.getName()

	# -------------------------------------------------
	def isCooldownType( self, cooldownType ) :
		skill = self.baseItem
		if skill is None : return False
		if skill.getType() not in csconst.BASE_SKILL_TYPE_SPELL_LIST : return False
		return skill.isCooldownType( cooldownType )

	def validTarget( self ):
		"""
		判断该Item是否能够对 targetEntity 起作用
		"""
		player = BigWorld.player()
		target = player.targetEntity
		skillInst = skills.getSkill( self.id )
		targetInfo = skillInst.getCastObject().convertCastObject( player, target )
		from skills.Spell_Cursor import Spell_Cursor
		if not isinstance( skillInst, Spell_Cursor):
			spellTarget = SkillTargetObjImpl.createTargetObjEntity( targetInfo )
			state = skillInst.useableCheck( player, spellTarget )
			if state in SKILL_STATE_LIST:
				return state

		return csstatus.SKILL_GO_ON

	def getSpell( self ) :
		return self.baseItem

	def spell( self ) :
		DEBUG_MSG( "skill %d has been used." %  self.id )
		BigWorld.player().useSkill( self.id )

	def spellToSelf( self ) :
		"""
		spell item to self
		"""
		BigWorld.player().changeAttackState( Const.ATTACK_STATE_ONCE, self.id )
		#BigWorld.player().spellSkill( self.id, False, BigWorld.player() )
		DEBUG_MSG( "skill %d has been used." %  self.id )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def icon( self ) :
		global _icon_mapping_36
		icon = self.baseItem.getIcon()
		return ( getValidIcon( icon ), _icon_mapping_36 )

	@property
	def description( self ) :
		"""
		技能描述
		"""
		player = BigWorld.player()
		skill = self.baseItem
		desList = []		#记录该技能所有的描述信息
		learnSkill = LearningSkill( self.id_ )
		teachSkill = learnSkill.getSkill()
		colorFunc = lambda v : v and "c6" or "c3"
		requireManaDes = ""		# 法力消耗
		requireVitalityDes = ""	# 体力消耗
		requireHPDes = ""		# 生命消耗
		cdTimeString = ""		# 冷却时间
		distString = ""			# 施法距离
		intonateString = ""		# 吟唱时间
		postureString = ""		# 心法需求
		learnUpReqs = ""		# 学习需求/下一级
		reqRoleLevelStr = ""	# 需要玩家等级
		reqTongLevelStr = ""	# 需要玩家帮会等级
		reqPotentialStr = ""	# 需要潜能
		rePreSkStr = ""			# 需要前置技能
		learned = True
		nextSkID = 0
		reqSkills = []
		reqSkDict = {}
		isTeachSkill = str( self.id_ ).startswith("9")
		if isTeachSkill:
			learned = False
			skillID = teachSkill._spellTeach
			skill = skills.getSkill( skillID )
			learnUpReqs = labelGather.getText( "SkillList:main", "learnReqs" )
			nextSkID = skillID
		else:
			if skill.getLevel() < skill.getMaxLevel():
				learnUpReqs = labelGather.getText( "SkillList:main", "upgradeReqs" )
			if skill.getMaxLevel() <= 1:
				learnUpReqs = ""
			skData = skTeachDatas.get( self.id_, None )
			if skData:
				nextSkID = skData["nextLevelID"]
		
		skillName = skill.getName()		# 技能名字,颜色c46
		skillName = PL_Font.getSource( skillName , fc = "c46" )

		levelString = ""				# 技能等级，颜色默认为白色
		sleightString = ""				# 生活技能熟练度
		if self.level > 0:
			if not self.id_ in csconst.SKILL_ID_ACTIONS:
				levelString = lbs_ItemsFactory.LEVEL % self.level
		if lvcMgr._sDatas.has_key( self.id_ ):
			if self.id_ in player.skillList_:
				livingSk = player.livingskill.get( self.id_, (0, 0) )
				levelString = lvcMgr.getDesByLevel( self.id_, livingSk[1] ).split( "|" )[-1]
				sleightMax = lvcMgr.getMaxSleightByLevel( self.id_, livingSk[1] )
				sleighyStr = "%d/%d" % ( livingSk[0], sleightMax )
				sleightString = lbs_ItemsFactory.SKILLLV + PL_Font.getSource( sleighyStr, fc ="c6" )
		if self.id_ in tongSkillResearch._datas:
			if hasattr( skill, "_spellTeach" ):
				levelString = lbs_ItemsFactory.LEVEL % 1

		requireManaDes = self.getRequireManaDes( skill )
		if hasattr( skill , "getRequire" ):
			requireVitality = skill.getRequire().getRequireVitality( skill )
			if requireVitality:
				requireVitalityDes = lbs_ItemsFactory.VITALITYDES + PL_Font.getSource( str( requireVitality ), fc = "c6" )
			requireHP = skill.getRequire().getRequireHP( skill )
			if requireHP:
				requireHPDes = lbs_ItemsFactory.HPDES + PL_Font.getSource( str( requireHP ), fc = "c6" )

		maxCDTime = 0
		if hasattr( skill, "getLimitCooldown" ):
			for cd in skill.getLimitCooldown():
				for cdData in skill.getSpringOnUsedCD():
					if cdData["CDID"] == cd:
						if cdData["CDTime"] > maxCDTime:
							maxCDTime  = cdData["CDTime"]
				for cdData in skill.getSpringOnIntonateOverCD():
					if cdData["CDID"] == cd:
						if cdData["CDTime"] > maxCDTime:
								maxCDTime  = cdData["CDTime"]
		if maxCDTime > 0:
			maxCDTime = int( math.ceil( maxCDTime ) )
			cdTimeStr = PL_Font.getSource( str( maxCDTime ), fc = "c6" )
			cdTimeString = lbs_ItemsFactory.COOLDOWNTIME % cdTimeStr

		rangeMax = 0
		if hasattr( skill, "getRangeMax" ):
			rangeMax = skill.getRangeMax( BigWorld.player() )
			rangeMax = int( math.ceil( rangeMax ) )
		if rangeMax >= 1:
			distStr = PL_Font.getSource( str( rangeMax ), fc = "c6" )
			distString = lbs_ItemsFactory.ATTACKRANGE % distStr

		if hasattr( skill, "getLimitCooldown" ):
			intonateTime = skill.getIntonateTime()
			if intonateTime > 0:
				intonateTime = int( math.ceil( intonateTime ) )
				intonateStr = PL_Font.getSource( str( intonateTime ), fc = "c6" )
				intonateString = lbs_ItemsFactory.INOTATETIME + intonateStr + lbs_ItemsFactory.TIMEUNIT_S
#			else:
#				intonateStr = PL_Font.getSource( lbs_ItemsFactory.INSTANTSKILL, fc = "c6" )
#				intonateString = lbs_ItemsFactory.INOTATETIME + intonateStr
		if lvcMgr._sDatas.has_key( self.id_ ):	 # 生活技能无吟唱时间显示
			if self.id_ in player.skillList_:
				intonateString = ""
		if self.id_ in csconst.SKILL_ID_ACTIONS: # 行为技能无吟唱时间显示
			intonateString = ""

		needPosture = skill.getPosture()
		postureStr = lbs_ItemsFactory.POSTURE_STR.get( needPosture, "" )
		if postureStr:
			postureString = lbs_ItemsFactory.POSTURE + PL_Font.getSource( postureStr, fc = "c6" )

		LeftLine  = [skillName, sleightString, requireManaDes, requireVitalityDes, requireHPDes, cdTimeString, distString, intonateString, postureString]
		RightLine = [levelString]

		while LeftLine.count( "" ):
			LeftLine.pop( LeftLine.index( "" ) )

		while RightLine.count( "" ):
			RightLine.pop( RightLine.index( "" ) )

		maxLine = 0
		Llen = len( LeftLine )
		Rlen = len( RightLine )
		if Llen < Rlen:
			maxLine = Rlen
		else:
			maxLine = Llen
		for i in xrange( maxLine ):
			if i > Llen - 1:
				l = " "
			else:
				l = LeftLine[i]
			if i > Rlen - 1:
				r = " "
			else:
				r = RightLine[i]
			desList.append([l,r])

		des = skill.getDescription()	# 技能描述，默认为白色
		if des:
			skilldes = skill.getDescription()
			desList.append( [skilldes] )

		reqPresks = ""
		if nextSkID and teachSkill:
			reqPresks = self.getReqSkills( teachSkill )
		if reqPresks != "":
			rePreSkStr = labelGather.getText( "SkillList:main", "reqSkills" ) % reqPresks

		reqPotent = self.getReqPotential( skill, learned )
		if reqPotent > 0:
			strColor = colorFunc( self.checkPotential( skill, learned ) )
			reqPotentialStr = labelGather.getText( "SkillList:main", "reqPotent" ) % PL_Font.getSource( " %d" % reqPotent, fc = strColor )

		needPlayerLevel = self.getReqPlayerLevel( skill, learned )
		if needPlayerLevel > 0:
			strColor = colorFunc( self.checkPlayerLevel( skill, learned ) )
			reqRoleLevelStr = labelGather.getText( "SkillList:main", "reqRoleLevel" ) % PL_Font.getSource( " %d" % needPlayerLevel, fc = strColor )
		
		if self.checkIsTongSkill( skill ):
			needTongLevel = self.getReqTongLevel( skill.getID() )
			if needTongLevel != 0:
				reqTongLevelStr = labelGather.getText( "SkillList:main", "reqTongLevel" ) % PL_Font.getSource( " %d" % needTongLevel, fc = strColor )
			learnList = [ reqTongLevelStr, reqPotentialStr, rePreSkStr]
		else:
			learnList = [ reqRoleLevelStr, reqPotentialStr, rePreSkStr]

		while learnList.count( "" ):
			learnList.pop( learnList.index( "" ) )

		if len( learnList ) and learnUpReqs:
			learnUpReqs = PL_Font.getSource( learnUpReqs, fc = 'c46' )
			desList.append( [learnUpReqs] )
			for m in learnList:
				desList.append( [m] )

		return desList

	def getRequireManaDes( self, skill ):
		"""
		单独提出获取角色法力消耗的接口是因为目前子类(宠物技能)与之不同，只单独提出一部分，而没有提出所有可能不同的描述的原因
		是各个部分的描述放置的位置不同，所以如果以后有可能再次提出含有争议额部分描述，需要单独提出接口
		"""
		requireManaDes = ""
		requireManaList = []
		if hasattr( skill , "getRequire" ):
			manaSkill = skill
			requireManaList = manaSkill.getRequire().getRequireManaList(  BigWorld.player(), manaSkill )		# 技能消耗的法力描述
		for requireMana in requireManaList:
			des = requireMana[0]
			number = re.findall( r"\d+", des )#这里取任意 1-N 个连续的数字存到 number 中,如 消耗法力:120 那么结果是 ['120']
			desNumber = ""
			if number:
				desNumber = PL_Font.getSource( number[0] , fc = "c6" )
			des = des.replace( number[0] ,desNumber )		#数字替换成有颜色的
			if requireManaDes == "" :
				requireManaDes += des
			else:
				requireManaDes = requireManaDes + PL_NewLine.getSource() + des

		return requireManaDes
	
	def checkIsTongSkill( self, skill ):
		"""
		是否为帮会技能
		"""
		skillID = skill.getID()
		skIDType = tongSkillDatas.getDatas().keys()
		return ( skillID/1000 ) * 1000 in skIDType
		

	def getReqPotential( self, skill, learned = True ):
		"""
		需要潜能
		"""
		skillID = skill.getID()
		skillData = skTeachDatas.get( skillID, None )
		if skillData is None: return 0
		if not learned:
			return skillData["ReqPotential"]
		nextSkID = skillData["nextLevelID"]
		if nextSkID > 0:
			nextSkData = skTeachDatas.get( nextSkID, None )
			if nextSkData is None: return 0
			return nextSkData["ReqPotential"]
		else:
			return 0

	def checkPotential( self, skill, learned = True ):
		"""
		潜能检测
		"""
		reqPotential = self.getReqPotential( skill, learned )
		return BigWorld.player().potential >= reqPotential

	def getReqPlayerLevel( self, skill, learned = True ):
		"""
		需要玩家等级
		"""
		skillID = skill.getID()
		skillData = skTeachDatas.get( skillID, None )
		if skillData is None: return 0
		if not learned: #未学习
			return skillData["ReqLevel"]
		nextSkID = skillData["nextLevelID"]
		if nextSkID > 0:
			nextSkData = skTeachDatas.get( nextSkID, None )
			if nextSkData is None: return 0
			return nextSkData["ReqLevel"]
		else:
			return 0
			
	def getReqTongLevel( self, skID ):
		"""
		需要玩家帮会等级
		"""
		reqTongLevel = 0
		isLearned = skID in BigWorld.player().skillList_
		skillType = ( skID / 1000 ) * 1000
		skillData = tongSkillDatas.getDatasByType( skillType )
		for index, skillInfo in skillData.iteritems():
			if skillInfo["id"] == skID:
				if not isLearned:
					reqTongLevel = skillInfo["repBuildingLevel"]	#研究院的等级直接就是帮会的等级
				else:
					skillMaxLevel = skillType + skillInfo["skillMaxLevel"]
					if skID < skillMaxLevel:
						nextSkillInfo = skillData.get( index + 1)
						if nextSkillInfo is not None:
							reqTongLevel = nextSkillInfo["repBuildingLevel"]
						
		return reqTongLevel																

	def checkPlayerLevel( self, skill, learned = True ):
		"""
		等级检测
		"""
		reqPlayerLevel = self.getReqPlayerLevel( skill, learned )
		return BigWorld.player().getLevel() >= reqPlayerLevel

	def getReqSkills( self, skill ):
		"""
		获取前置技能
		"""
		dsp = ""
		colorFunc = lambda v : v and "c6" or "c3"
		if hasattr( skill, "getReqSkills" ):
			player = BigWorld.player()
			reqSkills = skill.getReqSkills()
			for skilID in reqSkills:
				strColor = colorFunc( player.hasSkill( skilID ) )
				skill = skills.getSkill( skilID )
				skill_level = skill.getLevel()
				skill_name = skill.getName()
				dsp += PL_Font.getSource( " %s"%skill_name+ str( skill_level ) + lbDatas.LEVEL, fc = strColor )
		return dsp

	@property
	def countable( self ) :
		return False

	# ---------------------------------------
	@property
	def itype( self ) :
		return self.baseItem.getType()

	@property
	def level( self ) :
		return self.baseItem.getLevel()

	@property
	def isPassive( self ) :
		return self.baseItem.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE

	# ---------------------------------------
	@property
	def isNormalSkill( self ) :
		stype = self.baseItem.getType()
		return stype == csdefine.BASE_SKILL_TYPE_ACTION or stype == csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL


# --------------------------------------------------------------------
# 骑宠技能
# --------------------------------------------------------------------
class VehicleSkillItem( SkillItem ) :
	def __init__( self, baseItem ) :
		SkillItem.__init__( self, baseItem )

	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def spell( self ) :
		if self.baseItem.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE : return
		DEBUG_MSG( "skill %d has been used." %  self.id )

	def spellToSelf( self ) :
		"""
		spell item to self
		"""
		pass


# --------------------------------------------------------------------------------
class PetSkillItem( SkillItem ) :
	def __init__( self, baseItem ) :
		SkillItem.__init__( self, baseItem )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, baseItem ) :
		ItemInfo.update( self, baseItem )
		self.id_ = baseItem.getID()
		self.name_ = baseItem.getName()

	# -------------------------------------------------
	def isCooldownType( self, cooldownType ) :
		skill = self.baseItem
		if skill is None : return False
		if skill.getType() not in csconst.BASE_SKILL_TYPE_SPELL_LIST : return False
		return skill.isCooldownType( cooldownType )

	def getPetTarget( self ):
		player = BigWorld.player()
		pet = player.pcg_getActPet()
		if pet is None:return None
		target = player.targetEntity
		if target is None:
			target1 = BigWorld.entities.get( pet.targetID, None )
			if target1 is None:
				return None
			else:
				target = target1
		return target

	def validTarget( self ):
		"""
		判断该Item是否能够对宠物target起作用
		"""
		player = BigWorld.player()
		pet = player.pcg_getActPet()
		target = self.getPetTarget()

		skill = skills.getSkill( self.id )
		if skill.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE or not pet:
			return csstatus.SKILL_GO_ON

		skillCastObjCondition = skill.getCastObject()
		target = SkillTargetObjImpl.createTargetObjEntity( skillCastObjCondition.convertCastObject( pet, target ) )
		state = skills.getSkill( self.id ).useableCheck( pet, target )
		if state in SKILL_STATE_LIST:
			return state
		return csstatus.SKILL_GO_ON

	def getCooldownInfo( self ) :
		player = BigWorld.player()
		if not player.isPlayer() : return 0, 0

		totalTime = 0
		endTime = 0
		if self.getSpell().getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:
			return 0, 0
		for cd in self.baseItem.getLimitCooldown():
			cdData = player.pcg_getPetCooldown( cd )
			t = cdData[1]
			e = cdData[3]
			if e > Time.time() and e > endTime :
				totalTime, endTime = t, e

		leaveTime = endTime - Time.time()
		if leaveTime <= 0 or totalTime <= 0 : return 0, 0
		leaveRate = leaveTime * 1.0 / totalTime
		return leaveTime, leaveRate

	def getSpell( self ) :
		return self.baseItem

	def spell( self ) :
		player = BigWorld.player()
		pet = player.pcg_getActPet()
		spellCastObj = self.getSpell().getCastObject()
		target = spellCastObj.convertCastObject( player.pcg_getActPet(), self.getPetTarget() )
		if target:
			state = self.validTarget()
			if state not in [ csstatus.SKILL_GO_ON ] :
				player.showPetInvalidItemCover( self.id )
			pet.attackTarget( target, self.id )
			DEBUG_MSG( "skill %d has been used." %  self.id )

	def spellToSelf( self ) :
		"""
		spell item to self
		"""
		pass

	def getRequireManaDes( self, skill ):
		"""
		单独提出获取角色法力消耗的接口是因为目前子类(宠物技能)与之不同，只单独提出一部分，而没有提出所有可能不同的描述的原因
		是各个部分的描述放置的位置不同，所以如果以后有可能再次提出含有争议额部分描述，需要单独提出接口
		"""
		requireManaDes = ""
		requireManaList = []
		skill = self.baseItem
		castEntity = None
		try:
			castEntity = BigWorld.player().pcg_getActPet()
		except:
			ERROR_MSG( "has no act pet!")
			return ""
		if not castEntity:
			return ""
		if hasattr( skill , "getRequire" ):
			requireManaList = skill.getRequire().getRequireManaList( castEntity, skill )		# 技能消耗的法力描述
		for requireMana in requireManaList:
			des = requireMana[0]
			number = re.findall( r"\d+", des )#这里取任意 1-N 个连续的数字存到 number 中,如 消耗法力:120 那么结果是 ['120']
			desNumber = ""
			if number:
				if requireMana[1]:
					desNumber = PL_Font.getSource( number[0] , fc = "c6" )
			des = des.replace( number[0] ,desNumber )		#数字替换成有颜色的
			if requireManaDes == "" :
				requireManaDes += des
			else:
				requireManaDes = requireManaDes + PL_NewLine.getSource() + des

		return requireManaDes

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def icon( self ) :
		global _icon_mapping_36
		icon = self.baseItem.getIcon()
		return ( getValidIcon( icon ), _icon_mapping_36 )

#	@property
#	def description( self ) :
#		skill = self.baseItem
#		if self.level > 0 :
#			return [self.name, str( self.level ) + "级", skill.getDescription()]
#		return [self.name, skill.getDescription()]

	@property
	def countable( self ) :
		return False

	# ---------------------------------------
	@property
	def itype( self ) :
		return self.baseItem.getType()

	@property
	def level( self ) :
		return self.baseItem.getLevel()

	@property
	def isPassive( self ) :
		return self.baseItem.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE

	# ---------------------------------------
	@property
	def isNormalSkill( self ) :
		return self.baseItem.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL

# --------------------------------------------------------------------
# implement quickbar item class
# --------------------------------------------------------------------
class QuickBarItem( ItemInfo ) :
	def __init__( self, baseItem ) :
		ItemInfo.__init__( self, baseItem )

		self.__isInCooldown = False
		self.__cooldownStartTime = Time.time()
		self.__cooldownLastTime = 0

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isCooldownType( self, cooldownType ) :
		return False

	# -------------------------------------------------
	def unlock( self ) :
		self.__isInCooldown = False
		self.__cooldownLastTime = 0


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def qbType( self ) :
		return csdefine.QB_ITEM_NONE

# --------------------------------------------------------------------
# implement buffer item class
# --------------------------------------------------------------------
class BuffItem( ItemInfo ) :
	def __init__( self, buffInfo ) :
		buff = buffInfo["skill"]								# buff 对应的技能
		self.id_ = buff.getID()
		ItemInfo.__init__( self, buff )
		self.__persistent = math.ceil( buffInfo["persistent"] - Time.time() )
		self.__endTime = Time.time() + self.__persistent
		if self.__persistent <= 0:
			self.__endTime = 0									# 结束时间
		self.__buffIndex = buffInfo["index"]					# buff所对应的唯一索引(服务器上该buff也有相同的索引)
		self.__isNotIcon = buffInfo["isNotIcon"]				# 是否不显示buff图标

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def description( self ) :
		sDescription = []
		description = self.baseItem.getDescription()
		"""
		if self.baseItem.getLevel() > 0:		# 划要求buff弹出信息框内容不包括等级信息
			sDescription = [self.baseItem.getName(), str( self.baseItem.getLevel() ) + "级", description]
		else:
		"""
		sDescription = [self.baseItem.getName(), description]
		if self.endTime > 0 :
			residuaryTime = self.leaveTime
			if residuaryTime >= 31 :
				min = residuaryTime/60.0
				timeStr = lbs_ItemsFactory.REMAIN % int( math.ceil( min ) ) + ShareTexts.CHTIME_MINUTE
			else :
				sec = residuaryTime%60
				if sec < 1: sec = 1.0
				timeStr = lbs_ItemsFactory.REMAIN % sec + ShareTexts.CHTIME_SECOND
			timeStr = PL_Font.getSource( timeStr, fc = "c6" )
			sDescription.append( timeStr )
		return sDescription

	@property
	def icon( self ) :
		global _icon_mapping_36
		icon = self.baseItem.getIcon()
		return ( getValidIcon( icon ), _icon_mapping_36 )

	@property
	def startTime( self ) :
		"""
		buff 开始时间
		"""
		return self.__endTime - self.__persistent

	@property
	def endTime( self ) :
		"""
		buff 结束时间
		"""
		return self.__endTime

	@property
	def leaveTime( self ) :
		"""
		buff 的剩余时间
		"""
		return self.__endTime - Time.time()

	@property
	def buffIndex( self ) :
		"""
		buff 索引
		"""
		return self.__buffIndex

	@property
	def isNotIcon( self ) :
		"""
		是否不显示buff图标
		"""
		return self.__isNotIcon

	def _getPersistent( self ) :
		return self.__persistent

	def _setPersistent( self, persistent ) :
		self.__persistent = max( persistent - Time.time(), 0 )
		self.__endTime = persistent

	persistent = property( _getPersistent, _setPersistent )

# ---------------------------------------------------------------
# implement vehicle item class
# ---------------------------------------------------------------
class VehicleItem( ItemInfo ):

	def __init__( self, vechicleData ):
		ItemInfo.__init__( self, vechicleData )
		self.id_ = vechicleData["srcItemID"]
		self.dbid = vechicleData["id"]
		self.srcItem = BigWorld.player().createDynamicItem( self.id_ )

	def spell( self ):
		player = BigWorld.player()
		if player.vehicleDBID == self.dbid:
			player.cell.retractVehicle()
		else:
			player.conjureVehicle( self.dbid )

	def update( self, baseItem ) :
		self.id_ = baseItem["srcItemID"]
		self.dbid = baseItem["id"]
		self.srcItem = BigWorld.player().createDynamicItem( self.id_ )
		ItemInfo.update( self, self.srcItem )

	@property
	def icon( self ) :
		global _icon_mapping_36
		icon = self.srcItem.icon()
		return ( getValidIcon( icon ), _icon_mapping_36 )

	@property
	def description( self ) :
		dsp = self.srcItem.description( BigWorld.player() )
		"""
		name = dsp[0][0]
		name = name.split("}")
		name = name[0] + "}" + name[-1].split("(")[-1].split(")")[0]	# 去掉“骑宠蛋”几个字
		dsp[0][0] = name
		"""
		return dsp

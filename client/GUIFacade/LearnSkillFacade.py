# -*- coding: gb18030 -*-
#
# $Id: LearnSkillFacade.py,v 1.23 2008-04-18 08:33:55 fangpengjun Exp $

"""
implement skill learning facade

Dec 6th, 2006 : modified by huangyongwei
"""

from bwdebug import *
import BigWorld
from event.EventCenter import *
import csconst
import csstatus
import csdefine
import skills as Skill
import config.client.labels.GUIFacade as lbDatas

class LearningSkill :
	def __init__( self, id ) :
		self.__id = id
		self.__skill = Skill.getSkill( id )
		self.__unlearnableMsg = ""

	# -------------------------------------------------
	def getID( self ) :
		return self.__id

	def getSkill( self ):
		return self.__skill

	def getName( self ) :
		return self.__skill.getName()

	def getIcon( self ) :
		return self.__skill.getIcon()

	def getLevel( self ) :
		return self.__skill.getTeachNextLevel( BigWorld.player() )

	def getCost( self ):
		return self.__skill.getCost()

	def getLearnLevel( self ) :
		return self.__skill.getReqLevel()

	def getReqMetier( self ):
		return csconst.g_chs_class[csconst.g_map_class[self.__skill.getReqMetier()]]

	def getNeedPlayerLevel( self ):
		return self.__skill.getNeedPlayerLevel()

	def getNeedVehicleLevel( self ) :
		return self.__skill.getNeedVehicleLevel()

	def getRepSkill( self ):
		"""
		获取学习当前技能需要的前置技能是什么
		return str
		"""
		skills = self.__skill.getReqSkills()
		dsp = ""
		for skilID in skills:
			skill = Skill.getSkill( skilID )
			skill_level = skill.getLevel()
			skill_name = skill.getName()
			dsp += " %s"%str( skill_level ) + lbDatas.LEVEL + skill_name
		return dsp

	def getDescription( self ) :
		dsp = self.__skill.getSkillDsp()				#被教授的技能描述
		return dsp

	def getPotential( self ):
		player = BigWorld.player()
		return self.__skill.getPotential( player )

	def getType( self ):
		return self.__skill.getType()

	def learnable( self ) :
		self.__unlearnableMsg = self.__skill.learnable()
		if self.__unlearnableMsg is None :
			return True
		return False

	def getIntonateTime( self ):
		learnSkill = self.getLearnSkill()
		if learnSkill.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:
			return 0
		return learnSkill.getIntonateTime()

	def getMaxCDTime( self ):
		maxCDTime = 0
		skill = self.getLearnSkill()
		if skill.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:
			return 0
		for cd in skill.getLimitCooldown():
			for cdData in skill.getSpringOnUsedCD():
				if cdData["CDID"] == cd:
					if cdData["CDTime"] > maxCDTime:
						maxCDTime  = cdData["CDTime"]
			for cdData in skill.getSpringOnIntonateOverCD():
				if cdData["CDID"] == cd:
					if cdData["CDTime"] > maxCDTime:
						maxCDTime  = cdData["CDTime"]
		return maxCDTime

	def getLimitCooldown( self ):
		skill = self.getLearnSkill()
		if skill.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:
			return 0
		limitCDs = skill.getLimitCooldown()
		return limitCDs

	def getRequire( self ):
		skill = self.getLearnSkill()
		if skill.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:
			return None
		return skill.getRequire()

	def getLearnError( self ) :
		return self.__unlearnableMsg

	def getLearnID( self ):
		return self.__skill.getTeach() + self.getLevel() - Skill.getSkill( self.__skill.getTeach() ).getLevel()

	def getLearnSkill( self ):
		return Skill.getSkill( self.getLearnID() )

	def checkMetier( self ):
		"""
		检查职业
		@return BOOL
		"""
		return  self.__skill.checkMetier()

	def checkLevel( self ):
		"""
		检查等级
		@return BOOL
		"""
		return self.__skill.checkLevel()

	def checkMoney( self ):
		"""
		检查金钱
		@return BOOL
		"""
		return self.__skill.checkMoney()

	def checkPotential( self ):
		"""
		检查潜能点
		@return BOOL
		"""
		return self.__skill.checkPotential()

	def checkPremissSkill( self ):
		"""
		检查前置技能
		@return BOOL
		"""
		return self.__skill.checkPremissSkill()

	def isTongSkill( self ):
		"""
		是否为帮会技能
		@return BOOL
		"""
		return hasattr( self.__skill, "getReqTongContribute" )

	def reqTongContribute( self ):
		"""
		帮会技能需要帮会贡献度
		"""
		if self.isTongSkill():
			tongContribute = self.__skill.getReqTongContribute()
			contribute = int( tongContribute )
			return contribute

	def checkTongContribute( self ):
		"""
		检查帮会建筑度
		"""
		player = BigWorld.player()
		tongMembers = player.tong_memberInfos
		playerMember = tongMembers.get( player.databaseID, None )
		if playerMember is None:return
		return self.reqTongContribute() <= playerMember.getContribute()
	
	def checkHasLearnt( self, trainer ):
		"""
		检测是否在NPC学过该技能
		"""
		return self.__skill.checkHasLearnt( trainer )
	
	
	def getSpellTeachID( self ):
		"""
		获取第1级技能id
		"""
		return self.__skill._spellTeach
# --------------------------------------------------------------------
# LearnSkillFacade
# --------------------------------------------------------------------
class LearnSkillFacade :
	@staticmethod
	def reset() :
		LearnSkillFacade.trainer = None			# entity of trainer

	@staticmethod
	def getTrainer() :
		return LearnSkillFacade.trainer


# --------------------------------------------------------------------
# called by client base
# --------------------------------------------------------------------
def showLearnSkillWindow( trainer ) :
	"""
	show learn skill window
	@type			trainer : Bigworld.Entity
	@param			trainer : entity of trainer
	@return				: None
	"""
	LearnSkillFacade.trainer = trainer
	fireEvent( "EVT_ON_SHOW_LEARN_SKILL_WINDOW", trainer )

def onSkillLearnt( skillID ) :
	"""
	when a skill has been learnt, it will be called
	@type			skillID : INT32
	@param			skillID : the id of the learnt skill
	@return					: None
	"""
	fireEvent( "EVT_ON_SKILL_LEARNT", skillID )


# --------------------------------------------------------------------
# called by ui
# --------------------------------------------------------------------
def getLearnSkills() :
	"""
	get all skills
	@rtype						   : list
	@return						   : a list of skill id like as [skillID1, skillID2, ... ]
	"""
	trainer = LearnSkillFacade.getTrainer()
	if trainer is None : return []
	skills = []
	for skillID in trainer.getLearnSkillIDs() :
		sk = LearningSkill( skillID )
		if sk.checkHasLearnt( trainer ):		#已在npc学习该技能
			continue
		skills.append( sk )
	return skills

# -----------------------------------------------------
def learnSkill( skill ):
	"""
	require learning a skill
	@rtype				skill : LearningSkill
	@param				skill : instance of LearningSkill
	@return					  : None
	"""
	if skill.learnable() :
		trainer = LearnSkillFacade.getTrainer()
		trainer.train( BigWorld.player(), skill.getID() )
	else :
		BigWorld.player().statusMessage( csstatus.ACCOUNT_STATE_FAILED_MSG, skill.getLearnError() )

# --------------------------------------------------------------------
# called by ui livingSkillTrainer by 姜毅
# --------------------------------------------------------------------

def getLearnLivingSkill():
	"""
	获得已经学习的生活技能
	"""
	trainer = LearnSkillFacade.getTrainer()

def learnLivingSkill( skillID ):
	"""
	学习一个生活技能
	"""
	trainer = LearnSkillFacade.getTrainer()
	trainer.train( BigWorld.player(), skillID )

def obliveSkill( skillID ):
	"""
	遗忘一个生活技能
	"""
	trainer = LearnSkillFacade.getTrainer()
	trainer.oblive( BigWorld.player(), skillID )

def levelUpSkill( skillID ):
	"""
	升级一个生活技能
	"""
	trainer = LearnSkillFacade.getTrainer()
	trainer.skillLevelUp( BigWorld.player(), skillID )
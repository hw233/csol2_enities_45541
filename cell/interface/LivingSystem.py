# -*- coding: gb18030 -*-
#

"""
生活系统模块
"""
import time
from bwdebug import *
import csdefine
import csstatus
from MsgLogger import MsgLogger
import Const
from LivingConfigMgr import LivingConfigMgr
from Love3 import g_skills
from MsgLogger import g_logger

lcm = LivingConfigMgr.instance()

SKILLID_NAME = {
				790001001:"",
				790002001:"",
				790003001:"",
				790004001:"",
				790005001:"",
			}
			
class LivingSystem:
	"""
	"""
	def __init__( self ):
		"""
		初始化状态。要在Fight初始化之前
		"""
		for skillID in SKILLID_NAME:
			skillInstance = g_skills[skillID]
			if skillInstance is None:
				ERROR_MSG( "Living skill %s is None."%(skillID) )
				return
			SKILLID_NAME[skillID] = skillInstance.getName()
	
	def chargeVim( self ):
		"""
		Define method
		每天补充活力值
		"""
		maxVim = lcm.getMaxVimByLevel( self.level )
		self.vim = maxVim
		INFO_MSG( "chargeVim role %s(%s) DBID %s, level %i, max vim %i ."%( self.getName(), self.id, self.databaseID, self.level, maxVim ) )
		
	def consumeVim( self, value ):
		"""
		消耗活力值
		"""
		INFO_MSG( "consumeVim role %s(%s) DBID %s consumeValue %s nowVimValue %s"%( self.getName(), self.id, self.databaseID, value, self.vim ) )
		if self.vim == 0 or self.vim - value < 0: return False
		self.vim -= value
		return True
		
	def liv_onLevelUp( self, deltaLevel ):
		"""
		角色升级时对生活系统的影响
		
		@param deltaLevel : 升级后和升级前的级别差
		@type deltaLevel : UINT16
		"""
		self.vim += deltaLevel * 5	# 9:58 2011-5-20，大少要求：角色每升一级获得5点活力值。
		
	def liv_isSkillEmpty( self ):
		"""
		是否有生活技能
		"""
		return len( self.livingskill ) <= 0
		
	def getReqLevelUpMoney( self, skillID ):
		"""
		获取升级所需金钱
		"""
		nextLevelInfo = lcm.getLivingLevelInfo( skillID, self.getSkillLevel( skillID ) )
		return lcm.getReqMoneyByLevel( skillID, nextLevelInfo[1] )
		
	def liv_learnSkill( self, skillID ):
		"""
		新技能学习
		"""
		levelInfo = lcm.getLivingLevelInfo( skillID, 0 )
		self.livingskill[skillID] = levelInfo
		INFO_MSG( "living skill LearnSkill role %s(%s) DBID %s skillID %s sleight %s level %s"%( self.getName(), self.id, self.databaseID, skillID, levelInfo[0], levelInfo[1] ) )
		try:
			g_logger.skillLearnLog( self.databaseID, self.getName(), skillID, 0, 0 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
			
		self.client.onClientGetLivingSkill( skillID, levelInfo[0], levelInfo[1] )
		self.questLivingSkillLearned(skillID)	#更新任务task
		return True
		
	def liv_hasLearnSkill( self, skillID ):
		"""
		是否已学习某技能
		"""
		return skillID in self.livingskill
		
	def livingskillLearnMax( self ):
		"""
		生活技能学习是否达到上限数量
		"""
		return len( self.livingskill ) >= Const.LIVING_SKILL_NUM_MAX
		
	def liv_skillLevelUp( self, skillID ):
		"""
		技能升级
		"""
		sleight, level = lcm.getLivingLevelInfo( skillID, self.getSkillLevel( skillID ) )
		if skillID in self.livingskill:
			oldInfo = self.livingskill[skillID]
			if sleight < oldInfo[0]:
				sleight = oldInfo[0]
		self.livingskill[skillID] = ( sleight, level )
		INFO_MSG( "living skill LevelUp role %s(%s) DBID %s skillID %s sleight %s level %s"%( self.getName(), self.id, self.databaseID, skillID, sleight, level ) )
		# 写日志
		try:
			g_logger.skillUpgradeLog( self.databaseID, self.getName(), self.getLevel(), skillID, 0, 0 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		
		self.client.onClientGetLivingSkill( skillID, sleight, level )
		self.questLivingSkillLearned(skillID)	#更新任务task
		return True
		
	def liv_isMaxLevel( self, skillID ):
		"""
		某技能是否已经到顶级
		"""
		return lcm.isMaxLevel( skillID, self.getSkillLevel( skillID ) )
		
	def liv_allSkillMaxLevel( self ):
		"""
		是否所有技能已经到顶级
		"""
		if self.liv_isSkillEmpty():
			return False
		for skillID in self.livingskill:
			if not self.liv_isMaxLevel( skillID ):
				return False
		return True
	
	def liv_obliveSkill( self, skillID ):
		"""
		遗忘一个已习得的生活技能
		"""
		if not self.livingskill.has_key( skillID ): return False
		self.livingskill.pop( skillID )
		INFO_MSG( "living skill Oblive role %s(%s) DBID %s skillID %s"%( self.getName(), self.id, self.databaseID, skillID ) )
		try:
			g_logger.skillRemoveLog( self.databaseID, self.getName(), skillID )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		self.client.onClientGetLivingSkill( skillID, 0, 0 )
		return True
		
	def setVim( self, newVimValue ):
		"""
		设置活力值
		"""
		self.vim = newVimValue
		
	def getVim( self ):
		"""
		获得活力值
		"""
		return self.vim
		
	def isSleightLevelMax( self, skillID ):
		"""
		同等级技能熟练度是否已满
		"""
		return self.getSleight(skillID) >= self.getSleightMax(skillID)
		
	def addSleight( self, skillID, addValue ):
		"""
		增加一个技能的熟练度
		"""
		if not self.livingskill.has_key( skillID ): return
		value = self.livingskill[skillID][0] + addValue
		lim = self.getSleightMax( skillID )
		if value > lim: value = lim
		self.setSleight( skillID, value )
		
	def setSleight( self, skillID, newSleightValue ):
		"""
		设置某个已习得的生活技能的熟练度
		"""
		if not self.livingskill.has_key( skillID ): return
		level = self.getSkillLevel( skillID )
		self.livingskill[skillID] = ( newSleightValue, level )
		INFO_MSG( "living skill setSleight role %s(%s) DBID %s skillID %s newValue %s level %s"%( self.getName(), self.id, self.databaseID, skillID, newSleightValue, level ) )
		self.client.onClientGetLivingSkill( skillID, newSleightValue, level )
		
	def setSkillLevel( self, skillID, newLevel ):
		"""
		设置某个已习得的生活技能的技能等级
		"""
		if not self.livingskill.has_key( skillID ): return
		sleight =  self.livingskill[skillID][0]
		self.livingskill[skillID] = ( sleight, newLevel )
		INFO_MSG( "living skill setSkillLevel role %s(%s) DBID %s skillID %s sleight %s newLevel %s"%( self.getName(), self.id, self.databaseID, skillID, sleight, newLevel ) )
		self.client.onClientGetLivingSkill( skillID, sleight, newLevel )
		
	def getSleight( self, skillID ):
		"""
		获得某个已习得的生活技能的熟练度
		"""
		if not self.livingskill.has_key( skillID ): return -1
		return self.livingskill[skillID][0]
		
	def getSleightMax( self, skillID ):
		"""
		获得某个已习得的生活技能的熟练度上限
		"""
		if not self.livingskill.has_key( skillID ): return -1
		return lcm.getMaxSleightByLevel( skillID, self.getSkillLevel( skillID ) )
		
	def getSkillLevel( self, skillID ):
		"""
		通过技能id获得已习得技能的等级
		"""
		if not self.livingskill.has_key( skillID ): return -1
		return self.livingskill[skillID][1]
		
	def getSleLastMax( self, skillID ):
		"""
		获得当前等级的采集技能的前一级上限
		"""
		if not self.livingskill.has_key( skillID ): return -1
		return lcm.getSleLastMax( skillID, self.getSkillLevel( skillID ) )
		
	def getSkillReqLevel( self, skillID ):
		"""
		获得技能所需等级
		"""
		if not self.livingskill.has_key( skillID ): return 0
		reqLevel = lcm.getReqLevelByLevel( skillID, self.getSkillLevel( skillID ) )
		return reqLevel
		
	def getSkillNextReqLevel( self, skillID ):
		"""
		获得升级所需下级技能
		"""
		if not self.livingskill.has_key( skillID ): return 0
		level = self.getSkillLevel( skillID ) + 1
		reqLevel = lcm.getReqLevelByLevel( skillID, level )
		return reqLevel
		
	def clientGetLivingSkill( self ):
		"""
		初始化式客户端获得全部生活技能
		"""
		role_skills = self.getSkills()
		# 对于没有存入数据库但已习得的技能，先清除之
		for skillID in SKILLID_NAME:
			if skillID in role_skills and skillID not in self.livingskill:
				self.removeSkill( skillID )
		# 向客户端发送数据
		for skillID in self.livingskill:
			skillInfo = self.livingskill[skillID]
			self.client.onClientGetLivingSkill( skillID, skillInfo[0], skillInfo[1] )
		
	# -------------------------npc learn Result-----------------------------------------
	def onTeachTalkLVUPSkill( self, srcEntityID, skillID, money ):
		"""
		Exposed
		NPC对话升级技能结果
		"""
		reqLevel = self.getSkillNextReqLevel( skillID )
		if self.level < reqLevel:
			self.statusMessage( csstatus.LIVING_SKILL_NEED_LV, reqLevel )
			return
		if self.money >= money and self.payMoney( money, csdefine.CHANGE_MONEY_LIVING_LEVEL_UP_SKILL ):
			if self.liv_skillLevelUp( skillID ):
				level = self.getSkillLevel( skillID )
				levelString = lcm.getDesByLevel( skillID, level ).split( "|" )[-1]
				self.statusMessage( csstatus.LIVING_LEVEL_UP_SKILL_SUCCESS, SKILLID_NAME[skillID], levelString )
		else:
			self.statusMessage( csstatus.LIVING_LEARN_NOT_ENOUGHT_MONEY )
		
	def onTeachTalkObliveSkill( self, srcEntityID, skillID ):
		"""
		Exposed
		NPC对话遗忘技能结果
		"""
		if self.liv_obliveSkill( skillID ):
			self.removeSkill( skillID )
			self.statusMessage( csstatus.LIVING_OBLIVE_SKILL_SUCCESS )
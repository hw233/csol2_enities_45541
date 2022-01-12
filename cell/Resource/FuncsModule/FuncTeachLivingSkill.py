# -*- coding: gb18030 -*-
"""
学习生活技能对话 2009-11-27 by 姜毅
"""

from Function import Function
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
import csstatus
import BigWorld
import sys
from Resource.SkillLoader import g_skills

class FuncTeachLivingSkill( Function ):
	"""
	学习生活技能
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._talkType = int( section.readString( "param1" ) )	# 需要学习(1)还是遗忘(2)还是升级(3)技能
		self._learnSkillID = int( section.readString( "param2" ) )		# 需要学习/遗忘的技能ID


	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		reqLevel = player.getSkillReqLevel( self._learnSkillID )
		level = player.getSkillLevel( self._learnSkillID )
		try:
			skillInstance = g_skills[self._learnSkillID]
			if skillInstance is None:
				ERROR_MSG( "Living skill %s is None."%(self._learnSkillID) )
				return
			skillName = skillInstance.getName()
		except:
			skillName = ""
		if self._talkType == 1:	# 学习
			if player.liv_hasLearnSkill( self._learnSkillID ):
				player.statusMessage( csstatus.LIVING_SKILL_HAS_LEARN )
			elif player.livingskillLearnMax():
				player.statusMessage( csstatus.LIVING_CANT_LEARN_MORE_SKILL )
			elif player.level < 15:
				player.statusMessage( csstatus.LIVING_SKILL_LEARN_LV, 15 )
			else:
				if player.liv_learnSkill( self._learnSkillID ):
					skills = player.getSkills()
					if not self._learnSkillID in skills:
						player.addSkill( self._learnSkillID )
					player.statusMessage( csstatus.LIVING_LEARN_NEW_SKILL_SUCESS, skillName )
		elif self._talkType == 2:	# 遗忘
			nowLevel = player.getSkillLevel( self._learnSkillID )
			player.client.livingTeacherTalkResult( self._talkType, self._learnSkillID, nowLevel, 0 )
		elif self._talkType == 3:	# 升级
			if not player.isSleightLevelMax( self._learnSkillID ):
				player.statusMessage( csstatus.LIVING_SKILL_SLEIGHT_NOT_ENOUTH )
			elif player.iskitbagsLocked():	# 背包上锁，by姜毅
				player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			else:
				money = player.getReqLevelUpMoney( self._learnSkillID )
				player.client.livingTeacherTalkResult( self._talkType, self._learnSkillID, level, money )
		else:
			ERROR_MSG( "living teacher not has that talk: %i"%(self._talkType)  )
		player.sendGossipComplete( talkEntity.id )
		Function.do( self, player, talkEntity )
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		if self._talkType == 1:	# 学习
			if len(player.livingskill) < 2:
				return True
			else:
				player.statusMessage( csstatus.LEARN_LIVING_SKILL_NUMBER_LIMIT) 
				return False
		elif self._talkType == 2:	# 遗忘
			if player.liv_hasLearnSkill( self._learnSkillID ):
				return True
			else:
				if player.liv_isSkillEmpty():
					player.sendGossipComplete( talkEntity.id )
					player.endGossip( talkEntity )
					player.setGossipText( cschannel_msgs.CAIJI_SKILL_VOICE_1 )
				return False
		elif self._talkType == 3:	# 升级
			if player.liv_isSkillEmpty():
				player.sendGossipComplete( talkEntity.id )
				player.endGossip( talkEntity )
				player.setGossipText( cschannel_msgs.CAIJI_SKILL_VOICE_1 )
				return False
			if player.liv_allSkillMaxLevel():
				player.sendGossipComplete( talkEntity.id )
				player.endGossip( talkEntity )
				player.setGossipText( cschannel_msgs.CAIJI_SKILL_VOICE_2 )
				return False
			if player.liv_hasLearnSkill( self._learnSkillID ) and not player.liv_isMaxLevel( self._learnSkillID ):
				return True
			else:
				return False
		return True
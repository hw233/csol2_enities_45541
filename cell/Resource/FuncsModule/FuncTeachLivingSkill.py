# -*- coding: gb18030 -*-
"""
ѧϰ����ܶԻ� 2009-11-27 by ����
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
	ѧϰ�����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._talkType = int( section.readString( "param1" ) )	# ��Ҫѧϰ(1)��������(2)��������(3)����
		self._learnSkillID = int( section.readString( "param2" ) )		# ��Ҫѧϰ/�����ļ���ID


	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
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
		if self._talkType == 1:	# ѧϰ
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
		elif self._talkType == 2:	# ����
			nowLevel = player.getSkillLevel( self._learnSkillID )
			player.client.livingTeacherTalkResult( self._talkType, self._learnSkillID, nowLevel, 0 )
		elif self._talkType == 3:	# ����
			if not player.isSleightLevelMax( self._learnSkillID ):
				player.statusMessage( csstatus.LIVING_SKILL_SLEIGHT_NOT_ENOUTH )
			elif player.iskitbagsLocked():	# ����������by����
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
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		if self._talkType == 1:	# ѧϰ
			if len(player.livingskill) < 2:
				return True
			else:
				player.statusMessage( csstatus.LEARN_LIVING_SKILL_NUMBER_LIMIT) 
				return False
		elif self._talkType == 2:	# ����
			if player.liv_hasLearnSkill( self._learnSkillID ):
				return True
			else:
				if player.liv_isSkillEmpty():
					player.sendGossipComplete( talkEntity.id )
					player.endGossip( talkEntity )
					player.setGossipText( cschannel_msgs.CAIJI_SKILL_VOICE_1 )
				return False
		elif self._talkType == 3:	# ����
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
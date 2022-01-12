# -*- coding: gb18030 -*-
#
# $Id: Trainer.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
Trainer基类
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
import GUIFacade
from Trainer import Trainer

class TongTrainer( Trainer ):
	"""
	帮会领地NPC基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Trainer.__init__( self )
		self.skillInfos = None
		self.skillType = csdefine.TONG_SKILL_ALL
		
	def onReceiveCanResearchSkills( self, buildingLevel, currentResearchSkill, skills ):
		"""
		define method.
		接收服务器发送过来的可学习技能列表
		@param buildingLevel: 研究院当前等级
		@param currentResearchVal: 当前研究度
		"""
		return
		GUIFacade.tong_showSkillResearchWindow( self, buildingLevel, currentResearchVal, currentResearchSkill, skills )

	def researchSkill( self, skillID ):
		"""
		像服务器请求研发该技能
		"""
		self.cell.researchSkill( skillID )

	def onChangeResearchSkill( self, currentResearchSkill ):
		"""
		define method.
		当前正在研发的技能改变了
		"""
		GUIFacade.tong_onChangeResearchSkill( currentResearchSkill )

	def receiveTrainTongSkillInfos( self, skillInfos, skillType ):
		"""
		define method.
		ARRAY <of> TONG_SKILL_RESEARCH_DATA </of>
		接收到服务器传来的可学习技能信息，  其中包括可学习的当前最大级别
		"""
		self.skillInfos = skillInfos
		self.skillType = skillType
		# 暂时这么调用，等界面支持后应该改变这里的做法
		skillList = BigWorld.player().skillList_
		canLearnSkills =[]
		for skillInfo in skillInfos:
			skillID = str( skillInfo["id"] )[1:-1]
			skillLevel = skillInfo["level"]
			if skillID in [str( skill )[:-1] for skill in skillList]: #已经学过该类技能
				curLevel = self.getCurLevel( skillID )
				if curLevel < skillLevel:
					canLearnSkills.append( skillInfo )
			else: #未学则直接加进去
				canLearnSkills.append( skillInfo )
		self.receiveTrainInfos( [ item["id"] for item in canLearnSkills ] )
	
	def getCurLevel( self, skillID ):
		skillList = BigWorld.player().skillList_
		for skill in skillList:
			if skillID == str( skill )[:-1]:
				return int( str( skill )[-1] )
		return -1

	def onShowTongSkillClearWindow( self, clearSkillIDs ):
		"""
		收到服务器传来的技能遗忘表
		"""
		GUIFacade.tong_onShowTongSkillClearWindow( clearSkillIDs )

# Trainer.py

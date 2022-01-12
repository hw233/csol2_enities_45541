# -*- coding: gb18030 -*-
#
# $Id: Trainer.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
Trainer����
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
import GUIFacade
from Trainer import Trainer

class TongTrainer( Trainer ):
	"""
	������NPC����
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		Trainer.__init__( self )
		self.skillInfos = None
		self.skillType = csdefine.TONG_SKILL_ALL
		
	def onReceiveCanResearchSkills( self, buildingLevel, currentResearchSkill, skills ):
		"""
		define method.
		���շ��������͹����Ŀ�ѧϰ�����б�
		@param buildingLevel: �о�Ժ��ǰ�ȼ�
		@param currentResearchVal: ��ǰ�о���
		"""
		return
		GUIFacade.tong_showSkillResearchWindow( self, buildingLevel, currentResearchVal, currentResearchSkill, skills )

	def researchSkill( self, skillID ):
		"""
		������������з��ü���
		"""
		self.cell.researchSkill( skillID )

	def onChangeResearchSkill( self, currentResearchSkill ):
		"""
		define method.
		��ǰ�����з��ļ��ܸı���
		"""
		GUIFacade.tong_onChangeResearchSkill( currentResearchSkill )

	def receiveTrainTongSkillInfos( self, skillInfos, skillType ):
		"""
		define method.
		ARRAY <of> TONG_SKILL_RESEARCH_DATA </of>
		���յ������������Ŀ�ѧϰ������Ϣ��  ���а�����ѧϰ�ĵ�ǰ��󼶱�
		"""
		self.skillInfos = skillInfos
		self.skillType = skillType
		# ��ʱ��ô���ã��Ƚ���֧�ֺ�Ӧ�øı����������
		skillList = BigWorld.player().skillList_
		canLearnSkills =[]
		for skillInfo in skillInfos:
			skillID = str( skillInfo["id"] )[1:-1]
			skillLevel = skillInfo["level"]
			if skillID in [str( skill )[:-1] for skill in skillList]: #�Ѿ�ѧ�����༼��
				curLevel = self.getCurLevel( skillID )
				if curLevel < skillLevel:
					canLearnSkills.append( skillInfo )
			else: #δѧ��ֱ�Ӽӽ�ȥ
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
		�յ������������ļ���������
		"""
		GUIFacade.tong_onShowTongSkillClearWindow( clearSkillIDs )

# Trainer.py

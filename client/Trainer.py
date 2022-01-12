# -*- coding: gb18030 -*-
# $Id: Trainer.py,v 1.21 2008-01-15 06:55:11 kebiao Exp $

import BigWorld
from bwdebug import *
import NPC
import csstatus
import GUIFacade
import skills
import copy

class Trainer( NPC.NPC ):
	"""
	训练师NPC
	"""

	def __init__( self ):
		NPC.NPC.__init__( self )
		#self.attrTrainIDs = set()		# hash set, save the skillID as int
		self.attrTrainInfo = {}			# key is skill id, value like as [name, type, level, cost]
		self.currLearning = set()		# 记录当前正在学习的skillID

	def receiveTrainInfos( self, skillIDs ):
		"""
		@param skillIDs: array of int64
		"""
		#self.attrTrainIDs = set( skillIDs )
		if len(self.attrTrainInfo) != 0:  #判断技能有没有加载过
			self.attrTrainInfo = {}
			self.getSkillAndShowWindow(skillIDs)
		else:
			self.attrTrainInfo = {}
			self.loadSkillAndShowWindow(skillIDs)

	def getSkillAndShowWindow(self, skillIDs):
		for id  in skillIDs:
			spell = skills.getSkill( id )
			name = spell.getName()
			type = 0	# 暂时全为0
			level = spell.getReqLevel()
			cost = spell.getCost()
			self.attrTrainInfo[id] = [name, type, level, cost]
			
		self.filterIdle()
		GUIFacade.showLearnSkillWindow( self )
	
	def loadSkillAndShowWindow(self, skillIDs):
		onceLoadNum = 10 			#一次性加载技能数
		callTimer = 0.2 			#再次执行时间

		def onSectionGetSkill():
			getIDs = []
			if len(skillIDs) > onceLoadNum:
				getIDs = skillIDs[0:onceLoadNum]
			else:
				getIDs = copy.copy( skillIDs )
			
			for id  in getIDs:
				skillIDs.pop(0)
				spell = skills.getSkill( id )
				name = spell.getName()
				type = 0	# 暂时全为0
				level = spell.getReqLevel()
				cost = spell.getCost()
				self.attrTrainInfo[id] = [name, type, level, cost]
			
			if len(skillIDs) > 0:
				BigWorld.callback( callTimer, onSectionGetSkill )
			else:
				self.filterIdle()
				GUIFacade.showLearnSkillWindow( self )
				
		onSectionGetSkill()
		
	def train( self, player, skillID ):
		"""
		@type skillID: INT16
		"""
		if skillID not in self.attrTrainInfo:
			#ERROR_MSG( "%i not exist." % skillID )
			player.statusMessage( csstatus.SKILL_NOT_HAVE, skillID )
			return
		self.currLearning.add( skillID )

		self.cell.trainPlayer( skillID )

	def spellInterrupted( self, skillID, reason ):
		"""
		Define method.
		法术中断

		@type reason: INT
		"""
		NPC.NPC.spellInterrupted( self, skillID, reason )
		if skillID in self.currLearning:
			self.currLearning.discard( skillID )

	def castSpell( self, skillID, targetObject ):
		"""
		Define method.
		正式施放法术——该起施法动作了

		@type skillID: INT
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		try:
			NPC.NPC.castSpell( self, skillID, targetObject )
		except Exception, err:
			ERROR_MSG( err )
		if skillID in self.currLearning:
			self.currLearning.discard( skillID )
			GUIFacade.onSkillLearnt( skillID )

	def filterIdle( self ):
		"""
		过滤没有用的 （满级或者其他）
		"""
		skillIDs = []
		for s in self.attrTrainInfo:
			if skills.getSkill( s ).islearnMax( self ):
				skillIDs.append( s )
		for s in skillIDs:
			self.attrTrainInfo.pop( s )

	def getLearnSkillIDs( self ) :
		"""
		获取所有学习技能
		"""
		self.filterIdle()
		skillIDs = self.attrTrainInfo.keys()
		count = len( skillIDs )
		for i in xrange( 1, count ):
			for ii in xrange( i ):
				iskill = skills.getSkill( skillIDs[i] )
				iiskill = skills.getSkill( skillIDs[ii] )
				if iskill.getFirstReqLevel() < iiskill.getFirstReqLevel():
					tmp = skillIDs[i]
					skillIDs[i] = skillIDs[ii]
					skillIDs[ii] = tmp
		return skillIDs

# -*- coding: gb18030 -*-

# this module implement the VehicleTrainer class
# written by gjx 2009-06-13
#
# 从Trainer再抽象出VehicleTrainer是有必要的，客户端需要
# 根据不同类型的训练师来进行相应的界面表现。

from Trainer import Trainer
import skills
import BigWorld
import GUIFacade

class VehicleTrainer( Trainer ) :

	def __init__( self ) :
		Trainer.__init__( self )

	def receiveTrainInfos( self, skillIDs ):
		"""
		@param skillIDs: array of int64
		"""
		#self.attrTrainIDs = set( skillIDs )
		self.attrTrainInfo = {}
		player = BigWorld.player()

		for id in skillIDs:
			spell = skills.getSkill( id )
			#if player.hasSkill( spell.getTeach() + spell.getTeachMaxLevel() - 1 ):
			#	continue	# 隐藏已经学会的技能
			name = spell.getName()
			type = 0	# 暂时全为0
			level = spell.getReqLevel()
			cost = spell.getCost()
			self.attrTrainInfo[id] = [name, type, level, cost]
		GUIFacade.showLearnSkillWindow( self )

	def getLearnSkillIDs( self ) :
		"""
		获取所有学习技能，重载是因为骑宠导师
		不能每次都过滤掉相对某个骑宠的不可用技能
		"""
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
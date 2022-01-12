# -*- coding: gb18030 -*-

"""
精简怪物类
"""
from MiniMonster_Mini import MiniMonster_Mini
import BigWorld
import csdefine
import csstatus
from bwdebug import *
import time

class MiniMonster( MiniMonster_Mini ):
	"""
	基本精简怪物类，主要功能有：
	1、敌人有效性检查
	2、清理不在视野范围的敌人
	3、每隔4秒选择最高伤害为目标
	"""
	def __init__( self ):
		"""
		初始化
		"""
		MiniMonster_Mini.__init__( self )
		self.skillID = 0
		
	def onFightAIHeartbeat( self, selfEntity ):
		"""
		战斗状态下AI 的 心跳
		"""
		MiniMonster_Mini.onFightAIHeartbeat( self, selfEntity )
		
		# 每隔3秒选择最高伤害为目标
		if selfEntity.fightStartTime > 0 and  int( ( time.time() - selfEntity.fightStartTime ) ) % 3 == 1:
			self.getFirstDamage( selfEntity )
			if selfEntity.hasEnemy( selfEntity.aiTargetID ) and BigWorld.entities.has_key( selfEntity.aiTargetID ) and selfEntity.targetID != selfEntity.aiTargetID:
				selfEntity.changeAttackTarget( selfEntity.aiTargetID )

	def getFirstDamage( self, selfEntity ):
		"""
		选择最高伤害目标
		"""
		eid = 0
		rval = 0
		for id, val in selfEntity.damageList.iteritems():
			if val > rval:
				rval = val
				eid = id
		if eid > 0:
			 selfEntity.aiTargetID = eid
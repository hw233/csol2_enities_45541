# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC基类
"""

import BigWorld
from bwdebug import *
import csdefine
import ECBExtend
from Monster import Monster
from CPUCal import CPU_CostCal

class NPC( Monster ):
	"""
	NPC基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Monster.__init__( self )

	def onHangAndKill( self, timerID, cbID ):
		"""
		挂起并杀死
		"""
		self.changeState( csdefine.ENTITY_STATE_HANG )
		self.destroy()

	def onUnhang( self, timerID, cbID ):
		"""
		取消挂起
		"""
		self.changeState( csdefine.ENTITY_STATE_FREE )


	# 思考
	def onThink( self ):
		"""
		virtual method.
		"""
		if not self.canThink():
			return

		if self.state == csdefine.ENTITY_STATE_FIGHT:
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FIGHT, self.className )
			self.onFightAIHeartbeat()
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FIGHT, self.className )
		else:
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FREE, self.className )
			self.onNoFightAIHeartbeat()
			CPU_CostCal( csdefine.CPU_COST_AI, csdefine.CPU_COST_AI_FREE, self.className )
			
			if self.actionSign( csdefine.ACTION_FORBID_MOVE ):
				DEBUG_MSG( "im cannot the move!" )
				self.stopMoving()
			elif self.state == csdefine.ENTITY_STATE_FREE:											# 执行散步或巡逻判断
				if not self.isMoving():																# 正在移动时(不论原因)
					if self.move_speed > 0:
						if not self.patrolList and self.randomWalkRange > 0:														# 如果没有固定巡逻路线
							if self.randomWalkTime <= 0:
								self.doRandomWalk()													# 随机移动
							else:
								self.randomWalkTime -= 1
						else:
							if self.canPatrol:
								self.doPatrol( self.patrolPathNode, self.patrolList )
					elif self.fightStateAICount <= 0 and self.noFightStateAICount <= 0:				# 如果NPC速度小于0，且没有ai需要运行，那么停止think
						return

		self.think( 1.0 )
		

# NPC.py

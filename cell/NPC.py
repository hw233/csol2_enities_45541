# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC����
"""

import BigWorld
from bwdebug import *
import csdefine
import ECBExtend
from Monster import Monster
from CPUCal import CPU_CostCal

class NPC( Monster ):
	"""
	NPC����
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		Monster.__init__( self )

	def onHangAndKill( self, timerID, cbID ):
		"""
		����ɱ��
		"""
		self.changeState( csdefine.ENTITY_STATE_HANG )
		self.destroy()

	def onUnhang( self, timerID, cbID ):
		"""
		ȡ������
		"""
		self.changeState( csdefine.ENTITY_STATE_FREE )


	# ˼��
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
			elif self.state == csdefine.ENTITY_STATE_FREE:											# ִ��ɢ����Ѳ���ж�
				if not self.isMoving():																# �����ƶ�ʱ(����ԭ��)
					if self.move_speed > 0:
						if not self.patrolList and self.randomWalkRange > 0:														# ���û�й̶�Ѳ��·��
							if self.randomWalkTime <= 0:
								self.doRandomWalk()													# ����ƶ�
							else:
								self.randomWalkTime -= 1
						else:
							if self.canPatrol:
								self.doPatrol( self.patrolPathNode, self.patrolList )
					elif self.fightStateAICount <= 0 and self.noFightStateAICount <= 0:				# ���NPC�ٶ�С��0����û��ai��Ҫ���У���ôֹͣthink
						return

		self.think( 1.0 )
		

# NPC.py

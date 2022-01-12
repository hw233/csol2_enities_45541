# -*- coding: gb18030 -*-
"""
巡游buff，角色骑在坐骑上，不受玩家控制，由服务器通知移动
"""
import BigWorld
import Define
from SpellBase import Buff


class Buff_onPatrol( Buff ):
	"""
	巡游buff，角色骑在坐骑上，不受玩家控制，由服务器通知移动
	"""
	def __init__( self ):
		"""
		"""
		Buff.__init__( self )
		self.targetPreFilter = None

	def cast( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.cast( self, caster, target )
		if target.id == BigWorld.player().id:
			target.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_BUFF_ONPATROL )
			self.targetPreFilter = target.filter
			target.filter = BigWorld.AvatarFilter()

	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.end( self, caster, target )
		if target.id == BigWorld.player().id:
			target.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE, Define.CONTROL_FORBID_ROLE_MOVE_BUFF_ONPATROL )
			target.filter = self.targetPreFilter

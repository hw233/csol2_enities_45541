# -*- coding: gb18030 -*-

# add by gjx 7/1/14

"""
传送技能基础
"""

from SpellBase import *
from bwdebug import *
import csconst
import csdefine

class Spell_TeleportPlane( Spell ):
	"""
	位面传送技能基类
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self._planeType = "" #位面地图名称

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._planeType =  dict["param1"].strip()   	#地图名称

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if receiver.isReal():
			if receiver.spaceType != self._planeType:
				receiver.setTemp("MOVE_INTO_PLANE", True)
				receiver.enterPlane(self._planeType)
		else:
			receiver.receiveOnReal(caster.id, self)


class Spell_TeleportPlaneOnEnterTrap(Spell_TeleportPlane):
	"""
	进入陷阱时触发的位面传送
	"""

	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_TeleportPlane.__init__(self)

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):		# 只对玩家施放（不包括宠物）
			return

		if receiver.isReal():
			tp_plane_counter = receiver.queryTemp("TP_PLANE_COUNTER", 0)
			receiver.setTemp("TP_PLANE_COUNTER", tp_plane_counter + 1)
			INFO_MSG("----->>> Enter: TP_PLANE_COUNTER of %i is %i" % (receiver.id, tp_plane_counter))
			if tp_plane_counter <= 0 and self._planeType:
				INFO_MSG("----->>> Enter: Role %i has been teleported to plane %s" % (receiver.id, self._planeType))
				Spell_TeleportPlane.receive(self, caster, receiver)
		else:
			receiver.receiveOnReal(caster.id, self)


class Spell_TeleportPlaneOnLeaveTrap(Spell_TeleportPlane):
	"""
	离开陷阱时触发的位面传送
	"""

	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_TeleportPlane.__init__(self)

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):		# 只对玩家施放（不包括宠物）
			return

		if receiver.isReal():
			tp_plane_counter = receiver.queryTemp("TP_PLANE_COUNTER", 0)
			INFO_MSG("----->>> Leave: TP_PLANE_COUNTER of %i is %i" % (receiver.id, tp_plane_counter))
			if tp_plane_counter <= 1:
				receiver.removeTemp("TP_PLANE_COUNTER")
				if self._planeType:
					INFO_MSG("----->>> Leave: Role %i has been teleported to plane %s" % (receiver.id, self._planeType))
					Spell_TeleportPlane.receive(self, caster, receiver)
			else:
				receiver.setTemp("TP_PLANE_COUNTER", tp_plane_counter - 1)
		else:
			receiver.receiveOnReal(caster.id, self)

#
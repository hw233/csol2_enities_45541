# -*- coding:gb18030 -*-

import BigWorld
import Math
from bwdebug import *
from SpellBase import *

class Spell_DelayTeleport( Spell ):
	"""
	延迟传送
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		# 传送数据
		self._spaceName = ""         # 空间名称
		self._pos = Math.Vector3()	 # 坐标
		self._npcName = ""			 # NPC名字
		self._delayTime = 0			 # 延迟时间

	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )

		self._spaceName = dict["param1"] if len( dict["param1"] ) > 0 else ""
		pos = dict["param2"] if len( dict["param2"] ) > 0 else ""
		if pos:
			self._pos = Math.Vector3( eval( pos ) )
		self._npcName = dict["param3"] if len( dict["param3"] ) > 0 else ""
		self._delayTime = int( dict["param4"] if len( dict["param4"] ) > 0 else 0 )

	def receive( self, caster, receiver ):
		"""
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		if caster.isReal():
			Spell.receive( self, caster, receiver )

		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		receiver.receiveSpell( caster.id, self.getID(), 0, 0, 0 )

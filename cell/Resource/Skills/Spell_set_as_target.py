# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq

import csdefine
import csstatus
from SpellBase.Spell import Spell
import Love3

class Spell_set_as_target( Spell ):
	"""
	火力吸引
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		self._param1 = float( dict["param1"] )
		Spell.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		技能实现的目的
		"""
		players = receiver.entitiesInRangeExt( self._param1, "Role", receiver.position )
		for i in players:
			i.clientEntity( caster.id ).onSetAsTarget()

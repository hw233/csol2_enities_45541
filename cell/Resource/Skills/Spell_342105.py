# -*- coding: gb18030 -*-
#

import csdefine
from SpellBase import *


class Spell_342105( Spell ):
	"""
	#清怪
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.param1 = int( dict[ "param1" ] )

	def receive( self, caster, receiver ):
		"""
		技能命中时的消息回调
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		"""
		monster = receiver.entitiesInRangeExt( self.param1, "MonsterYayu", receiver.position )
		if len( monster ) == 0:
			return
		for e in monster:
			e.die( caster.id )

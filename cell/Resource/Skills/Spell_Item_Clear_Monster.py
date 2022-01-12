# -*- coding: gb18030 -*-
#

import csdefine
from SpellBase import *
from Spell_Item import Spell_Item


class Spell_Item_Clear_Monster( Spell_Item ):
	"""
	#清怪
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.param1 = int( dict[ "param1" ] )

	def cast( self, caster, receiver ):
		"""
		技能命中时的消息回调
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		"""
		Spell_Item.cast( self, caster, target )
		monster = caster.entitiesInRangeExt( self.param1, "MonsterYayu", caster.position )
		if len( monster ) == 0:
			return
		for e in monster:
			e.die( caster.id )

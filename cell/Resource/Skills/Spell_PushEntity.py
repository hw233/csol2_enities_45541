# -*- coding:gb18030 -*-

from SpellBase import Spell
from bwdebug import *
import ECBExtend

class Spell_PushEntity( Spell ):
	"""
	NPC技能，静电立场（将玩家吸附到附近的施法者创建的陷阱中去）
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

	def receive( self, caster, receiver ):
		for entity in caster.entitiesInRangeExt( 50.0, "AreaRestrictTransducer", caster.position ):
			if entity.casterID == caster.id and isinstance( receiver, BigWorld.Entity ):
				receiver.position = entity.position
				self.receiveLinkBuff( caster, receiver )
			
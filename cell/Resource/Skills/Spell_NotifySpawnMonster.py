# -*- coding:gb18030 -*-

from SpellBase import Spell
from bwdebug import *
import ECBExtend

class Spell_NotifySpawnMonster( Spell ):
	"""
	水晶副本专用，通知副本开始第二关、第三关刷怪
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
		if receiver.isDestroyed:
			return
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		spaceEntity = BigWorld.entities.get( receiver.getCurrentSpaceBase().id, None )
		if spaceEntity:
			spaceEntity.startSpawnMonsterBySkill()
		self.receiveLinkBuff( caster, receiver )
		
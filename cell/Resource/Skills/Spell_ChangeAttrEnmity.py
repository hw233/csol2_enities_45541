# -*- coding: gb18030 -*-

from bwdebug import *
from SpellBase import Spell

class Spell_ChangeAttrEnmity( Spell ):
	"""
	让范围内怪物攻击自己敌人列表里的指定怪物
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.callMonsterID = ""
		self.callRange = 0
		self.attackTargetIndex = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.callMonsterID = dict["param1"]
		self.callRange = float( dict["param2"] )
		self.attackTargetIndex = int( dict["param3"] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		Spell.receive( self, caster, receiver )
		targetID = caster.getEnemyByIndex( self.attackTargetIndex )
		if targetID:
			for e in caster.entitiesInRangeExt( self.callRange, "Monster", caster.position ):
				if e.className == self.callMonsterID:
					e.targetID = targetID
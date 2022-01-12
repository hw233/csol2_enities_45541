# -*- coding: gb18030 -*-
#
#edit by wuxo 2013-12-24
from SpellBase import Spell
import BigWorld
from gbref import rds

class Spell_Teleport( Spell ):
	"""
	同地图传送 无缝接入另一条飞翔路径
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
	
	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		if targetObject.getObject() == BigWorld.player():
			rds.roleFlyMgr.stopFly( False )
			BigWorld.player().checkTelepoertFly()
	

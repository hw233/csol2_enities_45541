# -*- coding: gb18030 -*-

"""
为40级剧情副本飞翔状态结束返回而制作的技能
"""

import csdefine
import BigWorld
from gbref import rds
from SpellBase import *

class Spell_322506( Spell ):
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell.__init__( self )
		self._paths = []
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		self._paths = str( dict[ "param1" ] ).split(";")
		
	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		if len(self._paths) > 0 and BigWorld.player().hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ):
			rds.roleFlyMgr.doCheckFly( self._paths, self.onEndFly )
			
	def onEndFly(self):
		"""
		结束飞行回调
		"""
		rds.roleFlyMgr.stopFly(False)
		BigWorld.player().physics.fall = True
		BigWorld.player().cell.requestClearBuffer()			#通知服务器结束飞翔传送buffer
		
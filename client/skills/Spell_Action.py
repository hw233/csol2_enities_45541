# -*- coding: gb18030 -*-

"""
为40级剧情副本飞翔状态中播放动作而制作的技能
"""
import BigWorld
from SpellBase import *
from gbref import rds

class Spell_Action( Spell ):
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell.__init__( self )
		self._actionName = ""
		self._playAniScale = None
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		self._actionName = str(dict["param1"])
		if dict["param2"] != "":
			self._playAniScale = float(dict["param2"])
		
	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		model = caster.model
		if model:
			model.action(self._actionName)()
		if self._playAniScale is not None:
			BigWorld.player().am.playAniScale = self._playAniScale
			
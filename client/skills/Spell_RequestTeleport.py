# -*- coding: gb18030 -*-
#
#edit by wuxo 2012-8-20


"""
客户端申请传送（用于客户端镜头）脚本
"""

from SpellBase import Spell
import BigWorld

class Spell_RequestTeleport( Spell ):
	"""
	传送技能基础
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
		Spell.init( self, dict )
	
	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		player = BigWorld.player()
		player.cell.requestTeleport( )
	

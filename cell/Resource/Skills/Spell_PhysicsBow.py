# -*- coding: gb18030 -*-
#
# $Id: Spell_PhysicsBow.py,v 1.3 2008-03-03 06:34:23 kebiao Exp $

"""
持续性效果
"""

from bwdebug import *
from Spell_Physics import Spell_Physics

class Spell_PhysicsBow( Spell_Physics ):
	"""
	普通物理伤害，用于弓等远程武器
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Physics.__init__( self )


	def calcDelay( self, caster, target ):
		"""
		virtual method.
		取得伤害延迟
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: float(秒)
		"""
		#这个和底层spell是一样的 由于继承自Spell_Physics所以要还原功能
		return target.calcDelay( self, caster )
		

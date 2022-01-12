# -*- coding: gb18030 -*-

import BigWorld
import csstatus
from SpellBase import *

class Spell_LevelUpDamage( Spell ):
	"""
	升级触发范围伤害技能专用脚本
	"""
	def __init__( self ):
		"""
		构造函数
		"""
		Spell.__init__( self )
		self._damage = 0	# 技能伤害

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._damage = int( dict["param1"] ) if len( dict["param1"] ) > 0 else 0

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用
		return type:int
		"""
		if caster.vehicleDBID:	# 骑乘状态下无法触发
			return csstatus.SKILL_NO_MSG

		return csstatus.SKILL_GO_ON
# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Cannot_PK.py by pengju
"""
使用物品使自己无敌
"""

from Spell_BuffNormal import Spell_ItemBuffNormal
import csstatus

class Spell_Item_Cannot_PK( Spell_ItemBuffNormal ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_ItemBuffNormal.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		self._castLvMax = dict[ "CastObjLevelMax" ] if dict[ "CastObjLevelMax" ] else 0
		Spell_ItemBuffNormal.init( self, dict )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		targetEntity = target.getObject()
		if targetEntity.level > self._castLvMax:
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return Spell_ItemBuffNormal.useableCheck( self, caster, target )
# -*- coding: gb18030 -*-
#
# 使用物品使自己无敌的客户端技能 by pengju
#
from Spell_Item import Spell_Item
import csstatus

class Spell_Item_Cannot_PK( Spell_Item ):
	"""
	使用物品使自己无敌的客户端技能
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		self._castLvMax = dict[ "CastObjLevelMax" ] if dict[ "CastObjLevelMax" ] else 0
		Spell_Item.init( self, dict )

	def useableCheck( self, caster, target ):
		"""
		校验技能是否可以使用。

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		targetEntity = target.getObject()
		if targetEntity.level > self._castLvMax:
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return Spell_Item.useableCheck( self, caster, target )


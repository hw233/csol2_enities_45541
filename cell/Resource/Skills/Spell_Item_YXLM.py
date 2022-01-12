# -*- coding:gb18030 -*-

from Spell_BuffNormal import Spell_BuffNormal


# 英雄联盟副本的NPC装备不放入玩家的背包，
# 只是建立了一个临时的属性存放，因此不能
# 走普通物品的使用流程，因为普通物品使用
# 时会从玩家背包中查找使用的物品，这会导
# 致物品找不到的问题
class Spell_Item_YXLM( Spell_BuffNormal ) :

	def cast( self, caster, target ):
		"""
		virtual method.
		正式向一个目标或位置施放（或叫发射）法术，此接口通常直接（或间接）由intonate()方法调用。

		注：此接口即原来旧版中的castSpell()接口

		@param     caster: 使用技能的实体
		@type      caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell_BuffNormal.cast( self, caster, target )
		caster.removeTemp( "item_using" )

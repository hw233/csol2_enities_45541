# -*- coding:gb18030 -*-

from Spell_BuffNormal import Spell_BuffNormal
import csstatus
import csdefine
from bwdebug import *

class Spell_PushDrag( Spell_BuffNormal ):
	"""
	增进玩家间互动的娱乐道具
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )

	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		targetObject = target.getObject()
		if caster == targetObject:								# 受术者不包括自己
			return csstatus.SKILL_NOT_ROLE_ENTITY
		if targetObject.hasFlag( csdefine.ROLE_FLAG_FLY ):  	# 受术者飞行状态检测
			return csstatus.SKILL_TARGET_FLYING
		if targetObject.state == csdefine.ENTITY_STATE_DEAD:    # 受术者死亡状态检测
			return csstatus.SKILL_TARGET_DEAD
		return Spell_BuffNormal.useableCheck( self, caster, target )

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
		self.updateItem( caster )

	def updateItem( self, caster ):
		"""
		更新物品使用
		"""
		uid = caster.popTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			printStackTrace()
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		item.onSpellOver( caster )
		caster.removeTemp( "item_using" )
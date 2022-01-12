# -*- coding: gb18030 -*-
#
# $Id: Spell_TeleportBase.py,v 1.1 2009-09-21 04:04:50 pengju Exp $

"""
传送技能基础类
"""
import BigWorld
import csstatus
import csdefine
from SpellBase import *
import Const

class Spell_TeleportBase( Spell ):
	"""
	传送技能基础类
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
		# 玩家当前不受控制，则不能传送
		if not caster.controlledBy :
			return csstatus.SKILL_CANT_USE_IN_LOSE_CONTROL

		#处理沉默等一类技能的施法判断
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB

		#携带跑商物品，不能使用
		if caster.hasMerchantItem() or caster.hasFlag( csdefine.ROLE_FLAG_BLOODY_ITEM ):
			return csstatus.MERCHANT_ITEM_CANT_FLY

		# 如果有法术禁咒buff
		if len( caster.findBuffsByBuffID( Const.FA_SHU_JIN_ZHOU_BUFF ) ) > 0:
			return csstatus.SKILL_CANT_CAST

		#在监狱中不能传送
		if caster.getCurrentSpaceType() == csdefine.SPACE_TYPE_PRISON :
			return csstatus.SPACE_MISS_LEAVE_PRISON
		if caster.getCurrentSpaceType() == csdefine.SPACE_TYPE_TONG_TURN_WAR:
			return csstatus.SKILL_CANT_CAST

		# 防止其他原因导致的不可施法
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
			return csstatus.SKILL_CANT_CAST
		return Spell.useableCheck( self, caster, target )

# $Log: not supported by cvs2svn $
#
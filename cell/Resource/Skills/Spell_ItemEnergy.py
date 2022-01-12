# -*- coding: gb18030 -*-
#
#

import Const
import csstatus
from Spell_ItemCure import Spell_ItemCure

class Spell_ItemEnergy( Spell_ItemCure ):
	"""
	精力恢复 活血丹
	"""
	def __init__( self ):
		"""
		"""
		Spell_ItemCure.__init__( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		#这句必须放在最前面 请参考底层
		Spell_ItemCure.receive( self, caster, receiver )
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		lostEN = Const.ROLE_EN_MAX_VALUE - receiver.energy
		curEN = min( self._effect_max, max( self._effect_min, lostEN ) )
		item.setTemp( "sd_usePoint", curEN )
		receiver.gainEnergy( lostEN, False )
		receiver.statusMessage( csstatus.SKILL_ENERGY_CURE, item.name(), lostEN )

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
		if target.getObject().energy == Const.ROLE_EN_MAX_VALUE:
			return csstatus.SKILL_CURE_NONEED
		return Spell_ItemCure.useableCheck( self, caster, target)

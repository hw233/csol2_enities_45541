# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
技能对物品施展法术基础。
"""

import csstatus
import random
import csdefine
import cschannel_msgs
from Spell_Item import Spell_Item

class Spell_ItemTiShou( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		#这句必须放在最前面 请参考底层
		Spell_Item.receive( self, caster, receiver )
		#caster.client.openTiShouSelect()
		#caster.setTemp( "allowTiShou", True)
		caster.createTSNPC( caster.id, 1, cschannel_msgs.TISHOU_INFO_01%caster.playerName )

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
		if not target.getObject().canVendInArea():
			return csstatus.TISHOU_FORBID_AREA
		if target.getObject().level < 15:
			return csstatus.TISHOU_FORBID_LEVEL
		if target.getObject().hasFlag( csdefine.ROLE_FLAG_TISHOU ):
			target.getObject().client.onStatusMessage( csstatus.ROLE_ALREADY_TISHOU, "" )
			return csstatus.SKILL_ITEM_NOT_READY
		if caster.isState( csdefine.ENTITY_STATE_VEND ) :
			caster.client.onStatusMessage( csstatus.TISHOU_FORBID_VENDING, "" )
			return csstatus.SKILL_ITEM_NOT_READY
		return Spell_Item.useableCheck( self, caster, target)


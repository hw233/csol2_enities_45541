# -*- coding: gb18030 -*-
"""
使用锦囊的技能
"""
import csstatus
import BigWorld
from Spell_Item import Spell_Item
from bwdebug import *


class Spell_912311001( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		item.freeze(caster)				#冻结物品
		caster.onlottery( item.uid )	#通知物品开始抽奖
		Spell_Item.receive( self, caster, receiver )

	def updateItem( self , caster ):
		"""
		更新物品使用
		注：这里只是去掉物品的使用，并不删除物品，当抽奖的物品放到玩家身上时再删除锦囊
		"""
		caster.removeTemp( "item_using" )

	def useableCheck( self, caster, target ):
		"""
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		主要是屏蔽信息，避免不能使用物品时提示使用技能
		"""
		if caster.havelotteryItem():		#如果当前正在使用该物品
			return csstatus.SKILL_ITEM_NOT_READY

		return Spell_Item.useableCheck( self, caster, target )
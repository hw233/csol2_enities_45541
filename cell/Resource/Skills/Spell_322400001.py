# -*- coding: gb18030 -*-

from bwdebug import *
from Spell_Item import Spell_Item
import csdefine


class Spell_322400001( Spell_Item ):
	"""
	物品红包的技能
	第一次使用触发给红包充钱的功能；
	第二次使用则使用者会活动相应金钱。
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
		Spell_Item.init( self, dict )


	def updateItem( self, caster ):
		"""
		更新物品
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return

		if item.query( "hide_money", 0 ) == 0:	# 如果红包里面没钱，表明是第一次使用，不需要更新物品
			caster.removeTemp( "item_using" )
			return

		caster.removeTemp( "item_using" )
		item.onSpellOver( caster )


	def receive( self, caster, receiver ):
		"""
		接收法术
		"""
		uid  = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		isCharge = item.query( "hide_money", 0 ) > 0
		if not isCharge:	# 如果红包里没钱，通知玩家充值
			receiver.client.couple_requestChargeHongbao( item.order )
			return

		receiver.addMoney( item.query( "hide_money" ), csdefine.CHANGE_MONEY_REDPACKAGE  )
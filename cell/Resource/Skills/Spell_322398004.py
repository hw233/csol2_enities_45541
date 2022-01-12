# -*- coding: gb18030 -*-


import Const

from bwdebug import *
from Spell_Item import Spell_Item
from Love3 import g_itemDropLuckyBoxZhaocai
import csdefine
import csstatus

class Spell_322398004( Spell_Item ):
	"""
	物品技能：招财宝盒
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


	def receive( self, caster, receiver ):
		"""
		virtual method.
		针对每一个受术者进行受术处理，如计算伤害、改变属性等等。通常情况下此接口是由onArrive()调用，
		但它亦有可能由SpellUnit::receiveOnreal()方法调用，用于处理一些需要在受术者的real entity身上作的事情。
		但对于是否需要在real entity身上接收，由技能设计者在receive()中自行判断，并不提供相关机制。
		注：此接口为旧版中的onReceive()

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		# 根据caster身上的宝盒物品级别给玩家加上获得的物品
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "招财宝盒：player( %s )'s item is None.uid:%i." % ( caster.getName(), uid ) )
			return

		dropType, dropInstance = g_itemDropLuckyBoxZhaocai.getDropData( item.getLevel() )
		
		if dropType == Const.LUCKY_BOX_DROP_MONEY:
			caster.addMoney( dropInstance, csdefine.CHANGE_MONEY_LUCKYBOXZHAOCAI )
		elif dropType == Const.LUCKY_BOX_DROP_POTENTIAL:
			caster.addPotential( dropInstance, csdefine.CHANGE_POTENTIAL_ZHAOCAI )
		elif dropType == Const.LUCKY_BOX_DROP_EXP:
			caster.addExp( dropInstance, csdefine.CHANGE_EXP_LUCKYBOXZHAOCAI )
		else:
			caster.addItem( dropInstance, csdefine.ADD_ITEM_LUCKYBOXZHAOCAI )

	def useableCheck( self, caster, target ):
		"""
		需要有一个空格才可以打开宝盒。避免无法获得物品
		"""
		if caster.getNormalKitbagFreeOrderCount() < 1:
			return csstatus.SKILL_USE_ITEM_NEED_ONE_BLANK
		return Spell_Item.useableCheck( self, caster, target )
		
# -*- coding: gb18030 -*-


import Const

from bwdebug import *
from Spell_Item import Spell_Item
import csdefine
import csstatus
import csconst

class Spell_Reward_Quest_Item( Spell_Item ):
	"""
	物品技能：刷新悬赏任务
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
			ERROR_MSG( "RewardQuest Item：player( %s )'s item is None.uid:%s." % ( caster.getName(), uid ) )
			return

		if item.id == csconst.REWARD_QUEST_LOW_ITEM:
			receiver.rewardQuestItemRefresh( 1, csdefine.REWARD_QUEST_LOW_ITEM_REFRESH )
		elif item.id == csconst.REWARD_QUEST_HIGH_ITEM:
			receiver.rewardQuestItemRefresh( 1, csdefine.REWARD_QUEST_HIGH_ITEM_REFRESH )

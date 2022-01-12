# -*- coding: gb18030 -*-

from bwdebug import *
from Spell_Item import Spell_Item
from Spell_TeleportBase import Spell_TeleportBase
import csstatus
import csconst
import csdefine
import BigWorld

 
class Spell_912313( Spell_Item ):
	"""
	烈焰玫瑰：增加友好度
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		
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
	
		
		
		state = Spell_Item.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:	# 先检查cooldown等条件
			return state
			
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		
		# 友好度道具增加对目标的判断 by mushuang		
		targetEntity = target.getObject()
		
	
		# if 目标不是玩家 :
		if not targetEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
			return csstatus.FRIEND_ITEM_USED_ONLY_ON_FRIEND
			
		# if 目标是自己 
		if caster.id == targetEntity.id :
			return csstatus.FRIEND_ITEM_USED_ONLY_ON_FRIEND
		
		# if 判断玩家A（使用者）和玩家B无友好关系
		caster.setTemp( "addFriendlyRequesting", True )
		caster.setTemp( "addFriendlyName",targetEntity.getName() )
		caster.base.rlt_checkAddFriendyValue( target.getObject().databaseID )
		return state
		
	def onSpellInterrupted( self, caster ):
		"""
		当施法被打断时的通知；
		打断后需要做一些事情
		"""
		Spell_Item.onSpellInterrupted( self, caster )
		caster.removeTemp( "addFriendlyRequesting" )
		
	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		针对每一个受术者进行受术处理，如计算伤害、改变属性等等。通常情况下此接口是由onArrive()调用，
		但它亦有可能由SpellUnit::receiveOnreal()方法调用，用于处理一些需要在受术者的real entity身上作的事情。
		但对于是否需要在real entity身上接收，由技能设计者在receive()中自行判断，并不提供相关机制。
		注：此接口为旧版中的onReceive()
		
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		caster.removeTemp( "addFriendlyRequesting" )
		casterName = caster.getName()
		receiverName = receiver.getName()
		caster.base.addItemFriendlyValue( receiver.databaseID, self._effect_max )
		receiver.base.addItemFriendlyValue( caster.databaseID, self._effect_max )
		itemName = caster.getByUid( caster.queryTemp( "item_using" ) ).name()
		caster.statusMessage( csstatus.FRIEND_ITEM_ADD_VALUE_SUCCESS, receiverName, itemName, receiverName, self._effect_max )
		receiver.client.onStatusMessage( csstatus.FRIEND_ITEM_BE_ADDED_VALUE_SUCCESS, "(\'%s\', \'%s\', \'%s\', %i)" % ( casterName, itemName, casterName, self._effect_max ) )
		
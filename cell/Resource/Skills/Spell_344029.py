# -*- coding:gb18030 -*-

from Spell_Item import Spell_Item
import csstatus
from bwdebug import *

class Spell_344029( Spell_Item ):
	"""
	增加玩家帮供
	"""
	def __init__( self ):
		Spell_Item.__init__( self )
		self.tongContribute = 0
		
	def init( self, data ):
		Spell_Item.init( self, data )
		self.tongContribute = int( data["param1"] ) if len( data["param1"] ) else 0
		
	def useableCheck( self, caster, target ):
		"""
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		roleEntity = target.getObject()
		if roleEntity is None or not hasattr( roleEntity, "tong_addContribute" ):
			ERROR_MSG( "targetEnity( %s ) is not Role" % roleEntity.getName() )
			return csstatus.SKILL_CANT_CAST_ENTITY
		if not roleEntity.isJoinTong():
			return csstatus.SKILL_ITEM_ADD_NOT_TONG_ATTRIBUTE
		return Spell_Item.useableCheck( self, caster, target )
		
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
		receiver.tong_addContribute( self.tongContribute )
		Spell_Item.receive( self, caster, receiver )
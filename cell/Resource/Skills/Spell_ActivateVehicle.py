# -*- coding: gb18030 -*-
#
# edit by wuxo 2013-3-27

from Spell_BuffNormal import Spell_BuffNormal
import csstatus
from bwdebug import *

class Spell_ActivateVehicle( Spell_BuffNormal ):
	"""
	激活骑宠技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_BuffNormal.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
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
		return Spell_BuffNormal.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method = 0
		针对每一个受术者进行受术处理，如计算伤害、改变属性等等。通常情况下此接口是由onArrive()调用，
		但它亦有可能由SpellUnit::receiveOnreal()方法调用，用于处理一些需要在受术者的real entity身上作的事情。
		但对于是否需要在real entity身上接收，由技能设计者在receive()中自行判断，并不提供相关机制。
		注：此接口为旧版中的onReceive()

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		receiverEntity = caster
		#在这里清除身上的其他激活骑宠buff是为了currAttrVehicleData属性可能会在buffend中被默认赋值
		receiverEntity.cancelActiveVehicle()
		
		vehicleData = receiverEntity.popTemp( "activateVehicleData", {} )
		if not vehicleData:
			return
		receiverEntity.onactivateVehicle( vehicleData )
		self.receiveLinkBuff( receiverEntity, receiverEntity )



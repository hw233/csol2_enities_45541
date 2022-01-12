# -*- coding: gb18030 -*-
#
# $Id: Spell_ConjureVehicle.py,v 1.1 2008-09-04 06:43:15 yangkai Exp $

"""
"""
import csconst
from SpellBase import Spell
import csstatus
from bwdebug import *
from Resource.SkillLoader import g_skills
from VehicleHelper import canMount,getVehicleSkillID



class Spell_ConjureVehicle( Spell ):
	"""
	召唤骑宠技能
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
		
		targetEntity = target.getObject()
		if not targetEntity:
			ERROR_MSG( "Can't find target entity!" )
			return
		
		vehicleData = caster.queryTemp( "conjureVehicleData", {} )
		
		# 如果不能骑乘，那么不可以召唤骑宠
		state = canMount( targetEntity, vehicleData["id"], vehicleData["type"] )
		if state != csstatus.SKILL_GO_ON :
			return state
		if  vehicleData["level"] - caster.level >= csconst.VEHICLE_DIS_LEVEL_MAX:
			return csstatus.VEHICLE_NO_CONJURE
			
		skillID = getVehicleSkillID( vehicleData )
		try:
			skill = g_skills[ skillID ]
		except:
			ERROR_MSG( "Can't load vehicle binded skill: %s"%skillID )
			return csstatus.SKILL_CANT_CAST
		
		# 如果与要召唤骑宠绑定的技能否决了召唤请求，那么不可召唤骑宠
		status = skill.useableCheck( caster, target )
		if status != csstatus.SKILL_GO_ON:
			return status
		
		return Spell.useableCheck( self, caster, target )

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
		
		vehicleData = receiverEntity.popTemp( "conjureVehicleData", {} )
		if not vehicleData:
			ERROR_MSG( "Can't find vehicle data! player(%s)" %receiverEntity.playerName  )
			return
		receiverEntity.onConjureVehicle( vehicleData )
		

# $Log: not supported by cvs2svn $

# -*- coding: gb18030 -*-

import BigWorld
import csstatus
import csdefine
from Spell_BuffNormal import Spell_ItemBuffNormal


class Spell_111006( Spell_ItemBuffNormal ):
	"""
	对目标单位造成相当于其生命值上限xx%的伤害
	"""
	def __init__( self ):
		"""
		"""
		Spell_ItemBuffNormal.__init__( self )
		self.param = []
		self.damage = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_ItemBuffNormal.init( self, dict )
		self.param1 = int( dict["param1"] if len( dict["param1"] ) > 0 else 10 )  / 100.0  # 伤害百分比
		self.param2 = dict["param2"]   													   # 伤害目标列表

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
		target = target.getObject()
		# 目标血量低于10%不能施法
		if target.HP <= target.HP_Max * self.param1:
			return csstatus.SKILL_TARGET_IS_GOING_TO_DIE
		List = self.param2.split("|")
		for i in List:
			self.param.append(i)
		# 只能对指定的目标施法
		if not target.className in self.param:
			return csstatus.SKILL_INVALID_ENTITY
		# 防止其他原因导致的不可施法
		if caster.actionSign( csdefine.ACTION_FORBID_USE_ITEM ):
			if caster.getState() == csdefine.ENTITY_STATE_PENDING:
				return csstatus.CIB_MSG_PENDING_CANT_USE_ITEM
			return csstatus.CIB_MSG_TEMP_CANT_USE_ITEM
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		# 检查技能cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_ITEM_NOT_READY
		return csstatus.SKILL_GO_ON

	def calReduceDamage( self,caster, receiver ):
		"""
		计算实际减伤率
		等级修正 = (攻方等级-守方等级)*4% 
		实际减伤=MAX(守方御敌属性-攻方破敌属性-等级修正,0) 
		"""
		disLevel = 0
		if caster.level  > receiver.level:
			disLevel = ( caster.level - receiver.level ) * 0.04
		
		return max( receiver.reduce_role_damage - caster.add_role_damage - disLevel, 0.0 )
	
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
		if caster.isReal():
			Spell_ItemBuffNormal.receive( self, caster, receiver )

		self.damage = int( receiver.HP_Max * self.param1 )
		#计算御敌、破敌带来的实际减免 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		self.damag *= rm

		receiver.receiveDamage( caster.id, self, csdefine.DAMAGE_TYPE_PHYSICS_NORMAL, self.damage )
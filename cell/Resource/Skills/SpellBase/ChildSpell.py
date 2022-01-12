# -*- coding: gb18030 -*-
#
# $Id: ChildSpell.py,v 1.1 2007-12-11 08:04:36 kebiao Exp $

"""
"""

import Language
from bwdebug import *
from CombatSpell import CombatSpell
import csstatus

class ChildSpell( CombatSpell ):
	"""
	一个法术的子技能。 通常使用与(散射型)群体法术中.
	该子技能拥有父技能的攻击特性和参数。  忽略吟唱和冷却等判定, 
	父技能在群攻中找到要伤害的所有ENTITY后，向每一个entity都释放一个该子技能
	"""
	def __init__( self, parent ):
		"""
		构造函数。
		"""
		CombatSpell.__init__( self )
		self.parent = parent
		
	def init( self, dictDat ):
		"""
		读取技能配置
		"""
		self.__dict__.update( self.parent.__dict__ )

	def doRequire_( self, caster ):
		"""
		virtual method.
		处理消耗

		@param caster	:	释放者实体
		@type caster	:	Entity
		"""
		pass

	def setCooldownInIntonateOver( self, caster ):
		"""
		virtual method.
		给施法者设置法术本身的cooldown时间

		@return: None
		"""
		pass
		

	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		entity = target.getObject()
		if entity is None:
			return []
		return [ entity ]

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
		#子技能无法决定父技能的计算方式(法术，物理等特性),因此转给父技能去产生作用
		self.parent.receive( caster, receiver )
		
#
# $Log: not supported by cvs2svn $
#
#
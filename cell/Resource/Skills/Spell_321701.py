# -*- coding: gb18030 -*-
#
# $Id: Spell_311413.py,v 1.7 2008-07-15 04:06:26 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill2
import random
import csdefine

class Spell_321701( Spell_PhysSkill2 ):
	"""
	冲锋 冲向敌人，快速靠近目标，造成一定的伤害，8米之内，20米之外不能冲锋
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill2.__init__( self )
		self._triggerBuffInterruptCode = []							# 该技能触发这些标志码中断某些BUFF

	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill2.init( self, dict )
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )

	def getCastRange( self, caster ):
		"""
		法术释放距离
		"""
		return self.getRangeMax( caster ) + 5

	def cast( self, caster, target ):
		"""
		virtual method.
		正式向一个目标或位置施放（或叫发射）法术，此接口通常直接（或间接）由intonate()方法调用。

		注：此接口即原来旧版中的castSpell()接口

		@param     caster: 使用技能的实体
		@type      caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		caster.setMoveSpeed( self.getFlySpeed() )
		caster.clearBuff( self._triggerBuffInterruptCode ) #删除自身现在所有可以删除的BUFF
		#通知所有客户端播放动作/做其他事情
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		self.setCooldownInIntonateOver( caster )
		# 处理消耗
		self.doRequire_( caster )
		#保证客户端和服务器端处理的受术者一致
		delay = self.calcDelay( caster, target )
		# 延迟
		caster.addCastQueue( self, target, delay + 0.35 )
		# 法术施放完毕通知，不一定能打中人哦(是否能打中已经和施法没任何关系了)！
		# 如果是channel法术(未实现)，只有等法术结束后才能调用
		self.onSkillCastOver_( caster, target )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		法术抵达目标通告。在默认情况下，此处执行可受术人员的获取，然后调用receive()方法进行对每个可受术者进行处理。
		注：此接口为旧版中的receiveSpell()

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell_PhysSkill2.onArrive( self, caster, target )
		caster.calcMoveSpeed()
		caster.client.onAssaultEnd()

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if receiver.isDestroyed:
			return
		distanceBB = caster.distanceBB( receiver )
		if distanceBB > 3.5:
			return

		damageType = self._damageType
		# 计算命中率
		hit = self.calcHitProbability( caster, receiver )
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			# 被躲开了并不代表我没打你，因此仇恨是有可能存在的，需要通知受到0点伤害
			receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
			receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
			caster.doAttackerOnDodge( receiver, damageType )
			receiver.doVictimOnDodge( caster, damageType )
			return

		# 执行命中后的行为
		caster.doAttackerOnHit( receiver, damageType )	#攻击者触发
		receiver.doVictimOnHit( caster, damageType )   #受击者触发
		self.receiveLinkBuff( caster, receiver )		# 接收额外的CombatSpell效果，通常是buff(如果存在的话)
# -*- coding: gb18030 -*-
#

import csdefine
from SpellBase.CombatSpell import CombatSpell


class Spell_122187( CombatSpell ):
	"""
	#爆炸
	"""
	def __init__( self ):
		"""
		"""
		CombatSpell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		CombatSpell.init( self, dict )
		self.param1 = float( dict[ "param1" ] )

	def onArrive( self, caster, target ):
		"""
		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""

		CombatSpell.onArrive( self, caster, target )
		receivers = self.getReceivers( caster, target )
		# 不管有没有击中目标，不管攻击几个目标，攻击几次
		caster.equipAbrasion( 100.0 )

		# 恶性技能使用触发
		caster.doOnUseMaligSkill( self )
		if not caster.isDestroyed:
			caster.onSkillArrive( self, receivers )

		#对自己造成伤害
		if ( not caster.isDestroyed ) and ( not caster.isDead() ):
			damage = caster.HP + 1  #确保能把自己炸死
			caster.planesAllClients( "receiveSpell", ( caster.id, self.getID(), csdefine.DAMAGE_TYPE_PHYSICS, damage ) )
			caster.setHP( caster.HP - damage )
			# 受到伤害时 抛出buff中断码， 所有配有在受到伤害被消除的buff都被去除
			caster.clearBuff( [csdefine.BUFF_INTERRUPT_GET_HIT] )

			if caster.HP == 0:
				caster.setMP( 0 )
				caster.die( 0 )

	def receive( self, caster, receiver ):
		"""
		技能命中时的消息回调
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		"""
		if caster != receiver:
			damage = int( receiver.HP_Max * self.param1 )
			#计算御敌、破敌带来的实际减免 
			reRate = self.calReduceDamage( caster, receiver )
			rm =  1 - reRate
			damage *= rm

			receiver.receiveSpell( caster.id, self.getID(), csdefine.DAMAGE_TYPE_PHYSICS, damage, 0 )
			receiver.receiveDamage( caster.id, self.getID(), csdefine.DAMAGE_TYPE_PHYSICS, damage )

		self.receiveLinkBuff( caster, receiver )
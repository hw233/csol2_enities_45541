# -*- coding: gb18030 -*-
#

import csdefine
from SpellBase.CombatSpell import CombatSpell


class Spell_122187( CombatSpell ):
	"""
	#��ը
	"""
	def __init__( self ):
		"""
		"""
		CombatSpell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		CombatSpell.init( self, dict )
		self.param1 = float( dict[ "param1" ] )

	def onArrive( self, caster, target ):
		"""
		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""

		CombatSpell.onArrive( self, caster, target )
		receivers = self.getReceivers( caster, target )
		# ������û�л���Ŀ�꣬���ܹ�������Ŀ�꣬��������
		caster.equipAbrasion( 100.0 )

		# ���Լ���ʹ�ô���
		caster.doOnUseMaligSkill( self )
		if not caster.isDestroyed:
			caster.onSkillArrive( self, receivers )

		#���Լ�����˺�
		if ( not caster.isDestroyed ) and ( not caster.isDead() ):
			damage = caster.HP + 1  #ȷ���ܰ��Լ�ը��
			caster.planesAllClients( "receiveSpell", ( caster.id, self.getID(), csdefine.DAMAGE_TYPE_PHYSICS, damage ) )
			caster.setHP( caster.HP - damage )
			# �ܵ��˺�ʱ �׳�buff�ж��룬 �����������ܵ��˺���������buff����ȥ��
			caster.clearBuff( [csdefine.BUFF_INTERRUPT_GET_HIT] )

			if caster.HP == 0:
				caster.setMP( 0 )
				caster.die( 0 )

	def receive( self, caster, receiver ):
		"""
		��������ʱ����Ϣ�ص�
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		"""
		if caster != receiver:
			damage = int( receiver.HP_Max * self.param1 )
			#�������С��Ƶд�����ʵ�ʼ��� 
			reRate = self.calReduceDamage( caster, receiver )
			rm =  1 - reRate
			damage *= rm

			receiver.receiveSpell( caster.id, self.getID(), csdefine.DAMAGE_TYPE_PHYSICS, damage, 0 )
			receiver.receiveDamage( caster.id, self.getID(), csdefine.DAMAGE_TYPE_PHYSICS, damage )

		self.receiveLinkBuff( caster, receiver )
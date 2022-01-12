# -*- coding: gb18030 -*-
#
# $Id: Spell_311413.py,v 1.7 2008-07-15 04:06:26 kebiao Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill2
import random
import csdefine

class Spell_321701( Spell_PhysSkill2 ):
	"""
	��� ������ˣ����ٿ���Ŀ�꣬���һ�����˺���8��֮�ڣ�20��֮�ⲻ�ܳ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill2.__init__( self )
		self._triggerBuffInterruptCode = []							# �ü��ܴ�����Щ��־���ж�ĳЩBUFF

	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill2.init( self, dict )
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )

	def getCastRange( self, caster ):
		"""
		�����ͷž���
		"""
		return self.getRangeMax( caster ) + 5

	def cast( self, caster, target ):
		"""
		virtual method.
		��ʽ��һ��Ŀ���λ��ʩ�ţ���з��䣩�������˽ӿ�ͨ��ֱ�ӣ����ӣ���intonate()�������á�

		ע���˽ӿڼ�ԭ���ɰ��е�castSpell()�ӿ�

		@param     caster: ʹ�ü��ܵ�ʵ��
		@type      caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		caster.setMoveSpeed( self.getFlySpeed() )
		caster.clearBuff( self._triggerBuffInterruptCode ) #ɾ�������������п���ɾ����BUFF
		#֪ͨ���пͻ��˲��Ŷ���/����������
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		self.setCooldownInIntonateOver( caster )
		# ��������
		self.doRequire_( caster )
		#��֤�ͻ��˺ͷ������˴����������һ��
		delay = self.calcDelay( caster, target )
		# �ӳ�
		caster.addCastQueue( self, target, delay + 0.35 )
		# ����ʩ�����֪ͨ����һ���ܴ�����Ŷ(�Ƿ��ܴ����Ѿ���ʩ��û�κι�ϵ��)��
		# �����channel����(δʵ��)��ֻ�еȷ�����������ܵ���
		self.onSkillCastOver_( caster, target )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		�����ִ�Ŀ��ͨ�档��Ĭ������£��˴�ִ�п�������Ա�Ļ�ȡ��Ȼ�����receive()�������ж�ÿ���������߽��д���
		ע���˽ӿ�Ϊ�ɰ��е�receiveSpell()

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell_PhysSkill2.onArrive( self, caster, target )
		caster.calcMoveSpeed()
		caster.client.onAssaultEnd()

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if receiver.isDestroyed:
			return
		distanceBB = caster.distanceBB( receiver )
		if distanceBB > 3.5:
			return

		damageType = self._damageType
		# ����������
		hit = self.calcHitProbability( caster, receiver )
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			# ���㿪�˲���������û���㣬��˳�����п��ܴ��ڵģ���Ҫ֪ͨ�ܵ�0���˺�
			receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
			receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
			caster.doAttackerOnDodge( receiver, damageType )
			receiver.doVictimOnDodge( caster, damageType )
			return

		# ִ�����к����Ϊ
		caster.doAttackerOnHit( receiver, damageType )	#�����ߴ���
		receiver.doVictimOnHit( caster, damageType )   #�ܻ��ߴ���
		self.receiveLinkBuff( caster, receiver )		# ���ն����CombatSpellЧ����ͨ����buff(������ڵĻ�)
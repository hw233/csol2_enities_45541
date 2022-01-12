# -*- coding: gb18030 -*-
#
# $Id: Spell_Physics.py,v 1.28 2008-08-13 07:55:41 kebiao Exp $

"""
������Ч��
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
from bwdebug import *
import Const
from Spell_Physics import Spell_Physics

class Spell_NormalPhysics( Spell_Physics ):
	"""
	��ͨ������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Physics.__init__( self )


	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		�������߳��������˺�
		ͨ��������Щ�����Ҫ���� ��Ҫ���ݶ�ĳentity���������˺� �������������Ӱ��
		"""
		receiver.receiveSpell( caster.id, self.getID(), damageType, damage, 0 )
		receiver.receiveDamage( caster.id, self.getID(), damageType, damage )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if receiver.isDestroyed:
			return

		# ����������
		hit = 0.9
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			self.onMiss( self._damageType, caster, receiver )				# ������δ����
			return

		# ���㼼�ܹ������ͼ���ֱ���˺�
		skillDamage = self.calcSkillHitStrength( caster,receiver, 0, 0 )
		
		#�������С��Ƶд�����ʵ�ʼ��� 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		skillDamage *= rm
		# �����ֻ����˺� ����Ҳ�����1���˺�
		self.persentDamage( caster, receiver, self._damageType, max( 1, int( skillDamage ) ) )

# -*- coding: gb18030 -*-
#
# $Id: Spell_BuffMagic.py,v 1.4 2008-08-13 07:55:41 kebiao Exp $

"""
"""

import csdefine
from SpellBase import *
import csstatus
import random
from Spell_Item import Spell_Item
from Spell_Magic import Spell_Magic
from Spell_Magic import Spell_MagicVolley

class Spell_BuffMagic( Spell_Magic ):
	"""
	�ͷŷ����˺���BUFF�� ������ܱ����������˺��� �������߷������� ���� ����·��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Magic.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
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
			
		self.receiveLinkBuff( caster, receiver )
		# ִ�����к����Ϊ
		caster.doAttackerOnHit( receiver, damageType )	#�����ߴ���
		receiver.doVictimOnHit( caster, damageType )   #�ܻ��ߴ���
		
class Spell_BuffMagicVolley( Spell_MagicVolley ):
	"""
	�ͷŷ����˺���BUFF�� ������ܱ����������˺��� �������߷������� ���� ����·��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_MagicVolley.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_MagicVolley.init( self, dict )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
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
			
		self.receiveLinkBuff( caster, receiver )
		# ִ�����к����Ϊ
		caster.doAttackerOnHit( receiver, damageType )	#�����ߴ���
		receiver.doVictimOnHit( caster, damageType )   #�ܻ��ߴ���
#
# $Log: not supported by cvs2svn $
# Revision 1.3  2008/07/04 03:50:57  kebiao
# ��Ч��״̬��ʵ���Ż�
#
# Revision 1.2  2008/07/03 02:49:39  kebiao
# �ı� ˯�� �����Ч����ʵ��
#
# Revision 1.1  2008/05/27 02:10:37  kebiao
# no message
#
#
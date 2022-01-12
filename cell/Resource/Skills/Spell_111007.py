# -*- coding: gb18030 -*-

import csdefine
from SpellBase import *

class Spell_111007( CombatSpell ):
	"""
	��ɵ�ǰĿ������ֵ���޵�һ�������������˺������ӷ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		CombatSpell.__init__( self )
		self._damageType = csdefine.DAMAGE_TYPE_PHYSICS		# �˺����
		self._percentage = 0								# �˺��ٷֱ�

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		CombatSpell.init( self, dict )
		self._percentage = int( dict["param1"] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		if receiver.isDestroyed:
			return

		finiDamage = int( receiver.HP_Max * self._percentage / 100 )
		#�������С��Ƶд�����ʵ�ʼ��� 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm

		self.persentDamage( caster, receiver, self._damageType, max( 1, int( finiDamage ) ) )
		self.receiveLinkBuff( caster, receiver )
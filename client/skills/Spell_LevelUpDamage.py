# -*- coding: gb18030 -*-

import BigWorld
import csstatus
from SpellBase import *

class Spell_LevelUpDamage( Spell ):
	"""
	����������Χ�˺�����ר�ýű�
	"""
	def __init__( self ):
		"""
		���캯��
		"""
		Spell.__init__( self )
		self._damage = 0	# �����˺�

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._damage = int( dict["param1"] ) if len( dict["param1"] ) > 0 else 0

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ��
		return type:int
		"""
		if caster.vehicleDBID:	# ���״̬���޷�����
			return csstatus.SKILL_NO_MSG

		return csstatus.SKILL_GO_ON
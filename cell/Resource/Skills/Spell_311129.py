# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��AreaRestrictTransducer��entity(���幦��entity)���ڽ�����λ��

import BigWorld
import csdefine
import csstatus
from SpellBase import *
from Spell_DirectDamage import Spell_DirectPhyDamage

class Spell_311129( Spell_DirectPhyDamage ):
	"""
	ͬ��ֱ���˺���������ʹĿ�귨������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_DirectPhyDamage.__init__( self )
		self.mpVal = 0				# ʹ��������ֵ

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_DirectPhyDamage.init( self, dict )
		self.mpVal = int( dict[ "param1" ] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		Spell_DirectPhyDamage.receive( self, caster, receiver )
		val = min(receiver.MP, self.mpVal)
		receiver.MP -= val

# -*- coding: gb18030 -*-
from SpellBase import *

class Spell_PickAnimaStop( Spell ):
	"""
	����ʰȡ�����淨
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		receiver.pickAnima_onEnd() #֪ͨ��ң��淨����
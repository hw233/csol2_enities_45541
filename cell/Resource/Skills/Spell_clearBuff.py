# -*- coding: utf-8 -*-
#
#

import csdefine
import csstatus
from SpellBase import Spell
import Const
import ECBExtend

class Spell_clearBuff( Spell ):
	"""
	���ĳbuff
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self._p1 = 0
		self._p2 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._p1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )	# buffID1
		self._p2 = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 )	# buffID2

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		if self._p1 > 0:
			receiver.removeAllBuffByBuffID( self._p1, [csdefine.BUFF_INTERRUPT_NONE] )

		if self._p2 > 0:
			receiver.removeAllBuffByBuffID( self._p2, [csdefine.BUFF_INTERRUPT_NONE] )

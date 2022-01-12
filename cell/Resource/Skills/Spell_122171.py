# -*- coding: gb18030 -*-
"""
����:Ѫ�� 
"""

from Spell_Magic import Spell_Magic
import csstatus

class Spell_122171(Spell_Magic):
	"""
	���ã��ָ�Ŀ����������i%������ֵ
	"""
	
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Magic.__init__( self )
		self._param = 0
	
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._param = float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0.0 )  / 100	
	
	def useableCheck( self, caster, receiver ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ��
		"""
		if receiver.getObject().HP == receiver.getObject().HP_Max:
			return csstatus.SKILL_NOT_NEED_USE
		return Spell_Magic.useableCheck( self, caster, receiver )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		value = receiver.HP_Max * self._param
		receiver.addHP( int( value ) )
# -*- coding: gb18030 -*-

from Spell_BuffNormal import Spell_ItemBuffNormal
import csstatus

class Spell_Item_To_SpecifiedTarget( Spell_ItemBuffNormal ):
	"""
	���ض�Ŀ��ʹ����Ʒ����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_ItemBuffNormal.__init__( self )
		self.classNames = []

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_ItemBuffNormal.init( self, dict )
		self.classNames = dict[ "param1" ].split( "|" ) if len( dict[ "param1" ] ) > 0 else [] 		# �������õ�Ŀ��ID

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		entity = target.getObject()
		if entity.className not in self.classNames:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET
		
		return Spell_ItemBuffNormal.useableCheck( self, caster, target )
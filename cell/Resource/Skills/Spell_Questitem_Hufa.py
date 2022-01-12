# -*- coding: gb18030 -*-


import BigWorld
import csdefine
import csstatus
from Spell_Item import Spell_Item

class Spell_Questitem_Hufa( Spell_Item ):
	"""
	����������Ʒʹ�ü���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.buffID = int( dict[ "param1" ] )


	def useableCheck( self, caster, target ):
		"""
		virtual method. 
		"""
		if len(target.getObject().findBuffsByBuffID( self.buffID )) == 0:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET

		return Spell_Item.useableCheck( self, caster, target)


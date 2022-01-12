# -*- coding: gb18030 -*-
import items
g_items = items.instance()

from SpellBase import *

class Spell_addRaceItem( Spell ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self._itemID = 0
		self._itemNum = 1

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._itemID = int( dict[ "param1" ] )
		self._itemNum = int( dict[ "param2" ] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
			
		item = g_items.createDynamicItem( self._itemID, self._itemNum )
		if item == None:
			return
			
		receiver.addRaceItem( item )
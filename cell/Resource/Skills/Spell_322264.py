# -*-coding:gb18030-*-

from bwdebug import *
from Spell_Item import Spell_Item


class Spell_322264( Spell_Item ):
	"""
	物品技能，获得称号
	"""
	def __init__( self ):
		Spell_Item.__init__( self )
		self.param1 = 0
		
	def init( self, data ):
		"""
		"""
		Spell_Item.init( self, data )
		self.param1 = int( data["param1"] )
		
	def receive( self, caster, receiver ):
		"""
		"""
		DEBUG_MSG( "--->>>self.param1", self.param1 )
		receiver.addTitle( self.param1 )
		
		
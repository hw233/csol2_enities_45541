# -*- coding:gb18030 -*-


from Spell_Item import Spell_Item

class Spell_Item_AICommand( Spell_Item ):
	"""
	ͨ�������������߷���aiָ��
	"""
	def __init__( self ):
		Spell_Item.__init__( self )
		self.commandString = ""
		
	def init( self, data ):
		Spell_Item.init( self, data )
		self.commandString = int( data["param1"] ) if len( data["param1"] ) > 0 else 0
		
	def receive( self, caster, receiver ):
		receiver.sendAICommand( receiver.id, self.commandString )	# ��������߲��ܹ�����aiָ�˵���˼��ܵ�����������������
# -*- coding:gb18030 -*-


from SpellBase import Spell

class Spell_AICommand( Spell ):
	"""
	ͨ�������������߷���aiָ��
	"""
	def __init__( self ):
		Spell.__init__( self )
		self.commandString = ""
		
	def init( self, data ):
		Spell.init( self, data )
		self.commandString = int( data["param1"] ) if len( data["param1"] ) > 0 else 0
		
	def receive( self, caster, receiver ):
		receiver.sendAICommand( receiver.id, self.commandString )	# ��������߲��ܹ�����aiָ�˵���˼��ܵ�����������������
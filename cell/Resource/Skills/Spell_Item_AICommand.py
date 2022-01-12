# -*- coding:gb18030 -*-


from Spell_Item import Spell_Item

class Spell_Item_AICommand( Spell_Item ):
	"""
	通过技能向受术者发送ai指令
	"""
	def __init__( self ):
		Spell_Item.__init__( self )
		self.commandString = ""
		
	def init( self, data ):
		Spell_Item.init( self, data )
		self.commandString = int( data["param1"] ) if len( data["param1"] ) > 0 else 0
		
	def receive( self, caster, receiver ):
		receiver.sendAICommand( receiver.id, self.commandString )	# 如果受术者不能够接受ai指令，说明此技能的受术对象配置有误
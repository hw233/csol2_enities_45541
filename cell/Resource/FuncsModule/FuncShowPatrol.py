# -*- coding: gb18030 -*-

#显示摆点路径

# common
import csdefine
# cell
from Function import Function


class FuncShowPatrol( Function ):
	"""
	客户端显示摆点寻路路径
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.path = section.readString( 'param1' )
		self.model = section.readString( 'param2' )

	def do( self, player, talkEntity = None ) :
		"""
		"""
		player.client.onShowPatrol( self.path,self.model )

	def valid( self, player, talkEntity = None ) :
		"""
		"""
		return True

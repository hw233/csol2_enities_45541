# -*- coding: gb18030 -*-

#��ʾ�ڵ�·��

# common
import csdefine
# cell
from Function import Function


class FuncShowPatrol( Function ):
	"""
	�ͻ�����ʾ�ڵ�Ѱ··��
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

# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function


class FuncClose( Function ):
	"""
	�رնԻ�
	"""
	def __init__( self, section ):
		"""
		"""
		pass

	def do( self, player, talkEntity = None ):
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		return True


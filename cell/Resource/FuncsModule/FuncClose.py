# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function


class FuncClose( Function ):
	"""
	关闭对话
	"""
	def __init__( self, section ):
		"""
		"""
		pass

	def do( self, player, talkEntity = None ):
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		return True


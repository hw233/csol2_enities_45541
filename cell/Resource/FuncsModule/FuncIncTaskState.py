# -*- coding: gb18030 -*-

# �Ի�����ĳ���������һ�������������Ƿ�����һ����������������þ�����
# by ganjinxing 2011-11-23

from Function import Function


class FuncIncTaskState( Function ) :
	"""
	"""
	def __init__( self, section ) :
		Function.__init__( self, section )
		self.questId = section.readInt( "param1" )				# ����ID
		self.taskIndex = section.readInt( "param2" )			# ����Ŀ������

	def valid( self, player, talkEntity = None ) :
		"""
		"""
		return not player.taskIsCompleted( self.questId, self.taskIndex )

	def do( self, player, talkEntity = None ) :
		"""
		"""
		player.endGossip( talkEntity )
		player.questTaskIncreaseState( self.questId, self.taskIndex )

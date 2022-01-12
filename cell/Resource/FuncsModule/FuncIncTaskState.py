# -*- coding: gb18030 -*-

# 对话触发某个任务完成一步（至于任务是否因这一步而完成由任务配置决定）
# by ganjinxing 2011-11-23

from Function import Function


class FuncIncTaskState( Function ) :
	"""
	"""
	def __init__( self, section ) :
		Function.__init__( self, section )
		self.questId = section.readInt( "param1" )				# 任务ID
		self.taskIndex = section.readInt( "param2" )			# 任务目标索引

	def valid( self, player, talkEntity = None ) :
		"""
		"""
		return not player.taskIsCompleted( self.questId, self.taskIndex )

	def do( self, player, talkEntity = None ) :
		"""
		"""
		player.endGossip( talkEntity )
		player.questTaskIncreaseState( self.questId, self.taskIndex )

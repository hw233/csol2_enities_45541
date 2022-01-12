# -*- coding: gb18030 -*-

# 对话放弃某个任务
# by ganjinxing 2011-11-21

# common
import csdefine
# cell
from Function import Function


class FuncAbandonQuest( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.questID = section.readInt( 'param1' )

	def do( self, player, talkEntity = None ) :
		"""
		"""
		player.endGossip( talkEntity )
		player.getQuest( self.questID ).abandoned( player, csdefine.QUEST_REMOVE_FLAG_NPC_CHOOSE )
		player.questRemove( self.questID, True )
		player.onQuestBoxStateUpdate()

	def valid( self, player, talkEntity = None ) :
		"""
		"""
		return player.has_quest( self.questID )

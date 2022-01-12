# -*- coding: gb18030 -*-
#
# 只能通过NPC放弃的任务
# by ganjinxing 2011-11-22

# common
import csdefine
# cell
from Quest import Quest


class QuestAbandonAtNPC( Quest ) :
	"""
	"""
	def __init__( self ):
		Quest.__init__( self )
		
	def init( self, section ):
		"""
		"""
		Quest.init( self, section )
		self._style = csdefine.QUEST_STYLE_ABANDOND_ATNPC			# 只能通过NPC放弃的任务类型
		
	def abandoned( self, player, flags ) :
		"""
		放弃任务
		"""
		if flags != csdefine.QUEST_REMOVE_FLAG_NPC_CHOOSE :
			return False
		return Quest.abandoned( self, player, flags )
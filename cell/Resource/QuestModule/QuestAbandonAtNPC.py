# -*- coding: gb18030 -*-
#
# ֻ��ͨ��NPC����������
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
		self._style = csdefine.QUEST_STYLE_ABANDOND_ATNPC			# ֻ��ͨ��NPC��������������
		
	def abandoned( self, player, flags ) :
		"""
		��������
		"""
		if flags != csdefine.QUEST_REMOVE_FLAG_NPC_CHOOSE :
			return False
		return Quest.abandoned( self, player, flags )
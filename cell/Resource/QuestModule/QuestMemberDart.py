# -*- coding: gb18030 -*-
#
# $Id $

"""
成员运镖任务模块 spf
"""


from QuestDart import *

class QuestMemberDart( QuestDart ):
	def __init__( self ):
		QuestDart.__init__( self )
		self._type = csdefine.QUEST_TYPE_MEMBER_DART
		
	def init( self, section ):
		QuestDart.init( self, section )
		self._type = csdefine.QUEST_TYPE_MEMBER_DART

	def hasOption( self ):
		"""
		"""
		return False


	def accept( self, player ):
		"""
		virtual method.
		接任务，如果接任务失败了则返回False（例如玩家背包满了放不下任务道具）。

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QuestDart.accept( self, player )
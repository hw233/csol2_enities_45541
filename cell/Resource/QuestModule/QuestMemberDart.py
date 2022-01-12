# -*- coding: gb18030 -*-
#
# $Id $

"""
��Ա��������ģ�� spf
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
		���������������ʧ�����򷵻�False��������ұ������˷Ų���������ߣ���

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return QuestDart.accept( self, player )
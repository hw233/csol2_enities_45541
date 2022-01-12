# -*- coding: gb18030 -*-
#


from Function import Function
import BigWorld
import csdefine
import csstatus
from bwdebug import *

class FuncHasQuest( Function ):
	"""
	����������ɣ��������������ԡ�
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )	# ����ID

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		quest = player.getQuest( self._param1 )
		if quest is None:
			ERROR_MSG( "cell/FuncHasQuest.py: There is no quest which ID is %i" % self._param1 )
			return False
		return quest.query( player ) in [ csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_COMPLETE ]



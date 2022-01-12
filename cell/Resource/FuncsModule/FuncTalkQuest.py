# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from Function import Function
import csdefine
import BigWorld
import csstatus

class FuncTalkQuest( Function ):
	"""
	�Ի�����ѡ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )			#����ID
		self._param2 = section.readInt( "param2" )			#����Ŀ������

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
		player.questTalk( talkEntity.className )

		

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
			return False
		
		if quest.query( player ) != csdefine.QUEST_STATE_NOT_FINISH:
			return False
		
		if player.getQuestTasks( self._param1 ).getTasks()[self._param2].isCompleted( player ):
			return False
		return True



class FuncTalkRandomQuest( Function ):
	"""
	��Ի�����ѡ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )			#������ID
		self._param2 = section.readInt( "param2" )			#������ID
		self._param3 = section.readInt( "param3" )			#����Ŀ������

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
		player.questTalk( talkEntity.className )

		

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
			return False
		
		if quest.query( player ) != csdefine.QUEST_STATE_NOT_FINISH:
			return False
		
		tasks = player.getQuestTasks( self._param1 )
		subQuestID = tasks.query( "subQuestID" )
		
		if self._param2 != subQuestID:
			return
		
		if tasks.getTasks()[self._param3].isCompleted( player ):
			return False
		return True



class FuncTalkRandomQuestWithAction( FuncTalkRandomQuest ):
	"""
	�ж����ĶԻ�����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )			#������ID
		self._param2 = section.readInt( "param2" )			#������ID
		self._param3 = section.readInt( "param3" )			#����Ŀ������
		self._param4 = section.readString( "param4" )			#��ɫ����
		self._param5 = section.readString( "param5" )			#NPC����


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
		player.questTalk( talkEntity.className )
		player.planesAllClients( "onPlayAction", ( self._param4, ) )
		talkEntity.planesAllClients( "onPlayAction", ( self._param5, ) )

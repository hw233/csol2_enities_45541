# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import random

class FuncChangePosition( Function ):
	"""
	�ı�NPC λ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.positionList = []
		ps = section.readString( "param1" ).split( ":" )
		for i in ps:

			self.positionList.append( eval( i ) )
		
		self.questID   = section.readInt( "param2" )
		self.taskIndex = section.readInt( "param3" )
		self.skillID    = section.readInt( "param4" )
		self.count	   = section.readInt( "param5" )


	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )

		tempPos = []
		for i in self.positionList:
			if ( int(i[0]), int(i[2]) ) != ( int(talkEntity.position[0]), int(talkEntity.position[2]) ):
				tempPos.append( i )
		
		
		talkEntity.setPosition( random.choice( tempPos ) )
		player.spellTarget( self.skillID, player.id )
		player.questTaskIncreaseState( self.questID, self.taskIndex )


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
		quest = player.getQuest( self.questID )
		
		if quest is None:
			return False
		
		if quest.query( player ) != csdefine.QUEST_STATE_NOT_FINISH:
			return False
		
		if player.getQuestTasks( self.questID ).getTasks()[self.taskIndex].val1 != self.count:
			return False
		
		return True
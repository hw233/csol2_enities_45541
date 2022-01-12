# -*- coding: gb18030 -*-

from Function import Function
from bwdebug import *
import csdefine
import csstatus

class FuncTalkToQuestNPCMonster( Function ):
	"""
	�������NPC�ĶԻ�������δ��ɶԻ�
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		questStrs = section.readString( "param1" )	# ��NPCӵ�е�����ID
		self._questIDs = questStrs.split( '|' )
		dialogStrs = section.readString( "param2" )	# ��ҿ����ĶԻ�
		self._dialogs = dialogStrs.split( '|' )

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
		talkDatas = {}
		valid = False
		if len( self._questIDs ) != len( self._dialogs ): return valid
		for index in range( len( self._questIDs ) ):
			talkDatas[ self._questIDs[index] ] = self._dialogs[index]
		# ������ʾ�͵ȼ�����Ի�����
		questID = 0
		questLevel = 150
		for qID in self._questIDs:
			if player.questsTable._quests.has_key( int( qID ) ):
				quest = player.getQuest( int( qID ) )
				if quest.query( player ) == csdefine.QUEST_STATE_NOT_FINISH:
					if quest.getLevel() <= questLevel:
						questLevel = quest.getLevel()
						questID = qID
						valid = True
		if valid:
			player.setGossipText( talkDatas[questID] )
		return valid
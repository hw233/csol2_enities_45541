# -*- coding: gb18030 -*-
#
# 2009-02-11 SongPeifang
#
"""
�������NPC�ĶԻ�
"""
from Function import Function
from bwdebug import *
import csdefine
import csstatus

class FuncQuestNPCMonster( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		questStrs = section.readString( "param1" )	# ��NPCӵ�е�����ID
		self._questIDs = questStrs.split( '|' )
		self._invalidDialog = section.readString( "param2" )	# ��������������ҿ����ĶԻ�

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
		if player.getState() == csdefine.ENTITY_STATE_PENDING:
			player.statusMessage( csstatus.NPC_TRADE_FORBID_TALK )
			return
		if talkEntity != None:
			talkEntity.changeToMonster( talkEntity.level, player.id )
			talkEntity.setTemp( "ownerID", player.id )	#add by wuxo 2011-9-23
			# ������ֱ�����ù����bootyOwner
			getEnemyTeam = getattr( player, "getTeamMailbox", None )	# ����ж������¼����mailbox
			if getEnemyTeam and getEnemyTeam():
				talkEntity.bootyOwner = ( player.id, getEnemyTeam().id )
			else:
				talkEntity.bootyOwner = ( player.id, 0 )
			talkEntity.firstBruise = 1		# ��������һ�����˺���bootyOwner����

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
		valid = False
		for qID in self._questIDs:
			if player.questsTable._quests.has_key( int( qID ) ):
				if player.getQuest( int( qID ) ).query( player ) == csdefine.QUEST_STATE_NOT_FINISH:
					valid = True
				else:
					valid = False
				break
		if not valid:
			player.setGossipText( self._invalidDialog )
		return valid
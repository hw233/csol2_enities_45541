# -*- coding: gb18030 -*-
#created by dqh
# $Id: Exp $


from Function import Function
import BigWorld
import csdefine
import csstatus
from bwdebug import *

class FuncCompleteQuestBySign( Function ):
	"""
	��������Ƿ���ĳһ��ָ���ı�ǣ������������Ƿ���ɡ����������������
	"""
	def __init__( self, section ):
		"""
		@param param : ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param : pyDataSection
		"""
		Function.__init__( self, section )
		
		self._tempSign = section.readString( "param1")		# �������
		self._questID = section.readInt( "param2" )			# ����ID
		self._taskIndex = section.readInt( "param3" )		# ����Ŀ������

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player     : ���
		@type  player     : Entity
		@param talkEntity : һ����չ�Ĳ���
		@type  talkEntity : entity
		@return           : None
		"""
		player.endGossip( talkEntity )
		player.questTaskIncreaseState( self._questID, self._taskIndex )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		
		@param player		: ���
		@type  player		: Entity
		@param talkEntity	: һ����չ�Ĳ���
		@type  talkEntity	: entity
		@return				: True/False
		@rtype				: bool
		"""
		quest = player.getQuest( self._questID )
		if quest and quest.query( player ) == csdefine.QUEST_STATE_NOT_FINISH and player.queryTemp( self._tempSign, 0):	#���������û����ɡ��������ָ�����
			return True
		return False


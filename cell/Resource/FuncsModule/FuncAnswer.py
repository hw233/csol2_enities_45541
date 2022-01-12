# -*- coding: gb18030 -*-
#
# $Id: Exp $


import time
import random
from Function import Function
import csstatus
import csdefine
import ECBExtend
from bwdebug import *

class FuncAnswer( Function ):
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )	# ����ID
		self._param2 = section.readInt( "param2" )	# ��Ŀ����


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
			
		player.setTemp( "talkID", "START ANSWER" )
		player.setTemp( "talkNPCID", talkEntity.id )
		player.addTimer( 0.5, 0, ECBExtend.AUTO_TALK_CBID )
		player.set("question_type", self._param2 )


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
			ERROR_MSG( "cell/FuncAnswer.py: There is no quest which ID is %i" % self._param1 )
			return False
		return quest.query( player ) == csdefine.QUEST_STATE_NOT_FINISH
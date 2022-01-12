# -*- coding: gb18030 -*-
#
# $Id: FuncConstCityWar.py,v 1.1 2008-08-20 00:52:43 kebiao Exp $

"""
"""
from Function import Function
from bwdebug import *
import csdefine
import csstatus
import csconst
import BigWorld
import time

class FuncRequestRobWar( Function ):
	"""
	�������Ӷ�ս
	"""
	def __init__( self, section ):
		"""
		param1: amount

		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if not BigWorld.globalData.has_key( "TONG_ROB_WAR_SIGNUP_START" ):
			player.statusMessage( csstatus.TONG_REQUEST_ROBWAR_DATE_INVALID )
			player.endGossip( talkEntity )
			return
			
		if not player.isTongChief():
			player.statusMessage( csstatus.TONG_REQUEST_ROBWAR_GRADE_INVALID )
			player.endGossip( talkEntity )
			return
		tongMailbox = player.tong_getTongEntity( player.tong_dbID )
		if tongMailbox:
			tongMailbox.onRequestRobWar( player.databaseID )
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
		return True


#
# $Log: not supported by cvs2svn $
#

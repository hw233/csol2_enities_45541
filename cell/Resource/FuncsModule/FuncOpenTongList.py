# -*- coding: gb18030 -*-
#
#$Id:$

import BigWorld
from bwdebug import *

class FuncOpenTongList:
	"""
	�򿪰���б����
	"""
	def __init__( self, section ):
		"""
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
		if talkEntity is None:
			WARNING_MSG( "talkEntity cannot be None." )
			return
		player.client.tong_openTongQueryWindow()
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




#$Log:$
#
# 
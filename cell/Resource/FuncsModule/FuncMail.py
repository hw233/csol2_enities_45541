# -*- coding: gb18030 -*-
#
# $Id: FuncMail.py,v 1.1 2008-03-06 09:13:08 fangpengjun Exp $

"""
ʵ�����ʼ�NPC�Ի�����
"""
from Function import Function
from bwdebug import *

class FuncMail( Function ):
	"""
	"""
	def __init__( self, section ):

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
		player.client.enterMailWithNPC( talkEntity.id )
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
# -*- coding: gb18030 -*-
#
from bwdebug import *
import csdefine
import csconst
import csstatus

class FuncBuyTongSpecial:
	"""
	������������Ʒ
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
			return
		if player.tong_dbID != talkEntity.ownTongDBID:
			return
		player.client.onTradeWithTongSpecialChapman( talkEntity.id )
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
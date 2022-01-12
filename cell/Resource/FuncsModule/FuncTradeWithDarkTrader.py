# -*- coding: gb18030 -*-
#
# 2008-12-10 SongPeifang
#
"""
��Ͷ�����˴�������Ʒ�ĶԻ�
"""
from Function import Function
import csstatus

class FuncTradeWithDarkTrader( Function ):
	"""
	���� -- ��Ͷ�����˴�������Ʒ
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
		if player.iskitbagsLocked():	# ����������by����
			player.endGossip( talkEntity )
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		player.client.enterTradeWithDarkTrader( talkEntity.id )
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
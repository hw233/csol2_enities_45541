# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from Function import Function
import csdefine
import BigWorld
import csstatus

class FuncMerchantCharge( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )

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
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		if not player.isInMerchantQuest():
			player.statusMessage( csstatus.ROLE_QUEST_IS_NOT_IN_MERCHANT )
			return
		if player.money < self._param1:
			player.statusMessage( csstatus.ROLE_QUEST_NOT_ENOUGH_MONEY_FOR_CHAGRE_YINPIAO)
			return
		player.moneyToYinpiao( self._param1 )


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


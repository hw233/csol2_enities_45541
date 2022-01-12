# -*- coding: gb18030 -*-

import csstatus
from Function import Function

class FuncKitbagForceUnlock( Function ) :

	def valid( self, player, targetEntity ) :
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��

		@param player: ���entity
		@param talkEntity: npc entity
		"""
		return True

	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������

		@param player: ���entity
		@param talkEntity: npc entity
		"""
		player.endGossip( talkEntity )
		if player.kitbagsForceUnlockLimitTime > 0 :			# ��ǿ�ƽ�����������ڣ������ظ���Ӧ����
			player.statusMessage( csstatus.CIB_MSG_KITBAG_FORCE_UNLOCK_REPEAT )
			return
		if not player.kitbagsLockerStatus & 0x02 :			# ����δ���ϣ�����������ǿ�ƽ���
			player.statusMessage( csstatus.CIB_MSG_KITBAG_FORCE_UNLOCK_FORBID )
			return
		player.client.kitbags_onConfirmForceUnlock()
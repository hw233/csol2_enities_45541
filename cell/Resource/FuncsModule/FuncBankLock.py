# -*- coding: gb18030 -*-

import csstatus
from Function import Function

class FuncBankForceUnlock( Function ) :

	def valid( self, player, targetEntity ) :
		"""
		Virtual method.
		对话选项有效性检查

		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		return True

	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		触发对话选项要做的事情

		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		player.endGossip( talkEntity )
		if player.bankForceUnlockLimitTime > 0 :		# 在强制解除锁定期限内，不再重复响应请求
			player.statusMessage( csstatus.BANK_FORCE_UNLOCK_REPEAT )
			return
		if not player.bankLockerStatus & 0x02 :			# 背包未锁上，不允许申请强制解锁
			player.statusMessage( csstatus.BANK_FORCE_UNLOCK_FORBID )
			return
		player.client.bank_onConfirmForceUnlock()
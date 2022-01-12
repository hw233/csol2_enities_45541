# -*- coding: gb18030 -*-
#



import csstatus
import cschannel_msgs
import ShareTexts as ST
import csdefine
import sys

class RoleGem:
	"""
	玩家经验石
	"""
	def __init__( self ):
		"""
		"""
		pass

	def gem_charge( self, gold ):
		"""
		Exposed method.
		玩家给代练宝石充值

		@param gold : 冲值的元宝值
		@type gold : UINT32
		"""
		if self.getUsableGold() < gold:
			self.statusMessage( csstatus.PET_TRAIN_CHARGE_FAIL_LACK_GOLD )
			return

		self.freezeGold( gold )
		self.cell.gem_charge( gold )

	def gem_chargeCB( self, gold, state ):
		"""
		Define method.
		玩家给代练石冲值回调

		@param gold : 充值的元宝值
		@type gold : UINT32
		@param state : 充值的的结果，是否成功
		@type state : BOOL
		"""
		self.thawGold( gold )
		if state:
			self.payGold( gold, csdefine.CHANGE_GOLD_GEM_CHARGE )
# -*- coding:gb18030 -*-

import csdefine
from bwdebug import *

class Fisher:
	def __init__( self ):
		pass

	def fish_gainMoney( self, earnings ):
		"""
		Define methods.
		玩家获得捕鱼金钱
		"""
		self.gainMoney( earnings, csdefine.CHANGE_MONEY_FISHING_JOY )

	def fish_buyBulletRequest( self, srcEntityID, cost ):
		"""
		Exposed method.
		玩家购买子弹
		"""
		if srcEntityID != self.id:
			ERROR_MSG( "player( %s ) srcEntityID( %i ) != self.id( %i )" % ( self.getName(), srcEntityID, self.id ) )
			return

		if not self.payMoney( cost, csdefine.CHANGE_MONEY_FISHING_JOY ):
			DEBUG_MSG( "player( %s ) dont have enough money( %i )." % ( self.getName(), cost ) )
			return
		self.base.fish_buyBullet( csdefine.CURRENCY_TYPE_MONEY, cost )

	def fish_retrunMoneyOnLeaving( self, amount ):
		"""
		Define method.
		玩家离开捕鱼场返还剩余金钱。
		需要cell返还成功的回调，避免cell已经销毁造成玩家金钱损失。
		"""
		self.gainMoney( amount, csdefine.CHANGE_MONEY_FISHING_JOY )
		self.base.fish_returnMoneySuccess()

	def fish_leaveFishing(self, srcEntityID):
		"""
		Exposed method.
		玩家退出捕鱼
		"""
		if srcEntityID != self.id:
			ERROR_MSG( "player( %s ) srcEntityID( %i ) != self.id( %i )" % ( self.getName(), srcEntityID, self.id ) )
			return

		if self.spaceType == "fishing_joy":
			self.gotoForetime()

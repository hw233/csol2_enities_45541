# -*- coding: gb18030 -*-
#

"""
元宝交易系统模块
"""
import BigWorld
from bwdebug import *
import csdefine
import csstatus
import Const

class YuanBaoTradeInterface:
	"""
	"""
	def __init__( self ):
		"""
		初始化状态。要在Fight初始化之前
		"""
		pass
		
	def ybt_switch( self, trigger ):
		"""
		通知base开闭元宝交易功能
		"""
		self.base.ybt_switch( trigger )
	# -----------------------------------------------------------------------------------------------------
	# 购买元宝
	def buyYB( self, selfEntityID, tick, uid, yuanbao, rate ):
		"""
		Exposed method
		购买元宝
		"""
		if self.iskitbagsLocked():	# 背包上锁
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		cost = yuanbao * rate * 1.1
		if self.money < cost:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.base.buyYB( tick, uid, yuanbao, rate )
		
	def onBuyYB( self, cost ):
		"""
		define method
		购买元宝回调
		"""
		if not self.payMoney( cost, csdefine.CHANGE_MONEY_BUY_YUANBAO ):
			ERROR_MSG( "Buy yuan bao pay money faild." )

	# -----------------------------------------------------------------------------------------------------
	# 出售元宝
	def sellYB( self, selfEntityID, tick, uid, yuanbao, rate ):
		"""
		Exposed method
		出售元宝
		"""
		if self.iskitbagsLocked():	# 背包上锁
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		self.base.sellYB( tick, uid, yuanbao, rate )
		
	def onSellYB( self, money ):
		"""
		define method
		出售元宝回调
		"""
		self.addMoney( money, csdefine.CHANGE_MONEY_BUY_YUANBAO )
		
	# -----------------------------------------------------------------------------------------------------
	# 求购订单
	def establishBuyBillRequest( self, selfEntityID, yuanbao, rate ):
		"""
		Exposed method
		请求建立求购订单
		"""
		if self.iskitbagsLocked():	# 背包上锁
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		cost = yuanbao * ( rate + int( rate*0.1 ) )
		if self.money < cost:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.base.establishBuyBillRequest()
		
	def establishBuyBill( self, selfEntityID, yuanbao, rate ):
		"""
		Exposed method
		建立求购订单
		"""
		if self.iskitbagsLocked():	# 背包上锁
			return
		cost = yuanbao* ( rate + int( rate*0.1 ) )
		if self.money < cost:
			return
		self.base.establishBuyBill( yuanbao, rate )
		
	def onEstablishBuyBill( self, cost ):
		"""
		defined method
		建立求购订单回调
		"""
		if not self.payMoney( cost, csdefine.CHANGE_MONEY_BUY_YUANBAO ):
			ERROR_MSG( "new buy bill pay money faild." )
			
	# -----------------------------------------------------------------------------------------------------
	# 寄售订单
	def establishSellBillRequest( self, selfEntityID, yuanbao ):
		"""
		Exposed method
		请求建立求寄售单
		"""
		if self.iskitbagsLocked():	# 背包上锁
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		self.base.establishSellBillRequest( yuanbao )
		
	def establishSellBill( self, selfEntityID, yuanbao, rate ):
		"""
		Exposed method
		建立寄售订单
		"""
		if self.iskitbagsLocked():	# 背包上锁
			return
		self.base.establishSellBill( yuanbao, rate )
		
	def onEstablishSellBill( self, cost ):
		"""
		defined method
		建立寄售订单回调
		"""
		if not self.payMoney( cost, csdefine.CHANGE_MONEY_BUY_YUANBAO ):
			ERROR_MSG( "new sell bill pay money faild." )
		
	# -----------------------------------------------------------------------------------------------------
	# 撤销订单
	def cancleBillRequest( self, selfEntityID, tick, uid, bType ):
		"""
		Exposed method
		请求撤销订单
		"""
		if self.iskitbagsLocked():	# 背包上锁
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		if self.money < 100000:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.base.cancleBillRequest( tick, uid, bType )
		
	def cancleBill( self, selfEntityID, tick, uid, bType ):
		"""
		Exposed method
		撤销订单
		"""
		if self.iskitbagsLocked() or self.money < 100000:
			return
		self.base.cancleBill( tick, uid, bType )
		
	def onCancleBill( self, tick, uid, desposit ):
		"""
		define method
		撤销订单回调
		"""
		self.addMoney( desposit, csdefine.CHANGE_MONEY_CANCLE_YBT_BILL )
		#if self.payMoney( 100000, csdefine.CHANGE_MONEY_CANCLE_YBT_BILL ):
		#	self.statusMessage( csstatus.YB_TRADE_NEW_BILL_EXTRA, 100000 )
		if tick == 0 or uid == 0:
			return
		self.client.onCancleBill( tick, uid )
		
	# -----------------------------------------------------------------------------------------------------
	# 取出元宝
	def drawYBRequest( self, selfEntityID ):
		"""
		Exposed method
		请求取出元宝
		"""
		if self.iskitbagsLocked():	# 背包上锁
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		self.client.onDrawYBRequest()
		
	def drawYB( self, selfEntityID ):
		"""
		Exposed method
		取出元宝
		"""
		if self.iskitbagsLocked():	# 背包上锁
			return
		self.base.drawYB()
		
	# -----------------------------------------------------------------------------------------------------
	# 取出金钱
	def drawMoneyRequest( self, selfEntityID ):
		"""
		Exposed method
		请求取出金钱
		"""
		if self.iskitbagsLocked():	# 背包上锁
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		self.client.onDrawMoneyRequest()
		
	def drawMoney( self, selfEntityID ):
		"""
		Exposed method
		取出金钱
		"""
		if self.iskitbagsLocked():	# 背包上锁
			return
		self.base.drawMoney()
		
	def onDrawMoney( self, money ):
		"""
		define method
		取出金钱回调
		"""
		self.addMoney( money, csdefine.CHANGE_MONEY_DRAW_MONEY )
		gold = money/10000
		silver = ( money%100 )/100
		coin = ( money%100 )%100
		self.statusMessage( csstatus.YB_TRADE_NEW_DRAW_MONEY, gold, silver, coin )
		self.client.onDrawMoney()
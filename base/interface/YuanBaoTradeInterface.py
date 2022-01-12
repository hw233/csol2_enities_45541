# -*- coding: gb18030 -*-
#

"""
元宝交易系统模块
"""
import BigWorld
from bwdebug import *
import csdefine
import csstatus
import cschannel_msgs
import Const
from AbstractTemplates import MultiLngFuncDecorator
import Love3


class languageDepart( MultiLngFuncDecorator ):
	"""
	多语言版本的内容区分 by 姜毅
	"""
	@staticmethod
	def locale_default( ybtInterface ):
		"""
		简体版
		"""
		languageDepart.originalFunc( ybtInterface )
		ybtInterface.ybtMgr = BigWorld.globalData["YuanBaoTradeMgr"]


class YuanBaoTradeInterface:
	"""
	"""
	@languageDepart
	def __init__( self ):
		"""
		初始化状态。要在Fight初始化之前
		"""
		self.ybtMgr = None
		
		# 临时记录该角色所占有交易权的订单数据
		self.tempBillTick = 0
		self.tempBillUid = 0
		self.tempBillType = 0
		
	def billLockRecord( self, tick, uid, bType ):
		"""
		define method
		临时记录该角色所占有交易权的订单数据，以便下线时自动解锁
		"""
		self.tempBillTick = tick
		self.tempBillUid = uid
		self.tempBillType = bType
		
	def billUnLockRecord( self ):
		"""
		define method
		清空临时记录的角色所占有交易权的订单数据
		"""
		self.tempBillTick = 0
		self.tempBillUid = 0
		self.tempBillType = 0
		
	def ybt_switch( self, trigger ):
		"""
		define method
		开闭元宝交易功能
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.ybt_switch( trigger )
		if trigger == 0:
			self.statusMessage( csstatus.YB_TRADE_BANNED )
		else:
			self.statusMessage( csstatus.YB_TRADE_UNBANNED )
		
	def ybt_onLeave( self ):
		"""
		玩家下线时，元宝交易系统的一些处理，例如解锁由该角色锁定的订单
		"""
		if self.ybtMgr is None:
			return
		if self.tempBillType == 0:
			return
		if self.tempBillType == csdefine.YB_BILL_TYPE_BUY:
			self.ybtMgr.unBuyYB( self.tempBillTick, self.tempBillUid, self.databaseID, self )
		elif self.tempBillType == csdefine.YB_BILL_TYPE_SELL:
			self.ybtMgr.unSellYB( self.tempBillTick, self.tempBillUid, self.databaseID, self )
		
	# -----------------------------------------------------------------------------------------------------
	# 购买元宝
	def buyYBRequest( self, tick, uid ):
		"""
		Exposed method
		请求购买元宝
		"""
		if self.ybtMgr is None:
			return
		if self.tempBillType != 0:
			ERROR_MSG( "buy request error, you are trading now." )
			return
		self.ybtMgr.buyYBRequest( tick ,uid, self.databaseID, self )
		
	def unBuyYB( self, tick, uid ):
		"""
		Exposed method
		取消购买元宝
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.unBuyYB( tick, uid, self.id, self )
		
	def buyYB( self, tick, uid, yuanbao, rate ):
		"""
		define method
		购买元宝
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.buyYB( tick, uid, yuanbao, rate, self )
		
	def onBuyYB( self, yuanbao ):
		"""
		define method
		购买元宝回调
		"""
		self.addGold( yuanbao, csdefine.CHANGE_GOLD_YBT_SELL )
		
	# -----------------------------------------------------------------------------------------------------
	# 出售元宝
	def sellYBRequest( self, tick, uid ):
		"""
		Exposed method
		请求出售元宝
		"""
		if self.ybtMgr is None:
			return
		if self.tempBillType != 0:
			ERROR_MSG( "sell request error, you are trading now." )
			return
		self.ybtMgr.sellYBRequest( tick ,uid, self.databaseID, self )
		
	def unSellYB( self, tick, uid ):
		"""
		Exposed method
		取消出售元宝
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.unSellYB( tick, uid, self.id, self )
		
	def sellYB( self, tick, uid, yuanbao, rate ):
		"""
		define method
		出售元宝
		"""
		if self.gold < yuanbao*100:
			self.statusMessage( csstatus.SPECIALSHOP_GOLD_NOT_ENOUGH )
			return
		self.ybtMgr.sellYB( tick, uid, yuanbao, rate, self )
		
	def onSellYB( self, cost ):
		"""
		define method
		出售元宝回调
		"""
		if self.ybtMgr is None:
			return
		if not self.payGold( cost, csdefine.CHANGE_GOLD_YBT_SELL ):
			ERROR_MSG( "sell yuan bao pay gold failed." )
			
	# -----------------------------------------------------------------------------------------------------
	# 求购订单
	def establishBuyBillRequest( self ):
		"""
		define method
		请求建立求购订单
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.establishBuyBillRequest( self.databaseID, self.getName(), self )
		
	def establishBuyBill( self, yuanbao, rate ):
		"""
		define method
		建立求购订单
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.establishBuyBill( yuanbao, rate, self.databaseID, self )
		
	def onEstablishBuyBill( self, rate ):
		"""
		define method
		建立求购订单后
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_EXTABLISH_YB_BUY_BILL%( self.getName(), rate ), [] )
	# -----------------------------------------------------------------------------------------------------
	# 寄售订单
	def establishSellBillRequest( self, yuanbao ):
		"""
		define method
		请求建立寄售订单
		"""
		if self.ybtMgr is None:
			return
		if self.gold < yuanbao:
			self.statusMessage( csstatus.SPECIALSHOP_GOLD_NOT_ENOUGH )
			return
		self.ybtMgr.establishSellBillRequest( self.databaseID, self.getName(), self )
		
	def establishSellBill( self, yuanbao, rate ):
		"""
		define method
		建立寄售订单
		"""
		if self.ybtMgr is None:
			return
		if self.gold < yuanbao:
			return
		self.ybtMgr.establishSellBill( yuanbao, rate, self.databaseID, self )
		
	def onEstablishSellBill( self, cost, rate ):
		"""
		define method
		建立寄售订单回调
		"""
		if self.ybtMgr is None:
			return
		if not self.payGold( cost, csdefine.CHANGE_GOLD_YBT_SELL_BILL ):
			ERROR_MSG( "new sell bill pay gold failed." )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_EXTABLISH_YB_SELL_BILL%( self.getName(), rate ), [] )
			
	# -----------------------------------------------------------------------------------------------------
	# 撤销订单
	def cancleBillRequest( self, tick, uid, bType ):
		"""
		define method
		请求撤销订单
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.cancleBillRequest( tick, uid, bType, self )
		
	def cancleBill( self, tick, uid, bType ):
		"""
		define method
		撤销订单
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.cancleBill( tick, uid, bType, self )
		
	def onCancleBill( self, tick, uid, desposit ):
		"""
		define method
		撤销订单回调
		"""
		if self.ybtMgr is None:
			return
		self.addGold( desposit, csdefine.CHANGE_GOLD_YBT_CANCLE_BILL )
		self.cell.onCancleBill( 0, 0, 0 )
		self.client.onCancleBill( tick, uid )
		
	# -----------------------------------------------------------------------------------------------------
	# 取出元宝
	def drawYB( self ):
		"""
		define method
		取出元宝
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.drawYB( self.databaseID, self )
		
	def onDrawYB( self, yuanbao ):
		"""
		define method
		取出元宝回调
		"""
		self.addGold( yuanbao, csdefine.CHANGE_GOLD_YBT_DRAW_YB )
		self.statusMessage( csstatus.YB_TRADE_NEW_DRAW_YB, yuanbao )
		self.client.onDrawYB()
		
	# -----------------------------------------------------------------------------------------------------
	# 取出金钱
	def drawMoney( self ):
		"""
		define method
		取出金钱
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.drawMoney( self.databaseID, self )
		
	# -----------------------------------------------------------------------------------------------------
	# 请求信息
	def getBuyBillsInfo( self, page, number ):
		"""
		Exposeds
		向服务器请求获取购买元宝订单信息
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.getBuyBillsInfo( page, number, self.databaseID, self )
		
	def getSellBillsInfo( self, page, number ):
		"""
		Exposeds
		向服务器请求获取出售元宝订单信息
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.getSellBillsInfo( page, number, self.databaseID, self )
		
	def getMyBillsInfo( self ):
		"""
		Exposed
		向服务器请求自己的订单的明细
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.getMyBillsInfo( self.databaseID, self )
		
	def getAllMyBills( self ):
		"""
		Exposed
		向服务器请求自己的订单
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.getAllMyBills( self.databaseID, self )
		
	def getBalanceMoney( self ):
		"""
		Exposed
		向服务器请求自己的账号金钱余额
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.getBalanceMoney( self.databaseID, self )
		
	def getBalanceYB( self ):
		"""
		Exposed
		向服务器请求自己的账号元宝余额
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.getBalanceYB( self.databaseID, self )
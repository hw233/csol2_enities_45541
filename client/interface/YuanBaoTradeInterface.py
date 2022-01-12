# -*- coding: gb18030 -*-
#

"""
元宝交易系统模块
"""
import BigWorld
import cPickle
from bwdebug import *
import csdefine
import csstatus
import Const
import event.EventCenter as ECenter
from guis.tooluis.richtext_plugins.PL_Image import PL_Image

class YuanBaoTradeInterface:
	"""
	"""
	def __init__( self ):
		"""
		初始化状态。要在Fight初始化之前
		"""
		pass
		
	# -----------------------------------------------------------------------------------------------------
	# 购买元宝
	def buyYBRequest( self, tick, uid ):
		"""
		请求购买元宝
		"""
		self.base.buyYBRequest( tick, uid )
		
	def onBuyYBRequest( self, tick, uid, state ):
		"""
		define method
		请求购买元宝回调
		"""
		DEBUG_MSG( "onBuyYBRequest  state: %i ."%state )
		if state == csdefine.YB_BILL_STATE_TRADE_LOCK:		# 交易锁定
			self.statusMessage( csstatus.YB_TRADE_BILL_TRADING )
			return
		if state == csdefine.YB_BILL_STATE_OVER_DUE:		# 过期
			self.statusMessage( csstatus.YB_TRADE_BILL_OVERDUE )
			ECenter.fireEvent( "EVT_ON_YBT_DELETE_SELL_BILL", tick, uid )		# 在界面上删除该订单
			return
		if state == csdefine.YB_BILL_STATE_SELL_OUT:			# 售空
			self.statusMessage( csstatus.YB_TRADE_BILL_SELL_OUT )
			ECenter.fireEvent( "EVT_ON_YBT_DELETE_SELL_BILL", tick, uid )		# 在界面上删除该订单
			return
		ECenter.fireEvent( "EVT_ON_YBT_ENABLE_BUY", tick, uid )				# 弹出购买元宝界面
		
	def unBuyYB( self, tick, uid ):
		"""
		取消购买元宝
		"""
		self.base.unBuyYB( tick, uid )
		
	def buyYB( self, tick, uid, yuanbao, rate ):
		"""
		购买元宝
		"""
		cost = yuanbao*rate
		if self.money < cost:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.buyYB( tick, uid, yuanbao, rate )
		
	def onBuyYB( self, tick, uid, deposit ):
		"""
		define method
		购买元宝回调
		"""
		ECenter.fireEvent( "EVT_ON_YBT_BUY_YUANBAO" )	# 关闭购买界面
		if deposit <=0:
			ECenter.fireEvent( "EVT_ON_YBT_DELETE_SELL_BILL", tick, uid )		# 在界面上删除该订单
			return
		ECenter.fireEvent( "EVT_ON_YBT_UPDATE_SELL_BILL", tick, uid, deposit )	# 更细界面上该订单
	# -----------------------------------------------------------------------------------------------------
	# 出售元宝
	def sellYBRequest( self, tick, uid ):
		"""
		请求出售元宝
		"""
		self.base.sellYBRequest( tick, uid )
		
	def onSellYBRequest( self, tick, uid, state ):
		"""
		define method
		请求出售元宝回调
		"""
		DEBUG_MSG( "onSellYBRequest  state: %i ."%state )
		if state == csdefine.YB_BILL_STATE_TRADE_LOCK:		# 交易锁定
			self.statusMessage( csstatus.YB_TRADE_BILL_TRADING )
			return
		if state == csdefine.YB_BILL_STATE_OVER_DUE:		# 过期
			self.statusMessage( csstatus.YB_TRADE_BILL_OVERDUE )
			ECenter.fireEvent( "EVT_ON_YBT_DELETE_BUY_BILL", tick, uid )		# 在界面上删除该订单
			return
		if state == csdefine.YB_BILL_STATE_SELL_OUT:			# 售空
			self.statusMessage( csstatus.YB_TRADE_BILL_SELL_OUT )
			ECenter.fireEvent( "EVT_ON_YBT_DELETE_BUY_BILL", tick, uid )		# 在界面上删除该订单
			return
		ECenter.fireEvent( "EVT_ON_YBT_ENABLE_SELL", tick, uid )				# 弹出购买元宝界面
		
	def unSellYB( self, tick, uid ):
		"""
		取消出售元宝
		"""
		self.base.unSellYB( tick, uid )
		
	def sellYB( self, tick, uid, yuanbao, rate ):
		"""
		出售元宝
		"""
		if self.gold < yuanbao*100:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.sellYB( tick, uid, yuanbao, rate )
		
	def onSellYB( self, tick, uid, deposit ):
		"""
		define method
		出售元宝回调
		"""
		ECenter.fireEvent( "EVT_ON_YBT_SELL_YUANBAO" )		# 关闭出售界面
		if deposit <=0:
			ECenter.fireEvent( "EVT_ON_YBT_DELETE_BUY_BILL", tick, uid )		# 在界面上删除该订单
			return
		ECenter.fireEvent( "EVT_ON_YBT_UPDATE_BUY_BILL", tick, uid, deposit )	# 更细界面上该订单
		
	# -----------------------------------------------------------------------------------------------------
	# 求购订单
	def establishBuyBillRequest( self, yuanbao, rate ):
		"""
		向服务器请求创建求购订单
		"""
		cost = yuanbao * ( rate + int( rate*0.1 ) )
		if self.money < cost:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.establishBuyBillRequest( yuanbao, rate )
		
	def onEstablishBuyBillRequest( self, result ):
		"""
		define method
		请求创建求购订单回调
		"""
		DEBUG_MSG( "onEstablishBuyBillRequest  result: %i ."%result )
		if result == 1:
			self.statusMessage( csstatus.YB_TRADE_BILL_LIMIT )
			return
		elif result == 2:
			self.statusMessage( csstatus.YB_TRADE_ACCOUNT_INIT )
			return
		ECenter.fireEvent( "EVT_ON_YBT_NEW_BUY_BILL" )
		
	def establishBuyBill( self, yuanbao, rate ):
		"""
		建立求购订单
		"""
		cost = yuanbao * ( rate + int( rate*0.1 ) )
		if self.money < cost:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.establishBuyBill( yuanbao, rate )
		
	def onEstablishBuyBill( self, tick, uid, rate, deposit, extra ):
		"""
		define method
		建立求购订单回调
		"""
		costStr = ""
		extraStr = ""
		cost = deposit * rate + extra
		costGold = cost/10000
		costSilver = ( cost%10000 )/100
		costCoin = ( cost%10000 )%100
		extraGold = extra/10000
		extraSilver = ( extra%10000 )/100
		extraCoin = ( extra%10000 )%100
		if costGold > 0:
			costStr += "%d%s"%( costGold, PL_Image.getSource( "guis/controls/goldicon.gui" ) )
		if costSilver > 0:
			costStr += "%d%s"%( costSilver, PL_Image.getSource( "guis/controls/silvericon.gui" ) )
		if costCoin > 0:
			costStr += "%d%s"%( costCoin, PL_Image.getSource( "guis/controls/coinicon.gui" ) )
		if extraGold > 0:
			extraStr += "%d%s"%( extraGold, PL_Image.getSource( "guis/controls/goldicon.gui" ) )
		if extraSilver > 0:
			extraStr += "%d%s"%( extraSilver, PL_Image.getSource( "guis/controls/silvericon.gui" ) )
		if extraCoin > 0:
			extraStr += "%d%s"%( extraCoin, PL_Image.getSource( "guis/controls/coinicon.gui" ) )
		self.statusMessage( csstatus.YB_TRADE_NEW_BUY_BILL, costStr, extraStr )
		ECenter.fireEvent( "EVT_ON_YBT_NEW_BUY_BILL_SUCCESS", tick, uid, rate, deposit )
		
	# -----------------------------------------------------------------------------------------------------
	# 寄售订单
	def establishSellBillRequest( self, yuanbao ):
		"""
		向服务器请求创建寄售订单
		"""
		if self.gold < yuanbao*100:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.establishSellBillRequest( yuanbao )
	
	def onEstablishSellBillRequest( self, result ):
		"""
		define method
		请求创建寄售订单回调
		"""
		DEBUG_MSG( "onEstablishSellBillRequest  result: %i ."%result )
		if result == 1:
			self.statusMessage( csstatus.YB_TRADE_BILL_LIMIT )
			return
		elif result == 2:
			self.statusMessage( csstatus.YB_TRADE_ACCOUNT_INIT )
			return
		ECenter.fireEvent( "EVT_ON_YBT_NEW_SELL_BILL" )
		
	def establishSellBill( self, yuanbao, rate ):
		"""
		建立寄售订单
		"""
		if self.gold < yuanbao*100:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.establishSellBill( yuanbao, rate )
		
	def onEstablishSellBill( self, tick, uid, rate, deposit ):
		"""
		define method
		建立寄售订单回调
		"""
		extraStr = ""
		extra = rate*deposit*0.01
		extraGold = extra/10000
		extraSilver = ( extra%10000 )/100
		extraCoin = ( extra%10000 )%100
		if int( extraGold ) > 0:
			extraStr += "%d%s"%( extraGold, PL_Image.getSource( "guis/controls/goldicon.gui" ) )
		if int( extraSilver ) > 0:
			extraStr += "%d%s"%( extraSilver, PL_Image.getSource( "guis/controls/silvericon.gui" ) )
		if int( extraCoin ) > 0:
			extraStr += "%d%s"%( extraCoin, PL_Image.getSource( "guis/controls/coinicon.gui" ) )
		yuanbaoStr = "%d%s"%( deposit*100, PL_Image.getSource( "guis/general/specialshop/yuanbao.gui" ) )
		self.statusMessage( csstatus.YB_TRADE_NEW_SELL_BILL, yuanbaoStr, extraStr )
		ECenter.fireEvent( "EVT_ON_YBT_NEW_SELL_BILL_SUCCESS", tick, uid, rate, deposit )
		
	# -----------------------------------------------------------------------------------------------------
	# 撤销订单
	def cancleBillRequest( self, tick, uid, bType ):
		"""
		向服务器请求撤销订单
		"""
		if self.money < 100000:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.cancleBillRequest( tick, uid, bType )
		
	def onCancleBillRequest( self, tick, uid, bType, result ):
		"""
		define method
		向服务器请求撤销订单回调
		"""
		DEBUG_MSG( "onCancleBillRequest  result: %i ."%result )
		if result == csdefine.YB_BILL_STATE_SELL_OUT:
			self.statusMessage( csstatus.YB_TRADE_BILL_SELL_OUT )
			return
		if result != csdefine.YB_BILL_STATE_FREE:
			self.statusMessage( csstatus.YB_TRADE_BILL_TRADING )
			return
		ECenter.fireEvent( "EVT_ON_YBT_CANCLE_BILL_ENABLE", tick, uid, bType )
		
	def cancleBill( self, tick, uid, bType ):
		"""
		撤销订单
		"""
		if self.money < 100000:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.cancleBill( tick, uid, bType )
		
	def onCancleBill( self, tick, uid ):
		"""
		define method
		撤销订单回调
		"""
		ECenter.fireEvent( "EVT_ON_YBT_CANCLE_BILL_SUCCESS", tick, uid )
		
	# -----------------------------------------------------------------------------------------------------
	# 取出元宝
	def drawYBRequest( self ):
		"""
		请求取出元宝
		"""
		self.cell.drawYBRequest()
		
	def onDrawYBRequest( self ):
		"""
		define method
		请求取出元宝回调
		"""
		ECenter.fireEvent( "EVT_ON_YBT_DRAW_YB_ENABLE" )
		
	def drawYB( self ):
		"""
		取出元宝
		"""
		self.cell.drawYB()
		
	def onDrawYB( self ):
		"""
		define method
		取出元宝回调
		"""
		ECenter.fireEvent( "EVT_ON_YBT_DRAW_YB_SUCCESS" )
		
	# -----------------------------------------------------------------------------------------------------
	# 取出金钱
	def drawMoneyRequest( self ):
		"""
		请求金钱元宝
		"""
		self.cell.drawMoneyRequest()
		
	def onDrawMoneyRequest( self ):
		"""
		define method
		请求取出金钱回调
		"""
		ECenter.fireEvent( "EVT_ON_YBT_DRAW_MONEY_ENABLE" )
		
	def drawMoney( self ):
		"""
		取出金钱
		"""
		self.cell.drawMoney()
		
	def onDrawMoney( self ):
		"""
		define method
		取出金钱回调
		"""
		ECenter.fireEvent( "EVT_ON_YBT_DRAW_MONEY_SUCCESS" )
		
	# -----------------------------------------------------------------------------------------------------
	# 请求信息
	def getBuyBillsInfo( self, page, number ):
		"""
		向服务器请求获取购买元宝订单信息
		"""
		self.base.getBuyBillsInfo( page, number )
		
	def onGetBuyBillInfo( self, buyBillInfo ):
		"""
		define method
		向服务器请求获取购买元宝订单信息回调
		格式 [ [ tick, uid, roleDBID, deposit, rate ], ... ]
		"""
		billInfo = cPickle.loads( buyBillInfo )
		ECenter.fireEvent( "EVT_ON_YBT_SHOW_BUY_BILL_INFO", billInfo )
		
	def getSellBillsInfo( self, page, number ):
		"""
		向服务器请求获取出售元宝订单信息
		"""
		self.base.getSellBillsInfo( page, number )
		
	def onGetSellBillsInfo( self, sellBillInfo ):
		"""
		define method
		向服务器请求获取出售元宝订单信息回调
		格式 [ [ tick, uid, roleDBID, deposit, rate ], ... ]
		"""
		billInfo = cPickle.loads( sellBillInfo )
		ECenter.fireEvent( "EVT_ON_YBT_SHOW_SELL_BILL_INFO", billInfo )
		
	def getMyBillsInfo( self ):
		"""
		向服务器请求自己的订单的明细
		"""
		self.base.getMyBillsInfo()
		
	def getAllMyBills( self ):
		"""
		向服务器请求自己的订单
		"""
		self.base.getAllMyBills()
		
	def onGetMyBillsInfo( self, myBillInfo ):
		"""
		define method
		[ uid, tType, tState, rate, yuanbao, endTime ]
		向服务器请求自己的订单的明细回调
		"""
		billInfo = cPickle.loads( myBillInfo )
		ECenter.fireEvent( "EVT_ON_YBT_SHOW_MY_BILL_INFO", billInfo )
		
	def onGetAllMyBills( self, myBills ):
		"""
		define method
		[ {tick:uid:billInfo}, {tick:uid:billInfo}, {tick:uid:billInfo}, ... ]
		向服务器请求自己的订单的回调
		"""
		billInfo = cPickle.loads( myBills )
		ECenter.fireEvent( "EVT_ON_YBT_SHOW_MY_ALL_BILL", billInfo )
		
	def getBalanceMoney( self ):
		"""
		向服务器请求自己的账号金钱余额
		"""
		self.base.getBalanceMoney()
		
	def onGetBalanceMoney( self, money ):
		"""
		define method
		向服务器请求自己的账号金钱余额回调
		"""
		ECenter.fireEvent( "EVT_ON_YBT_SHOW_ACC_MON", money )
		
	def getBalanceYB( self ):
		"""
		向服务器请求自己的账号元宝余额
		"""
		self.base.getBalanceYB()
		
	def onGetBalanceYB( self, yuanbao ):
		"""
		define method
		向服务器请求自己的账号元宝余额
		"""
		ECenter.fireEvent( "EVT_ON_YBT_SHOW_ACC_YB", yuanbao )
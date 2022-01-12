# -*- coding: gb18030 -*-
#

"""
Ԫ������ϵͳģ��
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
		��ʼ��״̬��Ҫ��Fight��ʼ��֮ǰ
		"""
		pass
		
	# -----------------------------------------------------------------------------------------------------
	# ����Ԫ��
	def buyYBRequest( self, tick, uid ):
		"""
		������Ԫ��
		"""
		self.base.buyYBRequest( tick, uid )
		
	def onBuyYBRequest( self, tick, uid, state ):
		"""
		define method
		������Ԫ���ص�
		"""
		DEBUG_MSG( "onBuyYBRequest  state: %i ."%state )
		if state == csdefine.YB_BILL_STATE_TRADE_LOCK:		# ��������
			self.statusMessage( csstatus.YB_TRADE_BILL_TRADING )
			return
		if state == csdefine.YB_BILL_STATE_OVER_DUE:		# ����
			self.statusMessage( csstatus.YB_TRADE_BILL_OVERDUE )
			ECenter.fireEvent( "EVT_ON_YBT_DELETE_SELL_BILL", tick, uid )		# �ڽ�����ɾ���ö���
			return
		if state == csdefine.YB_BILL_STATE_SELL_OUT:			# �ۿ�
			self.statusMessage( csstatus.YB_TRADE_BILL_SELL_OUT )
			ECenter.fireEvent( "EVT_ON_YBT_DELETE_SELL_BILL", tick, uid )		# �ڽ�����ɾ���ö���
			return
		ECenter.fireEvent( "EVT_ON_YBT_ENABLE_BUY", tick, uid )				# ��������Ԫ������
		
	def unBuyYB( self, tick, uid ):
		"""
		ȡ������Ԫ��
		"""
		self.base.unBuyYB( tick, uid )
		
	def buyYB( self, tick, uid, yuanbao, rate ):
		"""
		����Ԫ��
		"""
		cost = yuanbao*rate
		if self.money < cost:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.buyYB( tick, uid, yuanbao, rate )
		
	def onBuyYB( self, tick, uid, deposit ):
		"""
		define method
		����Ԫ���ص�
		"""
		ECenter.fireEvent( "EVT_ON_YBT_BUY_YUANBAO" )	# �رչ������
		if deposit <=0:
			ECenter.fireEvent( "EVT_ON_YBT_DELETE_SELL_BILL", tick, uid )		# �ڽ�����ɾ���ö���
			return
		ECenter.fireEvent( "EVT_ON_YBT_UPDATE_SELL_BILL", tick, uid, deposit )	# ��ϸ�����ϸö���
	# -----------------------------------------------------------------------------------------------------
	# ����Ԫ��
	def sellYBRequest( self, tick, uid ):
		"""
		�������Ԫ��
		"""
		self.base.sellYBRequest( tick, uid )
		
	def onSellYBRequest( self, tick, uid, state ):
		"""
		define method
		�������Ԫ���ص�
		"""
		DEBUG_MSG( "onSellYBRequest  state: %i ."%state )
		if state == csdefine.YB_BILL_STATE_TRADE_LOCK:		# ��������
			self.statusMessage( csstatus.YB_TRADE_BILL_TRADING )
			return
		if state == csdefine.YB_BILL_STATE_OVER_DUE:		# ����
			self.statusMessage( csstatus.YB_TRADE_BILL_OVERDUE )
			ECenter.fireEvent( "EVT_ON_YBT_DELETE_BUY_BILL", tick, uid )		# �ڽ�����ɾ���ö���
			return
		if state == csdefine.YB_BILL_STATE_SELL_OUT:			# �ۿ�
			self.statusMessage( csstatus.YB_TRADE_BILL_SELL_OUT )
			ECenter.fireEvent( "EVT_ON_YBT_DELETE_BUY_BILL", tick, uid )		# �ڽ�����ɾ���ö���
			return
		ECenter.fireEvent( "EVT_ON_YBT_ENABLE_SELL", tick, uid )				# ��������Ԫ������
		
	def unSellYB( self, tick, uid ):
		"""
		ȡ������Ԫ��
		"""
		self.base.unSellYB( tick, uid )
		
	def sellYB( self, tick, uid, yuanbao, rate ):
		"""
		����Ԫ��
		"""
		if self.gold < yuanbao*100:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.sellYB( tick, uid, yuanbao, rate )
		
	def onSellYB( self, tick, uid, deposit ):
		"""
		define method
		����Ԫ���ص�
		"""
		ECenter.fireEvent( "EVT_ON_YBT_SELL_YUANBAO" )		# �رճ��۽���
		if deposit <=0:
			ECenter.fireEvent( "EVT_ON_YBT_DELETE_BUY_BILL", tick, uid )		# �ڽ�����ɾ���ö���
			return
		ECenter.fireEvent( "EVT_ON_YBT_UPDATE_BUY_BILL", tick, uid, deposit )	# ��ϸ�����ϸö���
		
	# -----------------------------------------------------------------------------------------------------
	# �󹺶���
	def establishBuyBillRequest( self, yuanbao, rate ):
		"""
		����������󴴽��󹺶���
		"""
		cost = yuanbao * ( rate + int( rate*0.1 ) )
		if self.money < cost:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.establishBuyBillRequest( yuanbao, rate )
		
	def onEstablishBuyBillRequest( self, result ):
		"""
		define method
		���󴴽��󹺶����ص�
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
		�����󹺶���
		"""
		cost = yuanbao * ( rate + int( rate*0.1 ) )
		if self.money < cost:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.establishBuyBill( yuanbao, rate )
		
	def onEstablishBuyBill( self, tick, uid, rate, deposit, extra ):
		"""
		define method
		�����󹺶����ص�
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
	# ���۶���
	def establishSellBillRequest( self, yuanbao ):
		"""
		����������󴴽����۶���
		"""
		if self.gold < yuanbao*100:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.establishSellBillRequest( yuanbao )
	
	def onEstablishSellBillRequest( self, result ):
		"""
		define method
		���󴴽����۶����ص�
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
		�������۶���
		"""
		if self.gold < yuanbao*100:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.establishSellBill( yuanbao, rate )
		
	def onEstablishSellBill( self, tick, uid, rate, deposit ):
		"""
		define method
		�������۶����ص�
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
	# ��������
	def cancleBillRequest( self, tick, uid, bType ):
		"""
		�����������������
		"""
		if self.money < 100000:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.cancleBillRequest( tick, uid, bType )
		
	def onCancleBillRequest( self, tick, uid, bType, result ):
		"""
		define method
		������������������ص�
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
		��������
		"""
		if self.money < 100000:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.cell.cancleBill( tick, uid, bType )
		
	def onCancleBill( self, tick, uid ):
		"""
		define method
		���������ص�
		"""
		ECenter.fireEvent( "EVT_ON_YBT_CANCLE_BILL_SUCCESS", tick, uid )
		
	# -----------------------------------------------------------------------------------------------------
	# ȡ��Ԫ��
	def drawYBRequest( self ):
		"""
		����ȡ��Ԫ��
		"""
		self.cell.drawYBRequest()
		
	def onDrawYBRequest( self ):
		"""
		define method
		����ȡ��Ԫ���ص�
		"""
		ECenter.fireEvent( "EVT_ON_YBT_DRAW_YB_ENABLE" )
		
	def drawYB( self ):
		"""
		ȡ��Ԫ��
		"""
		self.cell.drawYB()
		
	def onDrawYB( self ):
		"""
		define method
		ȡ��Ԫ���ص�
		"""
		ECenter.fireEvent( "EVT_ON_YBT_DRAW_YB_SUCCESS" )
		
	# -----------------------------------------------------------------------------------------------------
	# ȡ����Ǯ
	def drawMoneyRequest( self ):
		"""
		�����ǮԪ��
		"""
		self.cell.drawMoneyRequest()
		
	def onDrawMoneyRequest( self ):
		"""
		define method
		����ȡ����Ǯ�ص�
		"""
		ECenter.fireEvent( "EVT_ON_YBT_DRAW_MONEY_ENABLE" )
		
	def drawMoney( self ):
		"""
		ȡ����Ǯ
		"""
		self.cell.drawMoney()
		
	def onDrawMoney( self ):
		"""
		define method
		ȡ����Ǯ�ص�
		"""
		ECenter.fireEvent( "EVT_ON_YBT_DRAW_MONEY_SUCCESS" )
		
	# -----------------------------------------------------------------------------------------------------
	# ������Ϣ
	def getBuyBillsInfo( self, page, number ):
		"""
		������������ȡ����Ԫ��������Ϣ
		"""
		self.base.getBuyBillsInfo( page, number )
		
	def onGetBuyBillInfo( self, buyBillInfo ):
		"""
		define method
		������������ȡ����Ԫ��������Ϣ�ص�
		��ʽ [ [ tick, uid, roleDBID, deposit, rate ], ... ]
		"""
		billInfo = cPickle.loads( buyBillInfo )
		ECenter.fireEvent( "EVT_ON_YBT_SHOW_BUY_BILL_INFO", billInfo )
		
	def getSellBillsInfo( self, page, number ):
		"""
		������������ȡ����Ԫ��������Ϣ
		"""
		self.base.getSellBillsInfo( page, number )
		
	def onGetSellBillsInfo( self, sellBillInfo ):
		"""
		define method
		������������ȡ����Ԫ��������Ϣ�ص�
		��ʽ [ [ tick, uid, roleDBID, deposit, rate ], ... ]
		"""
		billInfo = cPickle.loads( sellBillInfo )
		ECenter.fireEvent( "EVT_ON_YBT_SHOW_SELL_BILL_INFO", billInfo )
		
	def getMyBillsInfo( self ):
		"""
		������������Լ��Ķ�������ϸ
		"""
		self.base.getMyBillsInfo()
		
	def getAllMyBills( self ):
		"""
		������������Լ��Ķ���
		"""
		self.base.getAllMyBills()
		
	def onGetMyBillsInfo( self, myBillInfo ):
		"""
		define method
		[ uid, tType, tState, rate, yuanbao, endTime ]
		������������Լ��Ķ�������ϸ�ص�
		"""
		billInfo = cPickle.loads( myBillInfo )
		ECenter.fireEvent( "EVT_ON_YBT_SHOW_MY_BILL_INFO", billInfo )
		
	def onGetAllMyBills( self, myBills ):
		"""
		define method
		[ {tick:uid:billInfo}, {tick:uid:billInfo}, {tick:uid:billInfo}, ... ]
		������������Լ��Ķ����Ļص�
		"""
		billInfo = cPickle.loads( myBills )
		ECenter.fireEvent( "EVT_ON_YBT_SHOW_MY_ALL_BILL", billInfo )
		
	def getBalanceMoney( self ):
		"""
		������������Լ����˺Ž�Ǯ���
		"""
		self.base.getBalanceMoney()
		
	def onGetBalanceMoney( self, money ):
		"""
		define method
		������������Լ����˺Ž�Ǯ���ص�
		"""
		ECenter.fireEvent( "EVT_ON_YBT_SHOW_ACC_MON", money )
		
	def getBalanceYB( self ):
		"""
		������������Լ����˺�Ԫ�����
		"""
		self.base.getBalanceYB()
		
	def onGetBalanceYB( self, yuanbao ):
		"""
		define method
		������������Լ����˺�Ԫ�����
		"""
		ECenter.fireEvent( "EVT_ON_YBT_SHOW_ACC_YB", yuanbao )
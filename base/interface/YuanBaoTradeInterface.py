# -*- coding: gb18030 -*-
#

"""
Ԫ������ϵͳģ��
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
	�����԰汾���������� by ����
	"""
	@staticmethod
	def locale_default( ybtInterface ):
		"""
		�����
		"""
		languageDepart.originalFunc( ybtInterface )
		ybtInterface.ybtMgr = BigWorld.globalData["YuanBaoTradeMgr"]


class YuanBaoTradeInterface:
	"""
	"""
	@languageDepart
	def __init__( self ):
		"""
		��ʼ��״̬��Ҫ��Fight��ʼ��֮ǰ
		"""
		self.ybtMgr = None
		
		# ��ʱ��¼�ý�ɫ��ռ�н���Ȩ�Ķ�������
		self.tempBillTick = 0
		self.tempBillUid = 0
		self.tempBillType = 0
		
	def billLockRecord( self, tick, uid, bType ):
		"""
		define method
		��ʱ��¼�ý�ɫ��ռ�н���Ȩ�Ķ������ݣ��Ա�����ʱ�Զ�����
		"""
		self.tempBillTick = tick
		self.tempBillUid = uid
		self.tempBillType = bType
		
	def billUnLockRecord( self ):
		"""
		define method
		�����ʱ��¼�Ľ�ɫ��ռ�н���Ȩ�Ķ�������
		"""
		self.tempBillTick = 0
		self.tempBillUid = 0
		self.tempBillType = 0
		
	def ybt_switch( self, trigger ):
		"""
		define method
		����Ԫ�����׹���
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
		�������ʱ��Ԫ������ϵͳ��һЩ������������ɸý�ɫ�����Ķ���
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
	# ����Ԫ��
	def buyYBRequest( self, tick, uid ):
		"""
		Exposed method
		������Ԫ��
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
		ȡ������Ԫ��
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.unBuyYB( tick, uid, self.id, self )
		
	def buyYB( self, tick, uid, yuanbao, rate ):
		"""
		define method
		����Ԫ��
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.buyYB( tick, uid, yuanbao, rate, self )
		
	def onBuyYB( self, yuanbao ):
		"""
		define method
		����Ԫ���ص�
		"""
		self.addGold( yuanbao, csdefine.CHANGE_GOLD_YBT_SELL )
		
	# -----------------------------------------------------------------------------------------------------
	# ����Ԫ��
	def sellYBRequest( self, tick, uid ):
		"""
		Exposed method
		�������Ԫ��
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
		ȡ������Ԫ��
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.unSellYB( tick, uid, self.id, self )
		
	def sellYB( self, tick, uid, yuanbao, rate ):
		"""
		define method
		����Ԫ��
		"""
		if self.gold < yuanbao*100:
			self.statusMessage( csstatus.SPECIALSHOP_GOLD_NOT_ENOUGH )
			return
		self.ybtMgr.sellYB( tick, uid, yuanbao, rate, self )
		
	def onSellYB( self, cost ):
		"""
		define method
		����Ԫ���ص�
		"""
		if self.ybtMgr is None:
			return
		if not self.payGold( cost, csdefine.CHANGE_GOLD_YBT_SELL ):
			ERROR_MSG( "sell yuan bao pay gold failed." )
			
	# -----------------------------------------------------------------------------------------------------
	# �󹺶���
	def establishBuyBillRequest( self ):
		"""
		define method
		�������󹺶���
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.establishBuyBillRequest( self.databaseID, self.getName(), self )
		
	def establishBuyBill( self, yuanbao, rate ):
		"""
		define method
		�����󹺶���
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.establishBuyBill( yuanbao, rate, self.databaseID, self )
		
	def onEstablishBuyBill( self, rate ):
		"""
		define method
		�����󹺶�����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_EXTABLISH_YB_BUY_BILL%( self.getName(), rate ), [] )
	# -----------------------------------------------------------------------------------------------------
	# ���۶���
	def establishSellBillRequest( self, yuanbao ):
		"""
		define method
		���������۶���
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
		�������۶���
		"""
		if self.ybtMgr is None:
			return
		if self.gold < yuanbao:
			return
		self.ybtMgr.establishSellBill( yuanbao, rate, self.databaseID, self )
		
	def onEstablishSellBill( self, cost, rate ):
		"""
		define method
		�������۶����ص�
		"""
		if self.ybtMgr is None:
			return
		if not self.payGold( cost, csdefine.CHANGE_GOLD_YBT_SELL_BILL ):
			ERROR_MSG( "new sell bill pay gold failed." )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_EXTABLISH_YB_SELL_BILL%( self.getName(), rate ), [] )
			
	# -----------------------------------------------------------------------------------------------------
	# ��������
	def cancleBillRequest( self, tick, uid, bType ):
		"""
		define method
		����������
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.cancleBillRequest( tick, uid, bType, self )
		
	def cancleBill( self, tick, uid, bType ):
		"""
		define method
		��������
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.cancleBill( tick, uid, bType, self )
		
	def onCancleBill( self, tick, uid, desposit ):
		"""
		define method
		���������ص�
		"""
		if self.ybtMgr is None:
			return
		self.addGold( desposit, csdefine.CHANGE_GOLD_YBT_CANCLE_BILL )
		self.cell.onCancleBill( 0, 0, 0 )
		self.client.onCancleBill( tick, uid )
		
	# -----------------------------------------------------------------------------------------------------
	# ȡ��Ԫ��
	def drawYB( self ):
		"""
		define method
		ȡ��Ԫ��
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.drawYB( self.databaseID, self )
		
	def onDrawYB( self, yuanbao ):
		"""
		define method
		ȡ��Ԫ���ص�
		"""
		self.addGold( yuanbao, csdefine.CHANGE_GOLD_YBT_DRAW_YB )
		self.statusMessage( csstatus.YB_TRADE_NEW_DRAW_YB, yuanbao )
		self.client.onDrawYB()
		
	# -----------------------------------------------------------------------------------------------------
	# ȡ����Ǯ
	def drawMoney( self ):
		"""
		define method
		ȡ����Ǯ
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.drawMoney( self.databaseID, self )
		
	# -----------------------------------------------------------------------------------------------------
	# ������Ϣ
	def getBuyBillsInfo( self, page, number ):
		"""
		Exposeds
		������������ȡ����Ԫ��������Ϣ
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.getBuyBillsInfo( page, number, self.databaseID, self )
		
	def getSellBillsInfo( self, page, number ):
		"""
		Exposeds
		������������ȡ����Ԫ��������Ϣ
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.getSellBillsInfo( page, number, self.databaseID, self )
		
	def getMyBillsInfo( self ):
		"""
		Exposed
		������������Լ��Ķ�������ϸ
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.getMyBillsInfo( self.databaseID, self )
		
	def getAllMyBills( self ):
		"""
		Exposed
		������������Լ��Ķ���
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.getAllMyBills( self.databaseID, self )
		
	def getBalanceMoney( self ):
		"""
		Exposed
		������������Լ����˺Ž�Ǯ���
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.getBalanceMoney( self.databaseID, self )
		
	def getBalanceYB( self ):
		"""
		Exposed
		������������Լ����˺�Ԫ�����
		"""
		if self.ybtMgr is None:
			return
		self.ybtMgr.getBalanceYB( self.databaseID, self )
# -*- coding: gb18030 -*-
#

"""
Ԫ������ϵͳģ��
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
		��ʼ��״̬��Ҫ��Fight��ʼ��֮ǰ
		"""
		pass
		
	def ybt_switch( self, trigger ):
		"""
		֪ͨbase����Ԫ�����׹���
		"""
		self.base.ybt_switch( trigger )
	# -----------------------------------------------------------------------------------------------------
	# ����Ԫ��
	def buyYB( self, selfEntityID, tick, uid, yuanbao, rate ):
		"""
		Exposed method
		����Ԫ��
		"""
		if self.iskitbagsLocked():	# ��������
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
		����Ԫ���ص�
		"""
		if not self.payMoney( cost, csdefine.CHANGE_MONEY_BUY_YUANBAO ):
			ERROR_MSG( "Buy yuan bao pay money faild." )

	# -----------------------------------------------------------------------------------------------------
	# ����Ԫ��
	def sellYB( self, selfEntityID, tick, uid, yuanbao, rate ):
		"""
		Exposed method
		����Ԫ��
		"""
		if self.iskitbagsLocked():	# ��������
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		self.base.sellYB( tick, uid, yuanbao, rate )
		
	def onSellYB( self, money ):
		"""
		define method
		����Ԫ���ص�
		"""
		self.addMoney( money, csdefine.CHANGE_MONEY_BUY_YUANBAO )
		
	# -----------------------------------------------------------------------------------------------------
	# �󹺶���
	def establishBuyBillRequest( self, selfEntityID, yuanbao, rate ):
		"""
		Exposed method
		�������󹺶���
		"""
		if self.iskitbagsLocked():	# ��������
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
		�����󹺶���
		"""
		if self.iskitbagsLocked():	# ��������
			return
		cost = yuanbao* ( rate + int( rate*0.1 ) )
		if self.money < cost:
			return
		self.base.establishBuyBill( yuanbao, rate )
		
	def onEstablishBuyBill( self, cost ):
		"""
		defined method
		�����󹺶����ص�
		"""
		if not self.payMoney( cost, csdefine.CHANGE_MONEY_BUY_YUANBAO ):
			ERROR_MSG( "new buy bill pay money faild." )
			
	# -----------------------------------------------------------------------------------------------------
	# ���۶���
	def establishSellBillRequest( self, selfEntityID, yuanbao ):
		"""
		Exposed method
		����������۵�
		"""
		if self.iskitbagsLocked():	# ��������
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		self.base.establishSellBillRequest( yuanbao )
		
	def establishSellBill( self, selfEntityID, yuanbao, rate ):
		"""
		Exposed method
		�������۶���
		"""
		if self.iskitbagsLocked():	# ��������
			return
		self.base.establishSellBill( yuanbao, rate )
		
	def onEstablishSellBill( self, cost ):
		"""
		defined method
		�������۶����ص�
		"""
		if not self.payMoney( cost, csdefine.CHANGE_MONEY_BUY_YUANBAO ):
			ERROR_MSG( "new sell bill pay money faild." )
		
	# -----------------------------------------------------------------------------------------------------
	# ��������
	def cancleBillRequest( self, selfEntityID, tick, uid, bType ):
		"""
		Exposed method
		����������
		"""
		if self.iskitbagsLocked():	# ��������
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		if self.money < 100000:
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return
		self.base.cancleBillRequest( tick, uid, bType )
		
	def cancleBill( self, selfEntityID, tick, uid, bType ):
		"""
		Exposed method
		��������
		"""
		if self.iskitbagsLocked() or self.money < 100000:
			return
		self.base.cancleBill( tick, uid, bType )
		
	def onCancleBill( self, tick, uid, desposit ):
		"""
		define method
		���������ص�
		"""
		self.addMoney( desposit, csdefine.CHANGE_MONEY_CANCLE_YBT_BILL )
		#if self.payMoney( 100000, csdefine.CHANGE_MONEY_CANCLE_YBT_BILL ):
		#	self.statusMessage( csstatus.YB_TRADE_NEW_BILL_EXTRA, 100000 )
		if tick == 0 or uid == 0:
			return
		self.client.onCancleBill( tick, uid )
		
	# -----------------------------------------------------------------------------------------------------
	# ȡ��Ԫ��
	def drawYBRequest( self, selfEntityID ):
		"""
		Exposed method
		����ȡ��Ԫ��
		"""
		if self.iskitbagsLocked():	# ��������
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		self.client.onDrawYBRequest()
		
	def drawYB( self, selfEntityID ):
		"""
		Exposed method
		ȡ��Ԫ��
		"""
		if self.iskitbagsLocked():	# ��������
			return
		self.base.drawYB()
		
	# -----------------------------------------------------------------------------------------------------
	# ȡ����Ǯ
	def drawMoneyRequest( self, selfEntityID ):
		"""
		Exposed method
		����ȡ����Ǯ
		"""
		if self.iskitbagsLocked():	# ��������
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		self.client.onDrawMoneyRequest()
		
	def drawMoney( self, selfEntityID ):
		"""
		Exposed method
		ȡ����Ǯ
		"""
		if self.iskitbagsLocked():	# ��������
			return
		self.base.drawMoney()
		
	def onDrawMoney( self, money ):
		"""
		define method
		ȡ����Ǯ�ص�
		"""
		self.addMoney( money, csdefine.CHANGE_MONEY_DRAW_MONEY )
		gold = money/10000
		silver = ( money%100 )/100
		coin = ( money%100 )%100
		self.statusMessage( csstatus.YB_TRADE_NEW_DRAW_MONEY, gold, silver, coin )
		self.client.onDrawMoney()
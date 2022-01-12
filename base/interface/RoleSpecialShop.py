# -*- coding: gb18030 -*-
#
# $Id: RoleSpecialShop.py,v 1.1 2008-08-15 09:13:08 wangshufeng Exp $


import BigWorld
import cschannel_msgs
import ShareTexts as ST
import csdefine
import csconst
import csstatus
import sys
from bwdebug import *
from MsgLogger import g_logger
from SpecialShopMgr import specialShop

class RoleSpecialShop:
	"""
	�����̳�
	"""
	def __init__( self ):
		pass

	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def spe_requestItemsPrices( self, itemIDs, moneyType ) :
		"""
		Exposed method.
		�ͻ���������ָ����Ʒ�۸�
		"""
		specialShop.requestItemsPrices( self, itemIDs, moneyType )

	def spe_updateGoods( self, queryType, moneyType ):
		"""
		Exposed method.
		�������ĳһ���͵��̳�����

		@param queryType :	��ѯ����Ʒ����
		@type queryType :	UINT32
		"""
		if queryType not in csconst.SPECIALSHOP_GOOS_LIST:
			return

		specialShop.updateGoods( self, queryType, moneyType )

	def spe_shopping( self, itemID, amount, moneyType ):
		"""
		Exposed method.
		�������Ʒ

		@param itemID : ��Ʒid
		@type itemID : ITEM_ID
		@param amount : ��Ʒ����
		@type amount : INT
		@param moneyType : ��������( ��Ԫ������Ԫ�� )
		@type amount : UINT32
		"""
		if moneyType not in [ csdefine.SPECIALSHOP_MONEY_TYPE_GOLD, csdefine.SPECIALSHOP_MONEY_TYPE_SILVER ]:
			ERROR_MSG( "Money type error:%i." % moneyType )
			return

		totalPrice = specialShop.getItemPrice( itemID, amount, moneyType )
		if totalPrice < 0:
			HACK_MSG( "player( %s ) buy item( %i ) error:there's no this item in special shop." % ( self.getName(), itemID ) )
			return
		if not hasattr( self, "cell" ):		# ��ʱ��ҵ�cell�п����ѱ�����
			return
		if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_SILVER:
			moneyAmount = self.getUsableSilver()
			statusMessageID = csstatus.SPECIALSHOP_SILVER_NOT_ENOUGH
			freezeFunc = self.freezeSilver
		else:
			moneyAmount = self.getUsableGold()
			statusMessageID = csstatus.SPECIALSHOP_GOLD_NOT_ENOUGH
			freezeFunc = self.freezeGold
		if moneyAmount < totalPrice:
			self.statusMessage( statusMessageID )
		else:
			self.cell.spe_receiveSpecialGoods( itemID, amount, totalPrice, moneyType )
			freezeFunc( totalPrice )			# ����Ԫ��

	def spe_buyItemCB( self, itemID, amount, totalPrice, moneyType, state ):
		"""
		Define method.
		����Ʒ����ص�

		@param itemID : ��Ʒid
		@type itemID : ITEM_ID
		@param amount : �����������
		@type amount : INT32
		@param totalPrice : �ܼ�
		@type totalPrice : INT32
		@param moneyType : Ԫ������
		@type moneyType : INT8
		@param state : ����Ƿ�ɹ������Ʒ
		@type state : BOOL
		"""
		if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_SILVER:
			self.thawSilver( totalPrice )
			if state:
				self.paySilver( totalPrice, csdefine.CHANGE_SILVER_BUYITEM )
				try:
					g_logger.specialShopBuyLog( self.accountEntity.playerName, 0, totalPrice, itemID, amount )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
		else:
			self.thawGold( totalPrice )
			if state:
				self.payGold( totalPrice, csdefine.CHANGE_GOLD_BUYITEM  )
				try:
					g_logger.specialShopBuyLog( self.accountEntity.playerName, totalPrice, 0, itemID, amount )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )

	def spe_onAutoUseYell( self, itemID, moneyType, msg, blobArgs ):
		"""
		Define method.
		ϵͳ������Զ��������
		hyw--2009.03.25
		@param		item	  : ��Ʒid
		@type		item	  : ITEM_ID
		@param		moneyType : ��������
		@type		moneyType : UINT8
		@param		msg	  : Ҫ���͵�ȫ����Ϣ
		@type		msg	  : str
		"""
		price = specialShop.getItemPrice( itemID, 1, moneyType )
		if price < 0:
			ERROR_MSG( "���( %s )�̳��Զ����������������������Ʒid( %i )����ȷ��" % ( self.getName(), itemID ) )
			return

		if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_SILVER:
			moneyAmount = self.getUsableSilver()
			statusMessageID = csstatus.CHAT_TURNNEL_SILER_NOENOUGH
			payFunc = self.paySilver
		else:
			moneyAmount = self.getUsableGold()
			statusMessageID = csstatus.CHAT_WELKIN_GOLD_NOENOUGH
			payFunc = self.payGold

		if moneyAmount < price:
			self.statusMessage( statusMessageID )
		else:
			if itemID == csconst.CHAT_WELKIN_ITEM :
				self.chat_handleMessage( csdefine.CHAT_CHANNEL_WELKIN_YELL, "", msg, blobArgs )
			elif itemID == csconst.CHAT_TUNNEL_ITEM :
				self.chat_handleMessage( csdefine.CHAT_CHANNEL_TUNNEL_YELL, "", msg, blobArgs )
			payFunc( price, csdefine.AUTOUSEYELL )
			INFO_MSG( "player( %s ) auto buy yell item( %i ) and use, price:%i." % ( self.getName(), itemID, price ) )
			if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_SILVER:
				try:
					g_logger.specialShopBuyLog( self.accountEntity.playerName, 0, totalPrice, itemID, 1 )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
			else:
				try:
					g_logger.specialShopBuyLog( self.accountEntity.playerName, totalPrice, 0, itemID, 1 )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )

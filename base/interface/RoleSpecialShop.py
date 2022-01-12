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
	道具商城
	"""
	def __init__( self ):
		pass

	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def spe_requestItemsPrices( self, itemIDs, moneyType ) :
		"""
		Exposed method.
		客户端请求发送指定物品价格
		"""
		specialShop.requestItemsPrices( self, itemIDs, moneyType )

	def spe_updateGoods( self, queryType, moneyType ):
		"""
		Exposed method.
		请求更新某一类型的商城配置

		@param queryType :	查询的商品类型
		@type queryType :	UINT32
		"""
		if queryType not in csconst.SPECIALSHOP_GOOS_LIST:
			return

		specialShop.updateGoods( self, queryType, moneyType )

	def spe_shopping( self, itemID, amount, moneyType ):
		"""
		Exposed method.
		玩家买物品

		@param itemID : 物品id
		@type itemID : ITEM_ID
		@param amount : 物品数量
		@type amount : INT
		@param moneyType : 货币类型( 金元宝或银元宝 )
		@type amount : UINT32
		"""
		if moneyType not in [ csdefine.SPECIALSHOP_MONEY_TYPE_GOLD, csdefine.SPECIALSHOP_MONEY_TYPE_SILVER ]:
			ERROR_MSG( "Money type error:%i." % moneyType )
			return

		totalPrice = specialShop.getItemPrice( itemID, amount, moneyType )
		if totalPrice < 0:
			HACK_MSG( "player( %s ) buy item( %i ) error:there's no this item in special shop." % ( self.getName(), itemID ) )
			return
		if not hasattr( self, "cell" ):		# 此时玩家的cell有可能已被销毁
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
			freezeFunc( totalPrice )			# 冻结元宝

	def spe_buyItemCB( self, itemID, amount, totalPrice, moneyType, state ):
		"""
		Define method.
		买物品结果回调

		@param itemID : 物品id
		@type itemID : ITEM_ID
		@param amount : 欲购买的数量
		@type amount : INT32
		@param totalPrice : 总价
		@type totalPrice : INT32
		@param moneyType : 元宝类型
		@type moneyType : INT8
		@param state : 玩家是否成功获得物品
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
		系统帮玩家自动购买道具
		hyw--2009.03.25
		@param		item	  : 物品id
		@type		item	  : ITEM_ID
		@param		moneyType : 货币类型
		@type		moneyType : UINT8
		@param		msg	  : 要发送的全局消息
		@type		msg	  : str
		"""
		price = specialShop.getItemPrice( itemID, 1, moneyType )
		if price < 0:
			ERROR_MSG( "玩家( %s )商城自动购买地音符、天音符，物品id( %i )不正确。" % ( self.getName(), itemID ) )
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

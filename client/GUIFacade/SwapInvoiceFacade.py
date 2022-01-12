# -*- coding: gb18030 -*-
#
# $Id: SwapInvoiceFacade.py,v 1.17 2008-05-30 09:54:48 fangpengjun Exp $

from bwdebug import *
import BigWorld
from ItemsFactory import ObjectItem
from event.EventCenter import *
import csconst

class SwapInvoiceFacade:
	@staticmethod
	def reset():
		pass



# ------------------------------->
# 用于让底层调用
# ------------------------------->
def onInviteSwapItem( invitorName, flag ):
	"""
	有人邀请进行交易

	flag为1则表示是物品交易，否则是宠物交易
	"""
	if flag:
		fireEvent( "EVT_ON_RSI_INVITE_SWAP_ITEM", invitorName )
	else:
		fireEvent( "EVT_ON_RSI_INVITE_SWAP_PET", invitorName )

def onSwapItemBegin( invitorName ):
	"""
	开始进入交易
	"""
	# 进入交易状态时需要把两边的按钮初始化到默认状态
	#onDstSwapStateChanged( False, False )
	#onSelfSwapStateChanged( False, False )
	# 通知交易开始
	fireEvent( "EVT_ON_RSI_SWAP_ITEM_BEGIN", invitorName )

def onSwapItemEnd():
	"""
	交易结束
	"""
	fireEvent( "EVT_ON_RSI_SWAP_ITEM_END" )


def onDstSwapItemChanged( swapOrder, item ):
	"""
	交易目标物品改变

	@param swapOrder: 交易栏的位置
	@type  swapOrder: INT
	@param      item: 改变后的物品，如果变为空则置None
	@type       item: CItemBase
	"""
	if item is None:
		itemInfo = None
	else:
		itemInfo = ObjectItem( item )
	fireEvent( "EVT_ON_RSI_DST_ITEM_CHANGED", swapOrder, itemInfo )

def onDstSwapMoneyChanged( quantity ):
	"""
	交易目标改变金钱数量
	"""
	fireEvent( "EVT_ON_RSI_DST_MONEY_CHANGED", quantity )

def onSelfSwapItemChanged( swapOrder, item ):
	"""
	自己某个位置的物品信息改变

	@param swapOrder: 交易栏的位置
	@type  swapOrder: INT
	@param      item: 改变后的物品，如果变为空则置None
	@type       item: CItemBase
	"""
	if item is None:
		itemInfo = None
	else:
		itemInfo = ObjectItem( item )
	fireEvent( "EVT_ON_RSI_SELF_ITEM_CHANGED", swapOrder, itemInfo )

def onSelfSwapMoneyChanged( quantity ):
	"""
	自己金钱数量改变
	"""
	fireEvent( "EVT_ON_RSI_SELF_MONEY_CHANGED", quantity )


# ------------------------------->
# facade interface
# ------------------------------->
def getSwapItemBagSpace():
	"""
	交易框大小
	@return: int
	"""
	return csconst.TRADE_ITEMS_UPPER_LIMIT

def inviteSwapItem( entity, flag ):
	"""
	邀请目标entity进行交易
	"""
	BigWorld.player().si_requestSwap( entity, flag )

def inviteSwapItemReply( accept = True ):
	"""
	交易邀请答复

	@param accept: 是否接受交易
	@type  accept: BOOL
	"""
	BigWorld.player().si_replySwapItemInvite( accept )

def cancelSwapItem():
	"""
	请求取消交易
	"""
	BigWorld.player().si_tradeCancel()

def changeSwapItem( swapOrder, kitOrder, order ):
	"""
	改变某个位置上的交易物品

	@param swapOrder: 交易栏中的位置
	@type  swapOrder: INT
	@param  kitOrder: 物品所在的背包
	@type   kitOrder: INT
	@param     order: 物品所在的位置
	@type      order: INT
	"""
	BigWorld.player().si_changeItem( swapOrder, kitOrder, order )

def removeSwapItem( swapOrder ):
	"""
	删除某个位置上的交易物品

	@param swapOrder: 交易栏中的位置
	@type  swapOrder: INT
	"""
	BigWorld.player().si_removeItem( swapOrder )

def changeSwapMoney( quantity ):
	"""
	改变金钱数

	@param quantity: 金钱数量
	@type  quantity: INT
	"""
	BigWorld.player().si_changeMoney( quantity )

def swapAccept():
	"""
	第一次确定
	"""
	BigWorld.player().si_accept()

def swapAccept2():
	"""
	第二次确定
	"""
	BigWorld.player().si_secondAccept( True )

def getDstSwapItemDescription( swapOrder ):
	"""
	获取目标的物品描述

	@return: String
	"""
	player = BigWorld.player()
	try:
		return player.dstSIItem[swapOrder].description( player )
	except KeyError:
		return ""

def getSelfSwapItemDescription( swapOrder ):
	"""
	获取自己的物品描述

	@return: String
	"""
	player = BigWorld.player()
	try:
		return player.mySIItem[swapOrder].description( player )
	except KeyError:
		return ""

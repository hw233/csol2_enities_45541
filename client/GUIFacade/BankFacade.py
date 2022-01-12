# -*- coding: gb18030 -*-
#
# $Id: BankFacade.py,v 1.9 2008-05-30 03:07:39 yangkai Exp $

"""
implement bank facade
2006/10/25 : writen by huangyongwei
"""

import BigWorld
from bwdebug import *
from ItemsFactory import ObjectItem
from event.EventCenter import *
import csdefine
import ItemTypeEnum
import csstatus

class BankFacade :
	@staticmethod
	def reset() :
		pass

# --------------------------------------------------------------------
# called by base
# --------------------------------------------------------------------

def onHideBankWindow() :
	"""
	request for hiding bank window
	"""
	fireEvent( "EVT_ON_HIDE_STORE_WINDOW" )

# -----------------------------------------------------
def onUpdateBankItem( itemIndex, item ) :
	"""
	when an item had been updated, it will be called
	@type			index : int
	@param			index : item index in bank window
	@type			item  : instance
	@param			item  : object item instance
	@return				  : None
	"""
	itemInfo = None
	if item is not None :
		tamount = item.getAmount()
		ticon = item.icon()
		tid = item.id
		itemInfo = ObjectItem( item )
	fireEvent( "EVT_ON_UPDATE_STORE_ITEM",itemIndex, itemInfo )

def onBankMoneyChanged( amount ) :
	"""
	when store money changed, it will be changed
	@type			amount : int
	@param			amount : the number of store money
	@return				   : None
	"""
	fireEvent( "EVT_ON_STORE_MONEY_CHANGED", amount )

# --------------------------------------------------------------------
# called by ui
# --------------------------------------------------------------------
def tradeOverInventory():
	"""
	when Inventory over it will called
	"""
	player = BigWorld.player()
	player.cell.leaveTradeIV()

def getBankItemDescription( index ) :
	"""
	get item description
	@type			index : int
	@param			index : the item index
	@return				  : None
	"""
	player = BigWorld.player()
	return player.getItemDescriptionIV( index )

# -----------------------------------------------------
def storeBankItem( indexInBank, kitbagID, indexInBag, amount ) :
	"""
	store items
	@type			indexInBank : int
	@param			indexInBank : destanation in bank
	@type			kitBagID	: int
	@param			kitBagID	: kit bag index
	@type			indexInKit	: int
	@param			indexInKit	: source index in kit bag
	@type			amount		: int
	@param			amount		: the number of item you will be stored
	@return						: None
	"""
	player = BigWorld.player()
	player.storeItemIV( indexInBank, kitbagID, indexInBag, amount )

def storeBankMoney( amount ) :
	"""
	store money
	@type			money 		: int32
	@param			money		: amount of money you want to store
	@return						: None
	"""
	player = BigWorld.player()
	BigWorld.player().storeMoneyIV( amount )

# -------------------------------------------
def takeBankItem( indexInBank, kitbagID, indexInBag, amount ) :
	"""
	store items
	@type			indexInBank : int
	@param			indexInBank : destanation in bank
	@type			kitBagID	: int
	@param			kitBagID	: kit bag index
	@type			indexInKit	: int
	@param			indexInKit	: source index in kit bag
	@type			amount		: int
	@param			amount		: the number of item you will be stored
	@return						: None
	"""
	player = BigWorld.player()
	player.takeItemIV( indexInBank, kitbagID, indexInBag, amount )

def takeBankMoney( amount ) :
	"""
	store money
	@type			money 		: int32
	@param			money		: amount of money you want to take
	@return						: None
	"""
	BigWorld.player().takeMoneyIV( amount )

def getHireMoney( index, time ):
# 通过租赁的背包组和时间从服务器端得到相应租金
	money = 12345
	return money

def getRemain( index, time ): # 获得剩余时间
	return 0
#	remainTime =

# -----------------------------------------------------
def swapBankItem( srcIdx, dstIdx ) :
	"""
	exchange two items' sits
	@type			srcIndex : int
	@param			srcIndex : the source index
	@type			dstIndex : int
	@param			dstIndex : the distance index
	@return 				 : None
	"""
	player = BigWorld.player()
	player.swapItemIV( srcIdx, dstIdx )

def splitBankItem( index, amount ) :
	"""
	@type			srcIndex : int
	@param			srcIndex : the source index
	@type			amount	 : int
	@param			amount	 : the number of splitting
	@return 				 : None
	"""
	player = BigWorld.player()
	player.splitItemIV( index, amount )

def changePassword( password ):
	"""
	@type			password : string
	@param			suitIndex : the password string
	@return						: None
	"""
	pass

def settingPassword( password ):
	"""
	@type			password : string
	@param			suitIndex : the password string
	@return						: None
	"""
	pass

def hirePacks( packsIndex, timeStr ):
	#根据租赁背包组的索引和时间，向服务器请求相应值，并作相应判断
	"""
	@type			suitIndex : int
	@param			suitIndex : the packs index
	@type			timeStr	 : string
	@param			timeStr	 : the hire time
	@return 				 : None
	"""
	time = int( timeStr )
	hireMoney = getHireMoney( packsIndex, time )#根据不同组和时间计算相应租金
	player = BigWorld.player()
	if player.money < hireMoney:
		player.statusMessage( csstatus.MONEY_HIRE_NOT_ENOUGH )
		return
	# 在此向服务器端发送租赁请求，服务器做相应处理，比如计算剩余时间等
	remainTime = getRemain( packsIndex, timeStr )
	fireEvent( "EVT_ON_UPDATE_STORE_PACKS", packsIndex, remainTime )

def getHires( packsIndex ):
	# 根据背包组索引得到不同时间的不同租金
	"""
	@type			packsIndex : int
	@param			packsIndex : the packs index
	@return					: None
	"""
	pass

def isHasPassword( ):
# 确定仓库或者包裹是否有密码
	"""
	@type			id : int
	@param			id : the bank or the kitbag index
	@return				: bool
	"""
	return True

def isLocked( ):
#确定仓库或者包裹是否上锁
	"""
	@type			id : int
	@param			id : the bank or the kitbag index
	@return				: bool
	"""
	return True

def getPassword( ):
#获得仓库或者包裹的密码
	"""
	@type			id : int
	@param			id : the bank or the kitbag index
	@return				: int
	"""
	psw  = "123456" #临时做测试用
	return  psw

def freezeUnlock( ):
# 设置仓库或者包裹24小时不能解锁
	"""
	@type			id : int
	@param			id : the bank or the kitbag index
	@return				: None
	"""
	pass

def dropItemFromKitbag( srcBagIndex, gbIndex, packIndex ): #拖放普通物品到包裹位上
# 从物品栏中拖放一个物品到仓库中的某个背包位
	"""
	@type			srcBagIndex : int
	@param			srcBagIndex : the kitbag index
	@type			gbIndex : int
	@param			gbIndex : the package globel index
	@type			packIndex : int
	@param			packIndex : the target pack index
	@return				: None
	"""
	player = BigWorld.player()
	orderID = srcBagIndex * csdefine.KB_MAX_SPACE + gbIndex
	item = player.getItem_( orderID )
	amount = item.amount
	if item is None:
		player.statusMessage( csstatus.EQUIP_ANALYZE_NOT_EXIST )
		return
	storeBankItem( packIndex, srcBagIndex, gbIndex, amount )

def dropPackFromKitbag( srcBagIndex, index, packIndex ): # 拖放包裹到包裹位上
	player = BigWorld.player()
	orderID = srcBagIndex * csdefine.KB_MAX_SPACE + index
	item = player.getItem_( orderID )
	itemInfo = ObjectItem( item )
	amount = item.amount
	if item is None:
		player.statusMessage( csstatus.EQUIP_ANALYZE_NOT_EXIST )
		return
	fireEvent( "EVT_ON_UPDATE_STORE_PACK", packIndex, itemInfo )# 通知客户端更新

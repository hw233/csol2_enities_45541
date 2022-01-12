# -*- coding: gb18030 -*-
#
# $Id: Bank.py,v 1.19 2008-08-09 06:33:34 fangpengjun Exp $

from bwdebug import *
import BigWorld
import items
import csdefine
import csstatus
import csconst
import event.EventCenter as ECenter
from MessageBox import showMessage
from MessageBox import MB_YES_NO
from MessageBox import RS_YES
from config.client.msgboxtexts import Datas as mbmsgs
import ShareTexts
#from Time import Time


g_item = items.instance()

TIME_TO_GET_BANK_ITEMS = 1

class Bank:
	"""
	钱庄系统接口

	bankLockerStatus表示钱庄密码锁状态的数据，密码锁的状态可以方便由此数据查询得出，不需要再def中声明过多的数据。规则如下：
	bankLockerStatus位长为8，使用其字节模式右边的第一位来表示钱庄是否设置密码的状态，当位字节模式为0时表示不锁定，为1时表示锁定；
	使用右边第二位来表示钱庄是否锁定的状态数据，设置则为0，否则为1。右边第三、四位考虑以后扩展需要。
	使用其右边第五、六、七位来表示钱庄解锁密码失败次数数据，最多可以表示7次失败，即字节模式为111，bankLockerStatus右移4位操作即可得操作数据，
	每失败一次可在移位后进行+1的10进制运算。

		钱庄密码锁状态数据bankLockerStatus的状态如下（界面实现时可参考）：
		0000 0000:无密码状态
		0000 0001:有密码状态
		0000 0010:锁定状态
		0111 0000:钱庄解锁失败次数
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		self.Bank = None				# 钱庄物品数据
		self.bankMoney = 0					# 钱庄存储的金钱
		self._flag = False					# 钱庄数据接收状态
		self.entityID = -1
		self.bagIDList = []
		self.__pyMsgBox = None
#		self.bankBags = {}

		self.bankNameDict = {}			# 包裹位名字数据，key为包裹index，value为包裹名字
		self._openStyle = None 			#用来保存扩充仓库的方式的变量

	def _setDataFlag( self, flag ):
		"""
		设置钱庄数据接收状态

		type flag:	BOOL
		"""
		self._flag = flag


	def _getDataFlag( self ):
		"""
		获得钱庄数据接收状态
		"""
		return self._flag


	def enterBank( self, entityID ):
		"""
		Define method.
		提供给cell打开客户端界面的接口

		功能：打开界面并检查钱庄数据请求标志，根据标志决定是否向服务器请求数据
		"""
		self.entityID = entityID
		if not self._getDataFlag():
			self._setDataFlag( True )
			for i in xrange( len( self.bankNameList ) ):
				self.bagIDList.append( i )
			self.bagIDList.reverse()
			self.bank_requestBankBag()
		for i,j in enumerate( self.bankNameList ):
			self.bankNameDict[ i ] = j	# 这个数据是为了方便界面表现
			ECenter.fireEvent( "EVT_ON_BAG_NAME_UPDATED", i, self.bankNameDict[i] )
		ECenter.fireEvent( "EVT_ON_SHOW_STORE_WINDOW", entityID )

	def leaveBank( self ):
		"""
		退出仓库
		"""
		self.base.leaveBank()

	def bank_requestBankBag( self ):
		"""
		请求一批仓库商品
		"""
		length = len( self.bagIDList )
		if length > 0:
			self.base.bank_requestBankBag( self.bagIDList.pop() )
			BigWorld.callback( TIME_TO_GET_BANK_ITEMS, self.bank_requestBankBag )

	def bank_receiveBaseData( self, bagID, itemList ): 	# 更新仓库和里面的物品
		"""
		Define method.
		提供给base的给client发送钱庄物品数据的接口

		param bankBags:	钱庄中存储的物品数据
		type bankBags:	KITBAGS
		"""
		for item in itemList:
			order = item.order
			bankBagNum = order/csdefine.KB_MAX_SPACE
			ECenter.fireEvent( "EVT_ON_BANK_ADD_ITEM", bankBagNum, order, item ) # 更新各仓库的物品

	def hasEnoughItems( self, amount ):
		items = self.findItemsByIDFromNKCK( csdefine.ID_OF_ITEM_OPEN_BAG )
		count = 0
		for item in items:
			count += item.amount
		if count < amount:return False
		return True

	def requestOpenNextBag( self, isUseItemOpen):

		#@param isUseItemOpen： 是通过仓库界面还是直接点击金丝扩充仓库 0：仓库界面 1：点击金丝木
		# 这样做是因为策划要求在不同的方式下提示也不一样
		#@type boolean
		nextIndex = len( self.bankNameList )
		if nextIndex >= csconst.BANK_MAX_COUNT:
			self.statusMessage( csstatus.BANK_CANNOT_OPEN_MORE_BAG )
			return
		self._openStyle  = isUseItemOpen
		if self.hasEnoughItems( csconst.NEED_ITEM_COUNT_DICT[nextIndex] ):
			self.cell.bank_activateBag()
		else:
			self.noticeFailure()

	def getNextBagIndex( self):
		return len( self.bankNameList )

	def noticeFailure( self ):
		"""
		Exposed method.
		提供给base失败消息,因为某些原因，与noticeSuccess不能合并
		"""
		dialogID = csstatus.BANK_ITEM_NOT_ENOUGH_1
		if self._openStyle:
			dialogID = csstatus.BANK_ITEM_NOT_ENOUGH_2
		self.statusMessage( dialogID )
		self._openStyle = None		# 释放标记

	def noticeSuccess( self ):
		if self._openStyle:
			self.statusMessage( csstatus.BANK_KITBAG_OPEN_SUCCESS_2, len( self.bankNameList ) )
		else :
			self.statusMessage( csstatus.BANK_KITBAG_OPEN_SUCCESS_1 )

	def bank_activateBagSuccess( self ):
		"""
		Define method.
		激活钱庄储物箱成功
		"""
#		self.statusMessage( csstatus.BANK_ACTIVATE_SUCCESS )
		#bag = g_item.createDynamicItem( "070101005" )
		index = len( self.bankNameList )
		#self.bankBags[ index ] = bag
		self.bankNameList.append( "" )
		self.bankNameDict[ index ] = ""
		self.noticeSuccess( )
		self._openStyle = None
		ECenter.fireEvent( "EVT_ON_ACTIVATE_BANK_SUCCESS", index )

	def bank_bagNameUpdate( self, index, name ):
		"""
		Define method.
		包裹名更新函数
		"""
		DEBUG_MSG( "---->>>%i, %s" % ( index, name ) )
		#if self.bankNameDict.has_key( index ):
		#	DEBUG_MSG( "改名" )		# 改名
		#else:
		#	DEBUG_MSG( "新加包裹" )	# 新加了包裹
#		self.bankNameList.append( name )
		self.bankNameList[index] = name
		self.bankNameDict[ index ] = name
		ECenter.fireEvent( "EVT_ON_BAG_NAME_UPDATED", index, name )

	#------------------------------------往钱庄里存物品 BEGIN------------------------------
	def bank_storeItem2Order( self, kitbagNum, srcOrder, bankBagNum, dstOrder ):
		"""
		往钱庄里存储物品的接口，已知目标物品格

		param kitbagNum:背包包裹位号
		type kitbagNum:	UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		param bankBagNum:钱庄包裹位号
		type bankBagNum:	UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		"""
		srcOrder = kitbagNum * csdefine.KB_MAX_SPACE + srcOrder
		#dstOrder = bankBagNum * csdefine.KB_MAX_SPACE + dstOrder
		item = self.getItem_( srcOrder )
		if item is None:
			ERROR_MSG( "------>>>can not find item.order:%i." % srcOrder )
			return
		if not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return
		self.cell.bank_storeItem2Order( srcOrder, dstOrder, self.entityID )

	def bank_storeItem2Bank( self, kitbagNum, srcOrder ):
		"""
		往钱庄里存储物品的接口，不指定包裹位与目标格子，在钱庄里查找第一个空位

		param kitbagNum:背包包裹位号
		type kitbagNum:	UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		param bankBagNum:钱庄包裹位号
		type bankBagNum:	UINT8
		"""
		srcOrder = kitbagNum * csdefine.KB_MAX_SPACE + srcOrder
		item = self.getItem_( srcOrder )
		if item is None:
			ERROR_MSG( "------>>>can not find item.order:%i." % srcOrder )
			return
		if not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return
		self.cell.bank_storeItem2Bank( srcOrder, self.entityID )

	def bank_storeItem2Bag( self, kitbagNum, srcOrder, bankBagNum ):
		"""
		往钱庄里存储物品的接口，仅指定了包裹位

		param kitbagNum:背包包裹位号
		type kitbagNum:	UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		param bankBagNum:钱庄包裹位号
		type bankBagNum:	UINT8
		"""
		srcOrder = kitbagNum * csdefine.KB_MAX_SPACE + srcOrder
		item = self.getItem_( srcOrder )
		if item is None:
			ERROR_MSG( "------>>>can not find item.order:%i." % srcOrder )
			return
		if not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return
		self.cell.bank_storeItem2Bag( srcOrder, bankBagNum, self.entityID )

	# ------------------------往钱庄里存物品 END------------------------------------------------------------

	#------------------------------------物品从钱庄取出 BEGIN-----------------------------
	def bank_fetchItem2Order( self, srcOrder, kitbagNum, dstOrder ):
		"""
		左键拖钱庄物品栏物品到确定的背包物品格

		param bankBagNum:钱庄包裹位号
		type bankBagNum:	UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		param kitbagNum:背包包裹位号
		type kitbagNum:	UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		"""
		#srcOrder = bankBagNum * csdefine.KB_MAX_SPACE + srcOrder
		dstOrder = kitbagNum * csdefine.KB_MAX_SPACE + dstOrder
		self.cell.bank_fetchItem2Order( srcOrder, dstOrder, self.entityID )


	def moveItemCB( self, bankBagNum, srcOrder, dstBagNum, dstOrder ):
		"""
		Define method.
		交换两个道具的位置。
		"""
		ECenter.fireEvent( "EVT_ON_BANK_SWAP_ITEMS", bankBagNum, srcOrder, dstBagNum, dstOrder )




	def bank_fetchItem2Kitbags( self, bankBagNum, srcOrder ):
		"""
		从钱庄里取出物品的接口，不指定包裹位与目标格子，在背包里查找第一个空位

		param bankBagNum:钱庄包裹位号
		type bankBagNum:UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		"""
		self.cell.bank_fetchItem2Kitbags( srcOrder, self.entityID )
	#------------------------------------物品从钱庄取出 END------------------------------

	def bank_destroyItem( self, bankBagNum, order ):
		"""
		销毁物品的客户端接口

		param kitbagNum:钱庄包裹位号
		type kitbagNum:UINT8
		param order:	格子号
		type order:	INT16
		"""
		#order = bankBagNum * csdefine.KB_MAX_SPACE + order
		self.cell.bank_destroyItem( order, self.entityID )

	def bank_moveItem( self, srcBankBagNum, srcOrder, dstBankBagNum, dstOrder ):
		"""
		在同一个包裹中移动物品的接口

		param bankBagNum:钱庄包裹位号
		type bankBagNum:UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		param srcOrder:	格子号
		type srcOrder:	INT16
		"""
		#srcOrder = srcBankBagNum * csdefine.KB_MAX_SPACE + srcOrder
		#dstOrder = dstBankBagNum * csdefine.KB_MAX_SPACE + dstOrder
		self.cell.bank_moveItem( srcOrder, dstOrder, self.entityID )

	def bank_storeMoney( self, money ):
		"""
		玩家往钱庄存储金钱的接口

		param money：玩家要往钱庄存的金钱数目
		type money：UINT32
		"""
		if self.bankMoney >= csconst.BANK_MONEY_LIMIT:		 #如果钱庄的金钱数量已到上限 那么返回
			self.statusMessage( csstatus.BANK_MONEY_LIMIT )
			return
		elif self.bankMoney + money >= csconst.BANK_MONEY_LIMIT: #如果钱庄的金钱加上要存的钱超过上限 那么发出消息
			self.statusMessage( csstatus.BANK_MONEY_LIMIT )
			return
		if self.money < money :
			self.statusMessage( csstatus.BANK_MONEY_NOT_ENOUGH_TO_STORE )
			return
		self.cell.bank_storeMoney( money, self.entityID )

	def bank_fetchMoney( self, money ):
		"""
		玩家从钱庄取出金钱的接口

		param money：玩家要取出的金钱数目
		type money：UINT32
		"""

		if self.testAddMoney( money ) > 0:	#如果玩家携带的金钱数量加上取出的钱已到上限
			self.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )
			if self.ifMoneyMax():	#如果玩家身上的金钱已经超过了上限 返回
				return

		self.cell.bank_fetchMoney( money, self.entityID )


	def set_bankMoney( self, oldValue ):
		"""
		当钱庄金钱属性改变时被调用
		"""
#		pass	# 参照GUIFacade.onRoleMoneyChanged( oldValue, self.money )
		ECenter.fireEvent( "EVT_ON_ROLE_BANK_MONEY_CHANGED", oldValue, self.bankMoney )

	def bank_splitItemUpdate( self, bankBagNum, order, amount ):
		"""
		Define method.
		拆分一个钱庄物品的更新函数,更新源格子物品的数目

		param bankBagNum:钱庄包裹位号
		type bankBagNum:UINT8
		param order:	格子号
		type order:		INT16
		param amount:	物品数目
		type amount:	INT16
		"""
		#self.bankBags[bankBagNum][order].setAmount( amount )
		ECenter.fireEvent( "EVT_ON_BANK_SPLIT_ITEMS", bankBagNum, order, amount )


	def bank_storeItemUpdate( self, item ):
		"""
		Define method.
		背包往钱庄存储一个物品的更新函数

		param bankBagNum:钱庄包裹位号bank_storeMoney
		type bankBagNum:UINT8
		param order:	格子号
		type order:		INT16
		param item:	物品实例
		type item:	ITEM
		"""
		# 保存物品信息
		order = item.order
		bankBagNum = order/csdefine.KB_MAX_SPACE
		ECenter.fireEvent( "EVT_ON_BANK_ADD_ITEM", bankBagNum, order, item )		# 通知界面

	def bank_delItemUpdate( self, bankBagNum, order ): # 删除原来仓库中的包裹物品
		"""
		Define method.
		删除一个钱庄物品的更新函数
		被base调用

		param bankBagNum:	数据改变的包裹号
		type bankBagNum:	UINT8
		param order:	格子号
		type order:		INT16
		"""
		#order = order % csdefine.KB_MAX_SPACE
		ECenter.fireEvent( "EVT_ON_BANK_UPDATE_ITEM", bankBagNum, order, None )# 删除特定仓库内的某一物品

	# ------------------------------------------钱庄密码锁功能 BEGIN----------------------------------------
		# ------------------call by UI----------------------------------
	def bank_setPassword( self, srcPassword, password ):
		"""
		设置、修改钱庄密码都使用此接口。钱庄密码为空时，srcPassword值为"",修改密码时srcPassword值为 玩家的旧密码

		param srcPassword:		钱庄原密码,
		type srcsrcPassword:	STRING
		param password:	玩家输入的密码
		type password:	STRING
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		self.cell.bank_setPassword( srcPassword, password, self.entityID )

	def bank_lock( self ):
		"""
		给钱庄上锁，在玩家设置了密码且还没有对钱庄上锁的前提下，才满足此接口的使用条件

		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		self.cell.bank_lock( self.entityID )

	def bank_unlock( self, srcPassword ):
		"""
		给钱庄解锁，在玩家设置了钱庄密码且给钱庄上锁的前提下，才满足此接口的使用条件。
		注意：解锁的操作如果在本次登陆期间失败3次，24小时内不允许钱庄解锁操作。

		param srcPassword:		钱庄原密码,
		type srcsrcPassword:	STRING
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		self.cell.bank_unlock( srcPassword, self.entityID )

	def bank_clearPassword( self, srcPassword ):
		"""
		给钱庄永久解锁，玩家已经给钱庄设置了密码的前提下，此接口清除玩家设置的密码，把钱庄密码置为空。
		注意：永久解锁的操作如果在本次登陆期间失败3次，24小时内不允许钱庄解锁操作。

		param srcPassword:		钱庄原密码,
		type srcsrcPassword:	STRING
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		self.cell.bank_clearPassword( srcPassword, self.entityID )

	# -----------------------notify UI-------------------------------------------------
	def _isBankLocked( self ):
		"""
		验证钱庄是否被锁定
		"""
		return ( self.bankLockerStatus >> 1 ) & 0x01 == 1	# 表示钱庄是否被锁定与否状态位是否为1

	def set_bankLockerStatus( self, oldValue ):
		"""
		钱庄密码锁状态更新函数的自动更新函数，bankLockerStatus数据仅用来更新钱庄密码锁的状态，不要根据此数据通知玩家解锁或上锁成功
		"""
		ECenter.fireEvent( "EVT_ON_BANKLOCK_STATUAS_CHANGE", self.bankLockerStatus )
		# 通知界面，wsf

	def set_bankUnlockLimitTime( self, oldValue ):
		"""
		钱庄解锁限制时间的自动通知函数
		"""
		if self.bankUnlockLimitTime > 0:
			# 通知界面，因为如果bankUnlockLimitTime > 0，说明bankUnlockLimitTime是第一次设置，需要通知玩家他的行为受限了，wsf
			ECenter.fireEvent( "EVT_ON_BANKLOCK_TIME_CHANGE", self.bankUnlockLimitTime )

	def bank_lockerNotify( self, flag, remainTime ):
		"""
		Define method.
		钱庄密码锁通知函数

		if flag == 0: 设置钱庄密码成功的通知
		if flag == 1: 钱庄密码锁更改成功的通知
		if flag == 2: 输错解锁密码通知
		if flag == 3: 输错旧密码的通知
		if flag == 4: 给钱庄上锁成功的通知
		if flag == 5: 给钱庄解锁成功的通知
		if flag == 6: 已经输错三次密码
		if flag == 7: 成功永久解锁

		type flag:	UINT8
		"""
		ECenter.fireEvent( "EVT_ON_BANKLOCK_FLAG_CHANGE", flag, remainTime )

	def bank_onConfirmForceUnlock( self ) :
		"""
		Define method.
		强制解锁背包确认
		"""
		def confirmUnlock( result ) :
			if result == RS_YES :
				self.cell.bank_onForceUnlock()
		# 强制解锁背包需要%s，解锁后密码将被清空，你确定要申请吗？
		needTime = csconst.BANK_FORCE_UNLOCK_LIMIT_TIME
		needHours = needTime / 3600
		needMinutes = needTime % 3600 / 60
		needSeconds = needTime % 60
		needTimeText = ""
		if needHours :
			needTimeText += "%d%s" % ( needHours, ShareTexts.CHTIME_HOUR )
		if needMinutes :
			needTimeText += "%d%s" % ( needMinutes, ShareTexts.CHTIME_MINUTE )
		if needSeconds :
			needTimeText += "%d%s" % ( needSeconds, ShareTexts.CHTIME_SECOND )
		msg = mbmsgs[0x0e81] % needTimeText
		if self.__pyMsgBox is not None:
			self.__pyMsgBox.visible = False
			self.__pyMsgBox = None
		self.__pyMsgBox = showMessage( msg, "", MB_YES_NO, confirmUnlock )

	# ------------------------------------------钱庄密码锁功能 END----------------------------------------

	#--------------------以下功能由于界面的变化已经不用-----------------------
	def bank_moveItem2Bag( self, srcBankBagNum, srcOrder, dstBankBagNum ):
		"""
		在钱庄中 左键拖动物品到包裹位包裹中的接口

		param srcBankBagNum:钱庄包裹位号
		type srcBankBagNum:UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		param dstBankBagNum:钱庄包裹位号
		type dstBankBagNum:UINT8
		"""
		#srcOrder = srcBankBagNum * csdefine.KB_MAX_SPACE + srcOrder
		self.cell.bank_moveItem2Bag( srcOrder, dstBankBagNum, self.entityID )

	# -------------------------放置包裹 BEGIN----------------------------------
	def bank_bankLayBank( self, srcBankBagNum, srcOrder, dstBankBagNum ):
		"""
		从玩家当前钱庄物品栏往钱庄包裹位放置包裹的接口

		param srcBankBagNum:玩家钱庄当前包裹号
		type srcBankBagNum:	UINT8
		param srcOrder:		玩家钱庄当前包裹的格子号
		type srcOrder:		INT16
		param dstBankBagNum:玩家钱庄的包裹位
		type dstBankBagNum:	UNIT8
		"""
		pass
		#elf.cell.bank_bankLayBank( srcBankBagNum, srcOrder, dstBankBagNum, self.entityID )


	def bank_kitbagsLayBank( self, kitbagNum, srcOrder, bankBagNum ):
		"""
		从玩家当前背包栏往钱庄包裹位放置包裹的接口
		param kitbagNum:	玩家背包当前包裹号
		type kitbagNum:		UINT8
		param srcOrder:		玩家背包当前包裹的格子号
		type srcOrder:		INT16
		param bankBagNum:	玩家钱庄的包裹位
		type bankBagNum:	UNIT8
		"""
		pass
		#srcOrder = kitbagNum * csdefine.KB_MAX_SPACE + srcOrder
		#self.cell.bank_kitbagsLayBank( kitbagNum, srcOrder, bankBagNum, self.entityID )

	# -------------------------放置包裹 END----------------------------------
	def bank_changeGoldToItem( self, goldValue ):
		"""
		兑换元宝票
		"""
		if self.gold < goldValue:
			self.statusMessage( csstatus.GOLD_NO_ENOUGH )
			return
		if self.getNormalKitbagFreeOrder() == -1:
			self.statusMessage( csstatus.KITBAG_IS_FULL )
			return
		if goldValue < 0 and goldValue > 20000:
			self.statusMessage( csstatus.GOLD_TICKET_MAX_CHANGE )
			return
		self.base.bank_changeGoldToItem( goldValue )

	def openGoldToItemInterface( self ):
		"""
		define method
		通知打开元宝票界面
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_OPEN_GOLD_CHANGE" )


	#------------------------------------------------------------------------
#
# $Log: not supported by cvs2svn $
# Revision 1.18  2008/08/08 07:19:41  fangpengjun
# no message
#
# Revision 1.17  2008/08/08 03:14:06  fangpengjun
# 王树枫重新调整了仓库系统
#
# Revision 1.16  2008/07/07 11:06:29  wangshufeng
# 钱庄界面调整，界面使用了物品在钱庄中的全局order，并调整此模块数据。
# method modify:onBankBagsInfoReceive,修正了钱庄包裹数据更新不正确的bug。
#
# Revision 1.15  2008/05/30 03:04:21  yangkai
# 装备栏调整引起的部分修改
#
# Revision 1.14  2008/05/13 06:05:38  wangshufeng
# method modify:bank_splitItem,去掉目标包裹和目标格子参数，查找背包第一个空位放置拆分后的物品。
#
# Revision 1.13  2008/05/04 06:43:32  zhangyuxing
# no message
#
# Revision 1.12  2008/04/01 05:17:55  zhangyuxing
# 加入和仓库对话状态
#
# Revision 1.11  2008/03/28 01:13:05  zhangyuxing
# 修改 获得 cell.bank_requireData 的方式
#
# Revision 1.10  2008/02/04 00:57:15  zhangyuxing
# 修改仓库物品获得方式
#
# Revision 1.9  2008/01/22 03:58:51  wangshufeng
# 修正代码错误：self.kitbagsLockerStatus —〉self.bankLockerStatus，
#
# Revision 1.8  2008/01/15 01:47:44  kebiao
# onUpdateSkill to onUpdateNormalSkill
#
# Revision 1.7  2007/12/24 01:10:14  fangpengjun
# no message
#
# Revision 1.6  2007/12/22 10:00:26  fangpengjun
# 添加发送给客户端消息的事件
#
# Revision 1.4  2007/12/06 06:56:39  huangyongwei
# 将 updateSkill 改为 onUpdateSkill
#
# Revision 1.3  2007/12/05 06:45:06  wangshufeng
# no message
#
# Revision 1.2  2007/11/26 02:14:20  wangshufeng
# interface modify:去除bank_receiveCellData接口的多余参数bankMoney
#
# 增加了钱庄密码锁功能
#
# Revision 1.1  2007/11/14 02:54:38  wangshufeng
# 添加了钱庄系统
#
#
#
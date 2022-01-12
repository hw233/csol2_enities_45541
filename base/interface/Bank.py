# -*- coding: gb18030 -*-
#
# $Id: Bank.py,v 1.21 2008-08-08 03:08:13 fangpengjun Exp $


import cschannel_msgs
import ShareTexts as ST
import items
import ItemTypeEnum
import csdefine
import csstatus
import csconst
import sys
from bwdebug import *
from MsgLogger import g_logger
from ChatProfanity import chatProfanity

g_item = items.instance()


class Bank:
	"""
	钱庄系统接口
	"""
	def __init__( self ):
		"""
		"""
		# self.bankBags 定义在def文件中
		self._lastTote = 0
		self._isOperateBank = False # 打开仓库是否进行了操作
		if not self.bankNameList:	# 这段代码是为了兼容钱庄未改版前的创建的玩家wsf,13:40 2008-8-7
			self.bankNameList.append( "" )

	def bank_requestBankBag( self, itemIndex,):
		"""
		Exposed method
		"""
		if itemIndex >= len( self.bankNameList ):	# 如果玩家没有此储物箱
			return
		bankItemList = self._getBankItems( itemIndex )
		self.client.bank_receiveBaseData(  itemIndex, bankItemList )

	def bank_activateBag( self, amount ):
		"""
		Define method.
		激活包裹
		"""
		#item = g_item.createDynamicItem( "070101005" )
		bagIndex = len( self.bankNameList )
		if bagIndex >= csconst.BANK_MAX_COUNT:
			self.client.onStatusMessage( csstatus.BANK_CANNOT_OPEN_MORE_BAG, "" )
#			ERROR_MSG( "玩家( %s )不能再拥有更多的储物箱了。" %( self.getName() ) )
			return
		#self.bankBags[ count ] = item
		elif amount < csconst.NEED_ITEM_COUNT_DICT[bagIndex]:
			self.client.noticeFailure()
			return
		self.bankNameList.append( "" )
		self.cell.onBank_activateBagSuccess( csconst.NEED_ITEM_COUNT_DICT[bagIndex] )
		self.client.bank_activateBagSuccess()
		# 仓库扩充日志
		try:
			g_logger.bankExtendLog( self.databaseID, self.getName(), bagIndex, bagIndex*csconst.BANKBAG_NORMAL_ORDER_COUNT )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	#------------------------------------钱庄包裹的操作 BEGIN-----------------------------
	def _addItem2Order( self, srcOrder, dstOrder, srcItem ):
		"""
		description:把一个物品放到指定包裹的格子中，被bank_storeItem2Order调用，
					参数请参考bank_storeItem2Order,添加情况有三种：
					1.目标位置有物品且可以和源物品叠加：叠加操作
					2.目标位置有物品且不可以和源物品叠加：交换操作
					3.目标位置没有物品：添加操作
		param kitbag:	包裹实例
		type kitbag:	KITBAG
		param order:	格子号
		type order:		INT16
		"""
		if srcItem is None :
			return False
		dstItem = self.bankItemsBag.getByOrder( dstOrder )
		if dstItem is None:			# 情况3
			addResult = self._addItemByOrder( srcItem, dstOrder )
			if addResult == csdefine.KITBAG_ADD_ITEM_SUCCESS:
				self.cell.bank_storeItemSuccess01( srcOrder )
				return True
			return False

		if dstItem.isFrozen():
			WARNING_MSG( "包裹被锁定。" )
			return False

		if dstItem.id == srcItem.id and dstItem.isBinded() != srcItem.isBinded() and dstItem.getAmount() < dstItem.getStackable():
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False

		if dstItem.id == srcItem.id and dstItem.getAmount() < dstItem.getStackable():	# 情况1
			stackable = srcItem.getStackable()
			srcAmount = srcItem.getAmount()
			dstAmount = dstItem.getAmount()
			stackAmount = min( stackable - dstAmount, srcAmount )
			dstItem.setAmount( dstAmount + stackAmount )
			self.client.bank_storeItemUpdate( dstItem )
			srcAmount = srcAmount - stackAmount
			if srcAmount:	# 在目标位置叠加后还有剩余，放回背包
				srcItem.setAmount( srcAmount )
				self.client.bank_storeItemUpdate( srcItem )
				self.cell.bank_storeItemSuccess02( srcOrder, srcItem )
			else:
				self.cell.bank_storeItemSuccess01( srcOrder )
			return True

		swapSucc = self._swapItem( dstOrder, srcItem )	# 情况2
		if swapSucc:
			self._isOperateBank = True
			self.cell.bank_storeItemSuccess02( srcOrder, dstItem )
			return True
		return False

	def _swapItem( self, dstOrder, srcItem ):
		"""
		description:将cell发来的物品和银行包裹的物品叠加
		@param itemInstance: 继承于CItemBase的自定义道具实例
		@type  itemInstance: CItemBase
		@return:             成功则返回成功状态码，如果成功，则会自动通知client，失败则返回原因
		@rtype:              INT8
		"""
		if self.bankItemsBag.removeByOrder( dstOrder ):
			addResult = self._addItemByOrder( srcItem, dstOrder )
			if addResult == csdefine.KITBAG_ADD_ITEM_SUCCESS:
				return True
		return False

	def _addItemByOrder( self, itemInstance, orderID ):
		"""
		description:往指定位置加入某个道具实例
		@param itemInstance: 继承于CItemBase的自定义道具实例
		@type  itemInstance: CItemBase
		@param orderID: 道具在背包里的位置
		@type  orderID: INT16
		@return: 返回操作的状态码
		@rtype:  INT8
		"""
		# 此函数用做将物品实例加进银行包裹
		addResult = self.bankItemsBag.add( orderID, itemInstance )
		if not addResult:				# 返回底层的状态，暂时由于底层只返回0或1，所以才这么做
			return csdefine.KITBAG_ADD_ITEM_FAILURE
		self.client.bank_storeItemUpdate( itemInstance )
		try:
			g_logger.bankStoreLog( self.databaesID, self.getName(), itemInstance.uid, itemInstance.name(), itemInstance.getAmount() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		
		self._isOperateBank = True
		return csdefine.KITBAG_ADD_ITEM_SUCCESS

	#------------------------------------钱庄包裹的操作 END-----------------------------

	#------------------------------------往钱庄里存物品 BEGIN-----------------------------
	def bank_storeItem2Order( self, srcOrder, srcItem, dstOrder ):
		"""
		Define method.
		description:往钱庄包裹里指定的格子存储物品的接口
		param srcOrder:	格子号
		type srcOrder:	INT16
		param item:		往钱庄里存储的物品
		type item:		ITEM
		param dstOrder:	格子号
		type dstOrder:	INT16
		"""
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		bankBagNum = dstOrder / csdefine.KB_MAX_SPACE
		if bankBagNum >= len( self.bankNameList ):
			HACK_MSG( "玩家(%s)钱庄包裹位参数(%i)错。" % ( self.getName(), bankBagNum ) )
			self.cell.bank_storeItemFailed( srcOrder )
			return

		if not self._addItem2Order( srcOrder, dstOrder, srcItem ):	# 添加失败
			self.cell.bank_storeItemFailed( srcOrder )
			return

	def bank_storeItem2Bank( self, srcOrder, item ):
		"""
		Define method.
		往钱庄里存储物品的接口，不指定包裹位与目标格子，在钱庄里查找第一个空位
		@param dstOrder:	格子号
		@type dstOrder:	INT16
		@param item:		往钱庄里存储的物品
		@type item:		ITEM
		@param bankBagNum:钱庄包裹位号
		@type bankBagNum:UINT8
		"""
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		if item.getStackable() > 1:					# 如果是可叠加物品
			if self._stackableInBank( item ):		# 查找钱庄里的同类可叠加物品 叠加
				self.cell.bank_storeItemSuccess01( srcOrder )
				return
		# 查找钱庄里的空位
		orderID = self._findFreeOrder()
		if orderID != -1:
			result = self._addItemByOrder( item, orderID )
			if result == csdefine.KITBAG_ADD_ITEM_SUCCESS:
				self.cell.bank_storeItemSuccess01( srcOrder )
			else:
				ERROR_MSG("当向背包里增加一个道具时失败")
				self.cell.bank_storeItemFailed( srcOrder )
		else:	# 物品存储失败
			self.statusMessage( csstatus.BANK_IS_FULL )
			self.cell.bank_storeItemFailed( srcOrder )
			return

	def bank_storeItem2Bag( self, srcOrder, item, bankBagNum ):
		"""
		Define method.
		往钱庄里存储物品的接口，仅指定了包裹位
		由于界面已经改变，此功能已经不需要，暂时屏蔽
		param dstOrder:	格子号
		type dstOrder:	INT16
		param item:		往钱庄里存储的物品
		type item:		ITEM
		param bankBagNum:钱庄包裹位号
		type bankBagNum:UINT8
		"""
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		if bankBagNum >= len( self.bankNameList ):
			HACK_MSG( "玩家(%s)钱庄包裹位参数(%i)错。" % ( self.getName(), bankBagNum ) )
			self.cell.bank_storeItemFailed( srcOrder )
			return
		if item.getStackable() > 1:							# 如果是可叠加物品
			if self._stackableInBag( item, bankBagNum ):	# 叠加成功
				self.cell.bank_storeItemSuccess01( srcOrder )
				return
		order = self.__getFreeOrder( bankBagNum )
		if order == -1:
			self.cell.bank_storeItemFailed( srcOrder )
			self.statusMessage( csstatus.BANK_CURRENT_BAG_FULL )
			return
		if self._addItemByOrder( item, order ) == csdefine.KITBAG_ADD_ITEM_SUCCESS:
			self.cell.bank_storeItemSuccess01( srcOrder )
			#self.cell.bank_storeItemFailed( srcOrder )
			return

	def _stackableInBag( self, itemInstance, bankBagID ):
		"""
		在包裹中对一个可叠加物品叠加操作
		"""
		currtotal = 0
		stackable = itemInstance.getStackable()
		r = []
		for item in self._getBankItems( bankBagID ):
			if item.id == itemInstance.id and item.isBinded() == itemInstance.isBinded():	# 叠加时，必须是绑定类型一样的物品才能叠加。18:01 2009-2-16，wsf
				r.append( item )
		if len( r ) == 0: return False
		#获得总数
		for item in r:
			# like as: c += a < b ? a : b，做这个检查的原因是避免测试时手动设置多于stackable数量的物品产生判断错误
			currtotal += item.getAmount() < stackable and item.getAmount() or stackable
		val = len( r ) * stackable - currtotal		# 获取还可以叠加的数量
		val1 = itemInstance.getAmount()				# 获取这个物品的数量
		if val < val1 : return False
		for item in r :
			if val1 <= 0 : break
			amount = stackable - item.getAmount()
			if amount > 0:
				if amount > val1:
					item.setAmount( item.getAmount() + val1 )
					self.client.bank_storeItemUpdate( item )
					return True
				else:
					item.setAmount( stackable )
					self.client.bank_storeItemUpdate( item )
					val1 -= amount
		return True


	#------------------------------------往钱庄里存物品 END--------------------------------


	#------------------------------------物品从钱庄取出 BEGIN------------------------------
	def bank_fetchItemFailed( self, itemOrder ):
		"""
		Define method.
		存储物品到钱庄失败

		@param itemOrder : 没存储成功的物品order
		@type itemOrder : INT16
		"""
		item = self.bankItemsBag.getByOrder( itemOrder )
		if item is None:
			ERROR_MSG( "player( %s ) can not find item( order : %i )." % ( self.getName(), itemOrder) )
		else:
			item.unfreeze()

	def bank_fetchItem2Order( self, srcOrder, dstOrder ):
		"""
		左键拖钱庄物品栏物品到确定的背包物品格

		param dstOrder:	格子号
		type dstOrder:	INT16
		param kitbagNum:背包包裹位号
		type kitbagNum:	UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		"""
		bankBagNum = srcOrder / csdefine.KB_MAX_SPACE
		if bankBagNum >= len( self.bankNameList ):
			return

		item = self.bankItemsBag.getByOrder( srcOrder )
		if item is None:
			DEBUG_MSG( "玩家（%s）钱庄位置（bankBagNum(%i),order(%i)）不存在物品。" % ( self.getName(), bankBagNum, srcOrder ) )
			return
		if item.isFrozen():
			DEBUG_MSG( "玩家（%s）钱庄位置（bankBagNum(%i),order(%i)）不存在物品。" % ( self.getName(), bankBagNum, srcOrder ) )
			return
		item.freeze()
		self.cell.bank_fetchItem2OrderCB( dstOrder, item.copy(), srcOrder )

	def bank_fetchItem2Kitbags( self, srcOrder ):
		"""
		从钱庄里取出物品的接口，不指定包裹位与目标格子，在背包里查找第一个空位
		param kitbagNum:钱庄包裹位号
		type kitbagNum:UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		bankBagNum = srcOrder / csdefine.KB_MAX_SPACE
		item = self.bankItemsBag.getByOrder( srcOrder )
		if item is None:
			HACK_MSG( "物品不存在。" )
			return
		if item.isFrozen():
			WARNING_MSG( "物品被锁定" )
			return
		item.freeze()
		self.cell.bank_fetchItem2KitbagsCB( srcOrder, item.copy() )

	def bank_fetchItemSuccess01( self, dstOrder ):
		"""
		Define method.
		存储一个物品成功， base解锁并删除物品
		"""
		bankBagNum = dstOrder / csdefine.KB_MAX_SPACE
		dstItem = self.bankItemsBag.getByOrder( dstOrder )
		if dstItem is None:
			return
		self.bankItemsBag.removeByOrder( dstOrder )
		self.client.bank_delItemUpdate( bankBagNum, dstOrder )
		self.statusMessage( csstatus.CIB_MSG_FETCH_ITEMS_FROM_BANK, dstItem.name(),dstItem.amount )
		try:
			g_logger.bankTakeLog( self.databaseID, self.getName(), dstItem.uid, dstItem.name(), dstItem.getAmount() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def bank_fetchItemSuccess02( self, dstOrder, item ):
		"""
		Define method.
		背包从钱庄取一个物品的回调。
		背包中叠加一个物品有剩余，或钱庄与背包目标格子交换物品，把 剩余物品 或 交换的物品 放回钱庄
		"""
		bankBagNum = dstOrder / csdefine.KB_MAX_SPACE
		dstItem = self.bankItemsBag.getByOrder( dstOrder )
		if self.bankItemsBag.removeByOrder( dstOrder ):
			self._addItemByOrder( item, dstOrder )
			if dstItem.id == item.id:
				self.statusMessage( csstatus.CIB_MSG_FETCH_ITEMS_FROM_BANK, dstItem.name(),dstItem.amount-item.amount )
			else:
				self.statusMessage( csstatus.CIB_MSG_FETCH_ITEMS_FROM_BANK, dstItem.name(),dstItem.amount )
				self.statusMessage( csstatus.CIB_MSG_STORE_ITEMS_TO_BANK, item.name(),item.amount )
		try:
			g_logger.bankTakeLog( self.databaseID, self.getName(), dstItem.uid, dstItem.name(), dstItem.getAmount() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	#------------------------------------物品从钱庄取出 END------------------------------

	def bank_destroyItem( self, order ):
		"""
		Define method.
		销毁物品的接口
		param kitbagNum:钱庄包裹位号
		type kitbagNum:UINT8
		param order:	格子号
		type order:	INT16
		"""
		bankBagNum = order / csdefine.KB_MAX_SPACE

		#--销毁前的一些判断--
		if bankBagNum >= len( self.bankNameList ):
			HACK_MSG( "玩家(%s)钱庄包裹位参数(%i)错。" % ( self.getName(), bankBagNum ) )
			#self.cell.bank_unfreezeBag( kitbagNum )
			return
		item = self.bankItemsBag.getByOrder( order )
		if item is None:
			WARNING_MSG( "物品不存在。" )
			return
		if item.isFrozen():
			WARNING_MSG( "物品被锁定。" )
			return
		if not item.canDestroy():
			WARNING_MSG( "物品不可销毁。" )
			return
		#--------------------
		self._isOperateBank = True
		if self.bankItemsBag.removeByOrder( order ):
			self.client.bank_delItemUpdate( bankBagNum, order )
			try:
				g_logger.bankDestroyLog( self.databaseID, self.getName(), item.uid,item.name(),item.getAmount() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def bank_moveItem( self, srcOrder, dstOrder ):
		"""
		Define method.
		在同一个包裹中移动物品的接口
		param dstOrder:	格子号
		type dstOrder:	INT16
		param srcOrder:	格子号
		type srcOrder:	INT16
		"""
		if srcOrder == dstOrder:
 			return
		srcBankBagNum = srcOrder / csdefine.KB_MAX_SPACE
		dstBankBagNum = dstOrder / csdefine.KB_MAX_SPACE
		if srcBankBagNum != dstBankBagNum:
			return
		if srcBankBagNum >= len( self.bankNameList ):
			HACK_MSG( "玩家(%s)钱庄包裹位参数(%i)错。" % ( self.getName(), srcBankBagNum ) )
			return
		srcItem = self.bankItemsBag.getByOrder( srcOrder )
		if srcItem is None:
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return
		if srcItem.isFrozen():
			return

		dstItem = self.bankItemsBag.getByOrder( dstOrder )
		if dstItem and dstItem.isFrozen():
			return

		stack = srcItem.getStackable()
		srcAmount = srcItem.getAmount()
		if dstItem is None or dstItem.id != srcItem.id or dstItem.isBinded() != srcItem.isBinded() \
		or ( dstItem.getAmount() == stack or srcAmount == stack ) and srcAmount != dstItem.getAmount() :
			if self.bankItemsBag.swapOrder( srcOrder, dstOrder ) :
				self.client.moveItemCB( srcBankBagNum, srcOrder, srcBankBagNum, dstOrder )
				return
			else :
				ERROR_MSG(  "Swap false : src: %d <==> dst: %d " % ( srcOrder, dstOrder ) )
		dstAmount = dstItem.getAmount()
		if dstAmount < stack:	# 可叠加道具处理
			storeAmount = min( stack - dstAmount, srcAmount )
			dstItem.setAmount( dstAmount + storeAmount )				# 自动通知客户端
			srcAmount = srcAmount - storeAmount
			if srcAmount:	# 在目标位置叠加后还有剩余，放回源位置
				srcItem.setAmount( srcAmount )
				self.client.bank_storeItemUpdate( srcItem )
			elif self.bankItemsBag.removeByOrder( srcOrder ):	# 无剩余，删除源物品
				self.client.bank_delItemUpdate( srcBankBagNum, srcOrder )
			self.client.bank_storeItemUpdate( dstItem )

	def bank_unfreezeBag( self, bankBagNum ):

		"""
		Define method.
		Cell上检查条件不满足，则不进行卸下包裹 或 取出物品的操作，仅通过此接口解除base上被冻结的包裹
		"""
		pass
		#self.bankBags[bankBagNum].unfreeze()

	#-------------------------------------------------------------------------------------------
	def _findAllItemFromBank( self, itemKeyName ):
		"""
		从所有普通背包里找到所有与itemKeyName相同的物品

		@param itemKeyName: 表示每一类道具的唯一的道具类型
		@type  itemKeyName: STRING
		@return:	array of tuple as (kitOrder, orderID, itemData)
		@rtype:		array of tuple
		"""
		ar = []
		for i in xrange( csdefine.BANK_COMMON_ID, csdefine.BANK_COMMON_ID + csconst.BANK_MAX_COUNT ):
			if i < len( self.bankNameList ):
				for item in self._getBankItems( i ):
					if item.id == itemKeyName:
						ar.append( item )
		return ar

	def _getBankItems( self, bankBagID ):
		"""
		取得指定仓库背包的物品
		@return: [itemInstance, ...]
		"""
		start = bankBagID * csdefine.KB_MAX_SPACE
		end = bankBagID * csdefine.KB_MAX_SPACE + csdefine.KB_MAX_SPACE - 1
		return self.bankItemsBag.getDatasByRange( start, end )

	def _stackableInBank( self, itemInstance ):
		"""
		description:在钱庄中对一个可叠加物品叠加操作
		@param itemInstance:继承于CItemBase的自定义道具实例
		@type  itemInstance:CItemBase
		@return:	成功则返回True失败则返回False
		@rtype:		BOOL
		"""
		itemList = []
		currtotal = 0
		stackable = itemInstance.getStackable()
		#获得总数
		for e in self._findAllItemFromBank( itemInstance.id ):		# e like as ( kitOrder, orderID, itemData )
			# like as: c += a < b ? a : b，做这个检查的原因是避免测试时手动设置多于stackable数量的物品产生判断错误
			if e.isBinded() != itemInstance.isBinded():
				continue
			itemList.append( e )
			currtotal += e.getAmount() < stackable and e.getAmount() or stackable
		if itemList == []:return False
		val = len( itemList ) * stackable - currtotal	# 获取还可以叠加的数量
		val1 = itemInstance.getAmount()					# 获取这个物品的数量
		if val < val1:	return False
		for e in itemList:
			if val1 <= 0:break
			amount = stackable - e.getAmount()
			if amount > 0:
				if amount > val1:
					e.setAmount( e.getAmount() + val1 )
					self.client.bank_storeItemUpdate( e )
					return True
				else:
					e.setAmount( stackable )
					self.client.bank_storeItemUpdate( e )
					val1 -= amount
		return True

	def _findFreeOrder( self ):
		"""
		查找钱庄中第一个空位置

		@return: tuple as (kitOrder, orderID), return None while no free order
		@rtype:  tuple/None
		"""
		for i in xrange( csdefine.BANK_COMMON_ID, csdefine.BANK_COMMON_ID + csdefine.BANK_COUNT ):
			if i >= len( self.bankNameList ):
				 break
			# 这里暂时认为只要是能放到背包里的物品都能放到钱庄中，物品是否能被存储应该是物品本身的属性而不应该是包裹提供接口判断。wsf
			order = self.__getFreeOrder( i )
			if order != -1:
				return order
		return -1

	def __getFreeOrder( self, bankBagID ):
		"""
		取得指定仓库背包的空闲位置
		return: order
		"""
		# 取得指定背包的空闲位置
		if bankBagID >= len( self.bankNameList ):
			return -1
		startOrder = bankBagID * csdefine.KB_MAX_SPACE
		endOrder  = startOrder + csconst.BANKBAG_NORMAL_ORDER_COUNT
		for order in xrange( startOrder, endOrder ):
			if not self.bankItemsBag.orderHasItem( order ):
				return order
		return -1

	def bank_changeName( self, index, name ):
		"""
		Exposed method.

		@param index : 钱庄包裹号,UINT8
		@param name : 名字，STRING
		"""
		if index >= len( self.bankNameList ):
			HACK_MSG( "玩家(%s)钱庄包裹位参数(%i)错。" % ( self.getName(), index ) )
			return

		illegalWord = chatProfanity.searchNameProfanity( name )					# 验证名字是否合法
		if illegalWord is not None :
			self.statusMessage( csstatus.PET_RENAME_FAIL_ILLEGAL_WORD, illegalWord )
		elif len( name.decode( "gb2312" ) ) > csconst.PET_NAME_MAX_LENGTH :		# 名字是否超出限定长度
			self.statusMessage( csstatus.PET_RENAME_FAIL_OVERLONG )
		self.bankNameList[ index ] = name
		self.client.bank_bagNameUpdate( index, name )

	def bank_changeGoldToItem( self, goldValue ):
		"""
		Exposed method.
		银票替换为金元宝票物品
		"""
		if self.getUsableGold() < goldValue:
			self.statusMessage( csstatus.BANK_CHARGE_GOLD_LACK )
			return

		if goldValue < 0 and goldValue > 20000:
			self.statusMessage( csstatus.BANK_CHARGE_OVERTOP )
			return
		self.freezeGold( goldValue )
		self.cell.bank_changeGoldToItem( goldValue )

	def bank_changeGoldToItemCB( self, value, state ):
		"""
		Define method.
		元宝票兑换结果回调
		"""
		self._isOperateBank = True
		self.thawGold( value )
		if state:
			self.payGold( value, csdefine.CHANGE_GOLD_BANK_CHANGEGOLDTOITEM )

	def bank_item2Gold( self, value ):
		"""
		Define method.
		元宝票兑换成金元宝
		"""
		self._isOperateBank = True
		self.gainGold( value, csdefine.CHANGE_GOLD_BANK_ITEM2GOLD )

	
	def leaveBank( self ):
		"""
		exposed method
		退出仓库
		"""
		if self._isOperateBank:
			self.writeToDB()
		
		self._isOperateBank = False
#
# Revision 1.15  2008/07/02 05:38:59  songpeifang
# 加入了包裹的装备绑定功能，包括：1、钱庄物品栏->钱庄包位栏；2、钱庄物品栏->背包包位栏；3、背包物品栏->钱庄包裹栏。
#
# Revision 1.14  2008/05/30 03:03:49  yangkai
# 装备栏调整引起的部分修改
#
# Revision 1.13  2008/05/13 06:12:37  wangshufeng
# method modify:bank_splitItem,去掉目标包裹和目标格子参数，查找背包第一个空位放置拆分后的物品。
#
# Revision 1.12  2008/05/07 02:59:21  yangkai
# query( "stackable" ) -> getStackable()
#
# Revision 1.11  2008/04/28 06:07:12  wangshufeng
# method modify:bank_fetchItem2Order,修正钱庄位置的物品为None的bug
#
# Revision 1.10  2008/04/21 06:33:18  wangshufeng
# 修正客户端传递的物品格参数检察不正确的bug
#
# Revision 1.9  2008/04/03 06:33:07  phw
# KitbagBase::find2All()改名为find()，并更改返回值从原来的( order, toteID, itemInstance )改为itemInstance
# KitbagBase::findAll2All()改名为findAll()，并更改返回值从原来的( order, toteID, itemInstance )改为itemInstance
# 根据以上的变化，调整相关使用到以上接口的代码
#
# Revision 1.8  2008/02/04 00:56:52  zhangyuxing
# 修改仓库物品获得方式
#
# Revision 1.7  2007/12/22 09:51:55  fangpengjun
# if srcBag.swapOrder( srcOrder, dstOrder )
#   --------->
#          if bankBag.swapOrder( srcOrder, dstOrder ):
#
# Revision 1.6  2007/12/22 02:06:34  wangshufeng
# 交换2个物品位置使用moveItemCB函数通知客户端
#
# Revision 1.5  2007/12/11 06:41:43  wangshufeng
# 修正了：如果原包裹位存在包裹且包裹里有物品，往包裹位放置更大包裹时的代码错误
#
# Revision 1.4  2007/11/27 07:58:59  yangkai
# CIST_KITBAG --> ITEM_WAREHOUSE_KITBAG
# CIST_CASKET --> ITEM_WAREHOUSE_CASKET
#
# Revision 1.3  2007/11/26 02:10:39  wangshufeng
# interface modify:bank_requireItemData -> bank_requireData
# interface modify:bank_unlockBag -> bank_unfreezeBag
#
# Revision 1.2  2007/11/24 02:53:29  yangkai
# 物品系统调整，属性更名
# "wieldType" --> "eq_wieldType"
#
# Revision 1.1  2007/11/14 02:57:05  wangshufeng
# 添加了钱庄系统
#
#
#
#
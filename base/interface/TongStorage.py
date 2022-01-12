# -*- coding: gb18030 -*-

import time

from bwdebug import *
from MsgLogger import g_logger
import csdefine
import csconst
import csstatus
import Const
import ItemTypeEnum
import time

import items
g_item = items.instance()

EXTEND_LEVEL_LIST = [ 3, 5, 7, 9, 10 ]		# 仓库升级扩展空间的级别列表
REDUCE_LEVEL_LIST = [ 2, 4, 6, 8, 9 ]			# 仓库降级缩小空间的级别列表

DAY_FETCH_ITEM_LIMIT = 30000

ITEM_QUALITYS = [ ItemTypeEnum.CQT_WHITE, ItemTypeEnum.CQT_BLUE, ItemTypeEnum.CQT_GOLD, ItemTypeEnum.CQT_PINK, ItemTypeEnum.CQT_GREEN ]

RESET_LIMIT_POINT = [ 0, 0, 0 ]



class TongStorage:
	"""
	帮会仓库Interface
	"""
	def __init__( self ):
		"""
		"""
		self._lastTote = 0
		self.storageFreezeFlag = False	# 帮会仓库是否冻结的标记

		if self.storageLog is None:		# 初始化
			self.storageLog = []

		if self.playerFetchRecord is None:
			self.playerFetchRecord = {}

		if len( self.storageBagPopedom ) == 0:
			# 所有成员的默认权限为可取无限多的物品
			gradeFetchItemLimit = { csdefine.TONG_DUTY_MEMBER		:	0,\
									csdefine.TONG_DUTY_TONG			:	0,\
									csdefine.TONG_DUTY_DEPUTY_CHIEF	:	0,\
									csdefine.TONG_DUTY_CHIEF		:	DAY_FETCH_ITEM_LIMIT,\
									}

			tongStoragePopedom = { "bagID":csdefine.TONG_STORAGE_ONE,
									"bagName":"",
									"qualityUpLimit":ItemTypeEnum.CQT_GREEN,
									"qualityLowerLimit":ItemTypeEnum.CQT_WHITE,
									"fetchItemLimit":gradeFetchItemLimit,
									}
			self.storageBagPopedom.append( tongStoragePopedom )
		
		for item in self.storageBagPopedom:
			if len( set( item[ "fetchItemLimit" ].keys() ) & set( csdefine.TONG_DUTYS ) ) != len( csdefine.TONG_DUTYS ):
				self.storageBagPopedom.remove( item )
				
				gradeFetchItemLimit = { csdefine.TONG_DUTY_MEMBER	:	0,\
										csdefine.TONG_DUTY_TONG	:	0,\
										csdefine.TONG_DUTY_DEPUTY_CHIEF	:	0,\
										csdefine.TONG_DUTY_CHIEF	:	DAY_FETCH_ITEM_LIMIT,\
										}

				tongStoragePopedom = { "bagID":csdefine.TONG_STORAGE_ONE,
										"bagName":"",
										"qualityUpLimit":ItemTypeEnum.CQT_GREEN,
										"qualityLowerLimit":ItemTypeEnum.CQT_WHITE,
										"fetchItemLimit":gradeFetchItemLimit,
										}
				self.storageBagPopedom.append( tongStoragePopedom )

		self.storage_resetLimitTimer = self.addTimer( self._storageCalcTime( RESET_LIMIT_POINT[:] ) )
		now = time.time()
		if now - self.resetStorageLimitTime >= 24 * 60 * 60:	# 如果上一次重置时间是24小时之前,那么重置记录
			self.resetStorageLimit()


	def isStorageFrozen( self ):
		"""
		帮会仓库是否冻结
		"""
		return self.storageFreezeFlag


	def freezeStorage( self ):
		"""
		冻结帮会仓库,可能同时会有多个玩家操作仓库

		因为涉及到多服务器的数据交换,考虑异步问题,必须保证一个玩家的操作结束别的玩家才能操作
		"""
		self.storageFreezeFlag = True


	def unFreezeStorage( self ):
		"""
		解冻帮会仓库
		"""
		self.storageFreezeFlag = False


	def unFreezeStorageRemote( self ):
		"""
		Define method.
		远程方法，解冻帮会仓库
		"""
		self.unFreezeStorage()


	def _findFreeOrder( self ):
		"""
		获得仓库的第一个空位
		"""
		for i in xrange( csdefine.TONG_STORAGE_ONE, csdefine.TONG_STORAGE_ONE + csdefine.TONG_STORAGE_COUNT ):
			if i >= len( self.storageBagPopedom ): continue
			# 这里暂时认为只要是能放到背包里的物品都能放到钱庄中，物品是否能被存储应该是物品本身的属性而不应该是包裹提供接口判断。wsf
			#if not self.bankBags[i].canPlace( self, itemInstance ): continue
			order = self._findBagFreeOrder( i )
			if order == -1: continue
			return order	# orderID
		return -1


	def _findBagFreeOrder( self, bagID ):
		"""
		获得帮会仓库指定包裹的第一个空位
		"""
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID 参数错误,帮会名字:%s,bagID:%i." % ( self.playerName, bagID ) )
			return
		startOrder = bagID * csdefine.KB_MAX_SPACE
		for order in xrange( startOrder, startOrder + csconst.TONG_BAG_ORDER_COUNT ):
			if not self.storage.orderHasItem( order ):
				return order
		return -1

	def addStorageLog( self, playerDBID, operation, srcItem, bagID, date ):
		"""
		记录帮会仓库操作日志

		@param playerDBID : 玩家的DBID
		@type playerName : TongEntitiy.MemberInfos
		@operation : 玩家的操作:取出 或 存入
		@type srcItem : ITEM
		@param srcItem : 物品实例
		@type itemCount : INT
		@param bagID : 仓库的包裹id
		@type bagID : INT16
		@param date : 操作仓库的时间
		@type date : INT64
		"""
		memberINFO = self.getMemberInfos( playerDBID )
		logINFO = ( memberINFO.getName(), operation, srcItem.id, srcItem.getAmount(), bagID, date )
		self.storageLog.append( logINFO )
		if len( self.storageLog ) > csconst.TONG_STORAGE_LOG_COUNT:	# 只存储200条
			self.storageLog.pop( 0 )
		memberINFO.getBaseMailbox().client.tong_receiveStorageLog( logINFO )

		if operation == csdefine.TONG_STORAGE_OPERATION_ADD:
			try:
				g_logger.tongItemAddLog( self.databaseID, self.getName(), playerDBID, memberINFO.getName(), srcItem.getuid(), srcItem.id, srcItem.getAmount(), bagID )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
				
		elif operation == csdefine.TONG_STORAGE_OPERATION_MINUS:
			try:
				g_logger.tongItemRemoveLog( self.databaseID, self.getName(), playerDBID, memberINFO.getName(), srcItem.getuid(), srcItem.id, srcItem.getAmount(), bagID )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def requestStorageLog( self, playerDBID, count ):
		"""
		Define method.
		请求帮会仓库的log信息

		@param playerDBID : 玩家的dbid
		@type playerDBID : DATABASE_ID
		@param count : 请求的次数
		@type count : INT8
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return

		startIndex = count * 50
		if startIndex > len( self.storageLog ):
			return

		endIndex = startIndex + 50
		if endIndex > len( self.storageLog ):
			endIndex = len( self.storageLog )
		for index in xrange( startIndex, endIndex ):
			playerBase.client.tong_receiveStorageLog( self.storageLog[ index ] )


	def enterStorage( self, playerDBID ):
		"""
		Define method.
		玩家申请打开仓库，把仓库物品发给玩家客户端

		@param playerDBID : 玩家的databaseID
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return
		fetchRecord = self.getTodayStorageFetchRecord( playerDBID )
		playerBase.client.tong_enterStorage( self.storageBagPopedom, fetchRecord )


	def _getStorageBagItems( self, bagID ):
		"""
		取得仓库的物品
		@return: [itemInstance, ...]
		"""
		# 目前最多140个，需要分批发送
		#return self.storage.getDatas()
		return self.storage.getDatasByRange( bagID * csdefine.KB_MAX_SPACE, bagID * csdefine.KB_MAX_SPACE + csdefine.KB_MAX_SPACE - 1 )


	def requestStorageItem( self, playerDBID, count ):
		"""
		Define method.
		请求仓库数据

		@param playerDBID : 请求的玩家dbid
		@type playerDBID : DATABASE_ID
		@param count : 请求0,1,2...
		@type count : UINT8
		"""
		#storageOrderCount = csconst.TONG_WAREHOUSE_LIMIT[ self.ck_level ]
		#if count * 30 >= storageOrderCount:
		#	ERROR_MSG( "request items:out of storage's space!" )
		#	return
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return

		if count % 2 == 0:
			startOrder = count / 2 * 255
		else:
			startOrder = count / 2 * 255 + 40
		endOrder = startOrder + 40	# 一次最多发40个

		items = self.storage.getDatasByRange( startOrder, endOrder )
		playerBase.client.tong_receiveStorageItem( items )


	def storeItem2Order( self, srcOrder, srcItem, dstOrder, playerDBID ):
		"""
		Define method.
		存储物品到帮会仓库指定物品格

		@param srcOrder : 物品在背包中的order
		@type srcOrder : INT16
		@param srcItem : 物品实例
		@type srcItem : ITEM
		@param dstOrder : 物品在仓库中的order
		@type dstOrder : INT16
		@param playerDBID : 玩家databaseID
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return

		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE

		if self.isStorageFrozen():
			DEBUG_MSG( "The storage has been Frozen.-------->>>" )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		bagID = dstOrder / csdefine.KB_MAX_SPACE
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID 参数错误,帮会名字:%s,bagID:%i." % ( self.playerName, bagID ) )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		quality = srcItem.getQuality()
		if self.storageBagPopedom[bagID]["qualityLowerLimit"] > quality:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_QUALITY_LOWER )
			return

		if self.storageBagPopedom[bagID]["qualityUpLimit"] < quality:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_QUALITY_HIGHER )
			return

		if not self._addItem2Order( srcOrder, dstOrder, srcItem, playerBase ):	# 添加失败
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return
		self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_ADD, srcItem, bagID, time.time() )

	def _addItem2Order( self, srcOrder, dstOrder, srcItem, playerBase ):
		"""
		把一个物品放到指定包裹的格子中，被storeItem2Order调用
		成功则返回True，否则返回False

		@param srcOrder : 物品在背包中的order
		@type srcOrder : INT16
		@param srcItem : 物品实例
		@type srcItem : ITEM
		@param dstOrder : 物品在仓库中的order
		@type dstOrder : INT16
		@param playerBase : 玩家baseMailbox
		@type playerBase : MAILBOX
		"""
		if self.storage.add( dstOrder, srcItem ):
			playerBase.cell.tong_storeItemSuccess01( srcOrder )
			playerBase.client.tong_storeItemUpdate( srcItem )
			return True

		dstItem = self.storage.getByOrder( dstOrder )
		if dstItem.isFrozen():
			WARNING_MSG( "包裹被锁定。" )
			return False

		if srcItem.getStackable() > 1 and dstItem.id == srcItem.id:	# 可叠加道具特殊处理
			overlapAmount = srcItem.getStackable()
			dstAmount = dstItem.getAmount()
			srcAmount = srcItem.getAmount()
			storeAmount = min( overlapAmount - dstAmount, srcAmount )
			# 不能自动通知客户端，手动通知
			dstItem.setAmount( dstAmount + storeAmount )
			playerBase.client.tong_storeItemUpdate( dstItem )
			srcAmount = srcAmount - storeAmount
			if srcAmount:	# 在目标位置叠加后还有剩余，放回背包
				srcItem.setAmount( srcAmount )
				playerBase.client.tong_storeItemUpdate( srcItem )
				playerBase.cell.tong_storeItemSuccess02( srcOrder, srcItem )
				return True
			playerBase.cell.tong_storeItemSuccess01( srcOrder )			# 没有剩余
			return True

		else:	# 如果目标位置是 id相同的不可叠加物品 或 id不同的可叠加物品，则是交换操作
			playerBase.cell.tong_storeItemSuccess02( srcOrder, dstItem )
			if self.storage.removeByOrder( dstOrder ):
				if self.storage.add( dstOrder, srcItem ):	# 把从背包那边拖入仓库的物品加入到仓库物品栏
					playerBase.client.tong_storeItemUpdate( srcItem )
					return True
		return False


	def storeItem2Bag( self, srcOrder, item, bagID, playerDBID ):
		"""
		Define method.
		往帮会仓库里存储物品的接口，仅指定了包裹位

		param dstOrder:	格子号
		type dstOrder:	INT16
		param item:		往帮会仓库里存储的物品
		type item:		ITEM
		param bagID:帮会仓库包裹位号
		type bagID:UINT8
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID 参数错误,帮会名字:%s,bagID:%i." % ( self.playerName, bagID ) )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		if self.isStorageFrozen():
			DEBUG_MSG( "The storage has been Frozen.-------->>>" )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		quality = item.getQuality()
		if self.storageBagPopedom[bagID]["qualityLowerLimit"] > quality:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_QUALITY_LOWER )
			return

		if self.storageBagPopedom[bagID]["qualityUpLimit"] < quality:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_QUALITY_HIGHER )
			return

		if item.getStackable() > 1:							# 如果是可叠加物品
			if self._stackableInStorageBag( item, bagID, playerBase ):	# 叠加成功
				playerBase.cell.tong_storeItemSuccess01( srcOrder )
			else:
				order = self._findBagFreeOrder( bagID )
				if order == -1:
					playerBase.cell.tong_unfreezeBag( kitbagNum )
					return
				if self.storage.add( order, item ):
					playerBase.client.tong_storeItemUpdate( item )
					playerBase.cell.tong_storeItemSuccess01( srcOrder )
					playerBase.cell.tong_unfreezeBag( kitbagNum )
		else:	# 如果不是可叠加物品
			order = self._findBagFreeOrder( bagID )
			if order == -1:
				playerBase.cell.tong_unfreezeBag( kitbagNum )
				return
			if self.storage.add( order, item ):
				playerBase.client.tong_storeItemUpdate( item )
				playerBase.cell.tong_storeItemSuccess01( srcOrder )
				playerBase.cell.tong_unfreezeBag( kitbagNum )
		self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_ADD, item, bagID, time.time() )


	def storeItem2Storage( self, srcOrder, item, playerDBID ):
		"""
		Define method.
		存储物品到仓库,例如:鼠标右键操作

		@param srcOrder : 物品在背包中的order
		@type srcOrder : INT16
		@param item : 物品实例
		@type item : ITEM
		@param playerDBID : 玩家databaseID
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE

		if self.isStorageFrozen():
			DEBUG_MSG( "The storage has been Frozen.-------->>>" )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		dstOrder = self._findFreeOrder()
		if dstOrder == -1:
			#playerBase,通知：没有空位了。
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		bagID = dstOrder / csdefine.KB_MAX_SPACE
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID 参数错误,帮会名字:%s,bagID:%i." % ( self.playerName, bagID ) )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		quality = item.getQuality()
		if self.storageBagPopedom[bagID]["qualityLowerLimit"] > quality:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_QUALITY_LOWER )
			return

		if self.storageBagPopedom[bagID]["qualityUpLimit"] < quality:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_QUALITY_HIGHER )
			return

		def storeItem():
			# 查找帮会仓库里的空位
			orderID = self._findFreeOrder()
			if orderID != -1:	# 如果有空位
				if self.storage.add( orderID, item ):
					playerBase.cell.tong_storeItemSuccess01( srcOrder )
					playerBase.client.tong_storeItemUpdate( item )
					return
			else:	# 物品存储失败
				playerBase.cell.tong_unfreezeBag( kitbagNum )
				return

		if item.getStackable() > 1:					# 如果是可叠加物品
			if self._stackableInStorage( item, playerBase ):	# 查找仓库里的同类可叠加物品 叠加
				playerBase.cell.tong_storeItemSuccess01( srcOrder )
			else:
				storeItem()
		else:		# 如果不是可叠加物品
			storeItem()
		self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_ADD, item, bagID, time.time() )


	def fetchItem2Order( self, srcOrder, dstOrder, playerDBID ):
		"""
		Define method.
		从仓库取出物品到背包

		@param srcOrder : 物品在仓库中的order
		@type srcOrder : INT16
		@param dstOrder : 物品在玩家背包的order
		@type dstOrder : INT16
		@param playerDBID : 玩家databaseID
		@type playerDBID : DATABASE_ID
		"""
		kitbagNum = dstOrder / csdefine.KB_MAX_SPACE
		item = self.storage.getByOrder( srcOrder )
		self._fetchItem( kitbagNum, srcOrder, dstOrder, item.getAmount(), playerDBID )

	def fetchItem2Kitbags( self, kitbagNum, srcOrder, playerDBID ):
		"""
		Define method.
		从帮会仓库里取出物品的接口，不指定包裹位与目标格子，在背包里查找第一个空位

		@param srcOrder : 物品在背包中的order
		@type srcOrder : INT16
		@param playerDBID : 玩家databaseID
		@type playerDBID : DATABASE_ID
		"""
		item = self.storage.getByOrder( srcOrder )
		self._fetchItem( kitbagNum, srcOrder, 0, item.getAmount(), playerDBID )

	def fetchSplitItem2Kitbags( self, kitbagNum, srcOrder, amount, playerDBID ):
		"""
		Define method.
		从帮会仓库里取出物品的接口，不指定包裹位与目标格子，在背包里查找第一个空位

		@param srcOrder : 物品在仓库中的order
		@type srcOrder : INT16
		@param playerDBID : 玩家databaseID
		@param amount : 提取物品数量
		@param amount : INT16
		@type playerDBID : DATABASE_ID
		"""
		self._fetchItem( kitbagNum, srcOrder, 0, amount, playerDBID )
		
	def _fetchItem( self, kitbagNum, srcOrder, dstOrder, amount, playerDBID ):
		"""
		Define method.
		从帮会仓库里取出物品的接口，不指定包裹位与目标格子，在背包里查找第一个空位

		@param srcOrder : 物品在仓库中的order
		@type srcOrder : INT16
		@param dstOrder : 物品在玩家背包的order
		@type dstOrder : INT16
		@param playerDBID : 玩家databaseID
		@param amount : 提取物品数量
		@param amount : INT16
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return
		
		# 判断当前物品是否存在
		item = self.storage.getByOrder( srcOrder )
		if item is None:
			HACK_MSG( "物品不存在。" )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			playerBase.client.tong_delItemUpdate( srcOrder )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_ITEM_NOT_EXIST )
			return
			
		# 判断仓库是否锁定	
		if self.isStorageFrozen():
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_ISCHANGE )
			return
		
		# 判断当前物品是否锁定
		if item.isFrozen():
			WARNING_MSG( "物品被锁定" )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_ISCHANGE )
			return
		
		# 判断提取order的有效性	
		bagID = srcOrder / csdefine.KB_MAX_SPACE
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID 参数错误,帮会名字:%s,bagID:%i." % ( self.playerName, bagID ) )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_BAGID_ERROR )
			return
			
		# 当前职位每天能取多少物品
		fetchNum = self.getFetchNumByOfficialPos( bagID, menberInfo.getGrade() )	
		if fetchNum == 0:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_NOT_PURVIEW )
			return
		
		# 判断当天提取是否已经大于当前职位的提取量
		todayFetchNum = self.getTodayFetchNum( bagID, playerDBID )
		if amount > fetchNum - todayFetchNum:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_NOT_FETCH_MORE )
			return
		
		tempItem = item.copy()
		tempItem.setAmount( amount )
		item.freeze()
		if dstOrder == 0 or dstOrder == None:
			itemAmount = item.getAmount()
			if itemAmount <= amount:
				playerBase.cell.tong_fetchItem2KitbagsCB( srcOrder, tempItem )
			else:
				playerBase.cell.tong_fetchSplitItem2KitbagsCB( srcOrder, tempItem )
		else:
			playerBase.cell.tong_fetchItem2OrderCB( dstOrder, tempItem, srcOrder )

	def moveStorageItem( self, srcOrder, dstOrder, playerDBID ):
		"""
		Define method.
		在同一个包裹中移动物品的接口

		@param srcOrder : 物品在背包中的order
		@type srcOrder : INT16
		@param dstOrder : 物品在仓库中的order
		@type dstOrder : INT16
		@param playerDBID : 玩家databaseID
		@type playerDBID : DATABASE_ID
		"""
 		if srcOrder == dstOrder:
 			return

		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return

		# 检查权限
		if not self.checkMemberDutyRights( menberInfo.getGrade() , csdefine.TONG_RIGHT_STORAGE_MANAGE ):
			DEBUG_MSG( "------>>>权限不够."  )
			return

		srcItem = self.storage.getByOrder( srcOrder )
		if srcItem is None:
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return

		if srcItem.isFrozen():
			return

		if not self.storage.orderHasItem( dstOrder ):	# 目标格子空
			if self.storage.swapOrder( srcOrder, dstOrder ):
				playerBase.client.tong_moveItemCB( srcOrder, dstOrder )
				return
			else:	# 不可控原因
				return

		dstItem = self.storage.getByOrder( dstOrder )
		if dstItem.isFrozen():
			return

		if srcItem.getStackable() <= 1 or dstItem.id != srcItem.id:	# 可叠加道具处理
			if self.storage.swapOrder( srcOrder, dstOrder ):
				playerBase.client.tong_moveItemCB( srcOrder, dstOrder )
		else:	# 如果目标位置是 id相同的不可叠加物品 与 id不同的可叠加物品，则是交换操作
			overlapAmount = srcItem.getStackable()
			dstAmount = dstItem.getAmount()
			srcAmount = srcItem.getAmount()
			storeAmount = min( overlapAmount - dstAmount, srcAmount )
			dstItem.setAmount( dstAmount + storeAmount )
			playerBase.client.tong_storeItemUpdate( dstItem )
			srcAmount = srcAmount - storeAmount
			if srcAmount:	# 在目标位置叠加后还有剩余，放回源位置
				srcItem.setAmount( srcAmount )
				playerBase.client.tong_storeItemUpdate( srcItem )
				return
			if self.storage.removeByOrder( srcOrder ):	# 无剩余，删除源物品
				playerBase.client.tong_delItemUpdate( srcOrder )

	def storageStatusMessage( self, targetBaseMailbox, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		if args == ():
			tempArgs = ""
		else:
			tempArgs = str( args )
		#args = args == () and "" or str( args )
		targetBaseMailbox.client.onStatusMessage( statusID, tempArgs )


	def fetchItemSuccess01( self, dstOrder, playerDBID ):
		"""
		Define method.
		取出一个物品成功， base解锁并删除物品

		@param dstOrder : 物品在仓库中的order
		@type dstOrder : INT16
		@param playerDBID : 玩家databaseID
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		self.unFreezeStorage()
		item = self.storage.getByOrder( dstOrder )
		itemAmount = item.getAmount()
		self.storage.removeByOrder( dstOrder )
		bagID = dstOrder / csdefine.KB_MAX_SPACE
		self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_MINUS, item, bagID, time.time() )
		self._fetchItemSuccess( playerDBID, bagID, itemAmount )
		playerBase = menberInfo.getBaseMailbox()
		if playerBase:
			playerBase.client.tong_fetchStorageItemCB( itemAmount )
			playerBase.client.tong_delItemUpdate( dstOrder )


	def fetchItemSuccess02( self, dstOrder, item, playerDBID ):
		"""
		Define method.
		背包从帮会仓库取一个物品的回调。
		背包中叠加一个物品有剩余，或帮会仓库与背包目标格子交换物品，把 剩余物品 或 交换的物品 放回帮会仓库

		@param dstOrder : 物品在仓库中的order
		@type dstOrder : INT16
		@param item : 物品
		@type item : ITEM
		@param playerDBID : 玩家databaseID
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		self.unFreezeStorage()
		srcItem = self.storage.getByOrder( dstOrder )
		itemAmount = srcItem.getAmount()
		self.storage.removeByOrder( dstOrder )
		bagID = dstOrder / csdefine.KB_MAX_SPACE
		self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_MINUS, srcItem, bagID, time.time() )
		self._fetchItemSuccess( playerDBID, bagID, itemAmount )
		if self.storage.add( dstOrder, item ):
			self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_ADD, item, bagID, time.time() )
			if playerBase:
				playerBase.client.tong_storeItemUpdate( item )


	def fetchItemSuccess03( self, dstOrder, amount, playerDBID ):
		"""
		Define method.
		取出一个物品成功， base解锁并删除物品

		@param dstOrder : 物品在仓库中的order
		@type dstOrder : INT16
		@param playerDBID : 玩家databaseID
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		self.unFreezeStorage()
		item = self.storage.getByOrder( dstOrder )
		itemAmount = item.getAmount()
		
		item.setAmount( itemAmount - amount )
		item.unfreeze()
			
		bagID = dstOrder / csdefine.KB_MAX_SPACE
		self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_MINUS, item, bagID, time.time() )
		self._fetchItemSuccess( playerDBID, bagID, amount )
		playerBase = menberInfo.getBaseMailbox()
		if playerBase:
			playerBase.client.tong_fetchStorageItemCB( amount )
			playerBase.client.tong_storeItemUpdate( item )
				
	def _stackableInStorage( self, itemInstance, playerBase ):
		"""
		在仓库中对一个可叠加物品叠加操作

		@param itemInstance:继承于CItemBase的自定义道具实例
		@type  itemInstance:CItemBase
		@param playerBase : 玩家baseMailbox
		@type playerBase : MAILBOX
		@return:	成功则返回True失败则返回False
		@rtype:		BOOL
		"""
		currtotal = 0
		stackable = itemInstance.getStackable()
		r = self._findAllItemFromStorage( itemInstance.id, itemInstance.isBinded() )
		if r == []:return False
		#获得总数
		for e in r:									# e like as ( kitOrder, orderID, itemData )
			# like as: c += a < b ? a : b，做这个检查的原因是避免测试时手动设置多于stackable数量的物品产生判断错误
			currtotal += e.getAmount() < stackable and e.getAmount() or stackable
		val = len( r ) * stackable - currtotal		# 获取还可以叠加的数量
		val1 = itemInstance.getAmount()				# 获取这个物品的数量
		if val < val1:	return False
		for e in r:
			if val1 <= 0:break
			amount = stackable - e.getAmount()
			if amount > 0:
				if amount > val1:
					e.setAmount( e.getAmount() + val1 )
					playerBase.client.tong_storeItemUpdate( e )
					return True
				else:
					e.setAmount( stackable )
					playerBase.client.tong_storeItemUpdate( e )
					val1 -= amount
		return True


	def _findAllItemFromStorage( self, itemKeyName, isBinded ):
		"""
		从所有普通背包里找到所有与itemKeyName相同的物品

		@param itemKeyName: 表示每一类道具的唯一的道具类型
		@type  itemKeyName: STRING
		@return:	array of tuple as (kitOrder, orderID, itemData)
		@rtype:		array of tuple
		"""
		itemList = []
		for item in self.storage.getDatas():
			if item.id == itemKeyName and item.isBinded() == isBinded:
				itemList.append( item )
		return itemList


	def checkFetchStatus( self, playerDBID ):
		"""
		查询玩家的取物品状态

		@param playerDBID : 玩家的dbid
		@type playerDBID : DATABASE_ID

		查询的结果有可能是:
		1,今日已不能再取物品
		2,没有取物品的权限
		3,可以取物品
		"""
		pass

	def isStorageExtend( self ):
		"""
		仓库是否因为升级扩展空间
		"""
		if self.ck_level in EXTEND_LEVEL_LIST:
			return True
		return False

	def isStorageReduce( self ):
		"""
		仓库是否因为降级减少空间
		"""
		if self.ck_level in REDUCE_LEVEL_LIST:
			return True
		return False

	def onStorageUpgrade( self ):
		"""
		仓库升级
		"""
		if not self.isStorageExtend():
			return

		# 所有成员的默认权限为可取无限多的物品
		gradeFetchItemLimit = { csdefine.TONG_DUTY_MEMBER	:	0,
								csdefine.TONG_DUTY_TONG	:	0,
								csdefine.TONG_DUTY_DEPUTY_CHIEF	:	0,
								csdefine.TONG_DUTY_CHIEF	:	DAY_FETCH_ITEM_LIMIT,
								}

		tongStoragePopedom = { "bagID":len( self.storageBagPopedom ),	# 仓库升级，新加包裹id刚好为len( self.storageBagPopedom )
								"bagName":"",
								"qualityUpLimit":ItemTypeEnum.CQT_GREEN,
								"qualityLowerLimit":ItemTypeEnum.CQT_WHITE,
								"fetchItemLimit":gradeFetchItemLimit,
								}

		self.storageBagPopedom.append( tongStoragePopedom )


	def onStorageDegrade( self ):
		"""
		仓库降级
		"""
		if not self.isStorageReduce():
			return
		self.storageBagPopedom.pop()	# 此时还保留着仓库物品.


	def renameStorageBag( self, bagID, newName, playerDBID ):
		"""
		Define method.
		改变包裹的名字

		@param bagID : 帮会仓库包裹的id
		@type bagID : UINT8
		@param newName : 包裹名
		@type newName : STRING
		@param playerDBID : 玩家dbid
		@type playerDBID : DATABASE_ID
		"""
		# 参数检查
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID 参数错误,帮会名字:%s,bagID:%i." % ( self.playerName, bagID ) )
			return
		menberInfo = self.getMemberInfos( playerDBID )
		if not self.checkMemberDutyRights( menberInfo.getGrade() , csdefine.TONG_RIGHT_STORAGE_MANAGE ):
			DEBUG_MSG( "------>>>权限不够."  )
			return

		if newName == self.storageBagPopedom[ bagID ]["bagName"]:
			return

		self.storageBagPopedom[ bagID ]["bagName"] = newName

		playerBase = menberInfo.getBaseMailbox()
		if playerBase:	# 仅通知更改者的客户端
			playerBase.client.tong_updateStorageBagName( bagID, newName )


	def changeStorageQualityUp( self, bagID, quality, playerDBID ):
		"""
		Define method.
		改变帮会仓库包裹物品质量上限

		@param bagID : 帮会仓库包裹的id
		@type bagID : UINT8
		@param quality : 质量
		@type quality : UINT8
		@param playerDBID : 玩家dbid
		@type playerDBID : DATABASE_ID
		"""
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID 参数错误,帮会名字:%s,bagID:%i." % ( self.playerName, bagID ) )
			return
		if quality not in ITEM_QUALITYS:
			DEBUG_MSG( "----->>>quality:%i 不存在." % quality )
			return
		menberInfo = self.getMemberInfos( playerDBID )
		if not self.checkMemberDutyRights( menberInfo.getGrade() , csdefine.TONG_RIGHT_STORAGE_MANAGE ):
			DEBUG_MSG( "------>>>权限不够."  )
			return
		self.setBagUpQuality( bagID, quality )


	def changeStorageQualityLower( self, bagID, quality, playerDBID ):
		"""
		Define method.
		改变帮会仓库包裹物品质量下限

		@param bagID : 帮会仓库包裹的id
		@type bagID : UINT8
		@param quality : 质量
		@type quality : UINT8
		@param playerDBID : 玩家dbid
		@type playerDBID : DATABASE_ID
		"""
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID 参数错误,帮会名字:%s,bagID:%i." % ( self.playerName, bagID ) )
			return
		if quality not in ITEM_QUALITYS:
			DEBUG_MSG( "------->>>quality:%i 不存在." % quality )
			return
		menberInfo = self.getMemberInfos( playerDBID )
		if not self.checkMemberDutyRights( menberInfo.getGrade() , csdefine.TONG_RIGHT_STORAGE_MANAGE ):
			DEBUG_MSG( "------>>>权限不够."  )
			return

		self.setBagLowerQuality( bagID, quality )


	def setBagLowerQuality( self, bagID, quality ):
		"""
		设置包裹的物品品质下限

		@param bagID : 帮会仓库包裹的id
		@type bagID : UINT8
		@param quality : 质量
		@type quality : UINT8
		"""
		self.storageBagPopedom[bagID]["qualityLowerLimit"] = quality


	def setBagUpQuality( self, bagID, quality ):
		"""
		设置包裹的物品品质上限

		@param bagID : 帮会仓库包裹的id
		@type bagID : UINT8
		@param quality : 质量
		@type quality : UINT8
		"""
		self.storageBagPopedom[bagID]["qualityUpLimit"] = quality


	def getBagLimitByID( self, bagID ):
		"""
		根据bagID获得此包裹的额外数据
		"""
		return self.storageBagPopedom[ bagID ]


	def isStorageBagID( self, bagID ):
		"""
		验证bagID是否合法
		"""
		return bagID < len( self.storageBagPopedom )


	def changeStorageBagLimit( self, bagID, job, limitCount, playerDBID ):
		"""
		Define method.
		改变包裹的职位使用权限

		@param bagID : 帮会仓库包裹的id
		@type bagID : UINT8
		"""
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID 参数错误,帮会名字:%s,bagID:%i." % ( self.playerName, bagID ) )
			return

		if job == csdefine.TONG_DUTY_CHIEF:
			# 不能改变帮主的权限
			return

		menberInfo = self.getMemberInfos( playerDBID )
		if not self.checkMemberDutyRights( menberInfo.getGrade() , csdefine.TONG_RIGHT_STORAGE_MANAGE ):
			DEBUG_MSG( "------>>>权限不够."  )
			return

		bagLimit = self.getBagLimitByID( bagID )
		bagLimit[ "fetchItemLimit" ][job] = limitCount
		# 不需要更新到客户端


	def getFetchNumByOfficialPos( self, bagID, grade ):
		"""
		根据职位获得取物品的权限
		"""
		return self.storageBagPopedom[bagID]["fetchItemLimit"][grade]


	def getTodayStorageFetchRecord( self, playerDBID ):
		"""
		获得玩家今天在帮会仓库中的取物品记录
		"""
		playerFetchRecord = {}
		if playerDBID in self.playerFetchRecord:
			playerFetchRecord = self.playerFetchRecord[playerDBID]
		else:
			self.playerFetchRecord[playerDBID] = {}
		return playerFetchRecord


	def getTodayFetchNum( self, bagID, playerDBID ):
		"""
		根据玩家dbid获得玩家今天在bagID的包裹中已经取出的物品个数
		"""
		num = 0
		if playerDBID in self.playerFetchRecord:
			if bagID in self.playerFetchRecord[playerDBID]:
				num = self.playerFetchRecord[playerDBID][bagID]
			else:
				self.playerFetchRecord[playerDBID][bagID] = 0
		else:	# 如果今天还没取过,那么加入记录
			self.playerFetchRecord[playerDBID] = {}
			self.playerFetchRecord[playerDBID][bagID] = 0

		return num


	def _fetchItemSuccess( self, playerDBID, bagID, amount ):
		"""
		取物品成功后的处理
		例如:更新玩家今天的取物品数量

		@param playerDBID : 玩家dbid
		@type playerDBID : DATABASE_ID
		@param amount : 物品数量
		@type amount : INT32
		"""
		if playerDBID in self.playerFetchRecord:
			if bagID in self.playerFetchRecord[playerDBID]:
				self.playerFetchRecord[playerDBID][bagID] += amount
			else:
				self.playerFetchRecord[playerDBID][bagID] = amount
		else:
			self.playerFetchRecord[ playerDBID ] = {}
			self.playerFetchRecord[ playerDBID ][bagID] = amount


	def _stackableInStorageBag( self, itemInstance, bagID, playerBase ):
		"""
		在包裹中对一个可叠加物品叠加操作
		"""
		currtotal = 0
		stackable = itemInstance.getStackable()
		r = []
		for item in self._getStorageBagItems( bagID ):
			if item.id == itemInstance.id and item.isBinded() == itemInstance.isBinded():
				r.append( item )
		if len( r ) == 0: return False
		#获得总数
		for item in r:
			# like as: c += a < b ? a : b，做这个检查的原因是避免测试时手动设置多于stackable数量的物品产生判断错误
			currtotal += item.getAmount() < stackable and item.getAmount() or stackable
		val = len( r ) * stackable - currtotal		# 获取还可以叠加的数量
		val1 = itemInstance.getAmount()				# 获取这个物品的数量
		if val < val1:	return False
		for item in r:
			if val1 <= 0:break
			amount = stackable - item.getAmount()
			if amount > 0:
				if amount > val1:
					item.setAmount( item.getAmount() + val1 )
					playerBase.client.tong_storeItemUpdate( item )
					return True
				else:
					item.setAmount( stackable )
					playerBase.client.tong_storeItemUpdate( item )
					val1 -= amount
		return True


	def resetStorageLimit( self ):
		"""
		重置玩家的取物品记录
		"""
		self.playerFetchRecord = {}
		self.resetStorageLimitTime = time.time()	# 记录上一次重置时间


	def onTimer( self, timerID, cbid ):
		"""
		timer:每天0点重置帮会仓库的取物品限制数据.
		"""
		if timerID == self.storage_resetLimitTimer:
			self.resetStorageLimit()
			self.storage_resetLimitTimer = self.addTimer( 24*60*60 )	# 开启下一次重置timer


	def _storageCalcTime( self, point ):
		"""
		返回离point的时间差，比如point为[ 21, 40, 0 ]点 返回现在离下一次point点所需要的时间
		@param point: [ 小时, 分钟, 秒 ]
		"""
		t = time.localtime()
		h = t[ 3 ]
		m = t[ 4 ]
		s = t[ 5 ]

		# 以下过程模拟减法运算
		second = point[ 2 ] - s
		if second < 0:
			second = point[ 2 ] + 60 - s
			point[ 1 ] -= 1
		minut = point[ 1 ] - m
		if minut < 0:
			minut = point[ 1 ] + 60 - m
			point[ 0 ] -= 1
		hour = point[ 0 ] - h
		if hour < 0:
			hour = point[ 0 ] + 24 - h

		return hour * 60 * 60 + minut * 60 + second

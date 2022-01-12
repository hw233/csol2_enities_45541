# -*- coding: gb18030 -*-
#


import Love3
import BigWorld
from Function import newUID
from CollectionItem import CollectionItem
import csconst
import time
from bwdebug import *
from Function import Functor
import csstatus


"""
收购物品管理器
"""


#收购timer 行为
OPERATE_CANCEL			= 465485	#取消操作

MAX_OPERATE_ITEM		= 3.0		#秒


class Operate:
	"""
	"""
	def __init__( self, func, paramDict ):
		"""
		"""
		self.func 		= func
		self.paramDict 	= paramDict

	def do( self ):
		"""
		"""
		self.func( self.paramDict )


class CollectionBag:
	"""
	收集包
	"""
	def __init__( self, playerDBID, db, writeToDB = True ):
		"""
		"""
		self.state 			= False
		self.ownerDBID		= playerDBID
		self.items 			= {}
		self.db 			= db
		self.operateTime 	= 0.0
		if writeToDB:
			self.register()
		self.loadItems()


	def register( self ):
		"""
		"""
		self.db.new( self.ownerDBID )

	def loadItems( self ):
		"""
		"""
		self.db.loadItems( self )

	def onLoadItem( self, collectionItem ):
		"""
		"""
		self.items[collectionItem.uid] = collectionItem


	def start( self ):
		"""
		"""
		self.state = True
		self.db.start( self.ownerDBID )


	def stop( self ):
		"""
		"""
		self.state = False
		self.db.stop( self.ownerDBID )


	def add( self, collectionItem ):
		"""
		"""
		collectionItem.uid = newUID()
		self.items[collectionItem.uid] = collectionItem
		self.db.add( collectionItem )


	def remove( self, uid ):
		"""
		"""
		collectionItem = self.get( uid )
		if collectionItem is None:
			return False
		if collectionItem.collectedAmount == 0:
			del self.items[uid]
			self.db.remove( uid )
		elif collectionItem.collectAmount != collectionItem.collectedAmount:
			collectionItem.collectAmount = collectionItem.collectedAmount
			self.db.update( collectionItem )
		return True

	def update( self, collectionItem ):
		"""
		"""
		item = self.get( collectionItem.uid )

		if item is None:
			return False
		self.items[collectionItem.uid] = collectionItem
		self.db.update( collectionItem )
		
		return True

	def takeItems( self ):
		"""
		"""
		items = []
		for i in self.items.itervalues():
			if not i.isEmpty():
				items.append( i )
		return items

	def onTaked( self ):
		"""
		"""
		removes = []
		updates = []
		for i in self.items.itervalues():
			if i.isFull():
				removes.append( i )
			elif not i.isEmpty():
				updates.append( i )

		for i in removes:
			del self.items[i.uid]
			self.db.remove( i.uid )

		for i in updates:
			i.onTake()
			self.update( i )

	def get( self, uid ):
		"""
		"""
		if uid in self.items:
			return self.items[uid]
		return None

	def check( self, collectionItems ):
		"""
		"""
		items = []
		for i in collectionItems:
			item = self.get( i.uid )
			if item and item.check( i ):
				items.append( item )
			else:
				return []
		return items


	def isFull( self ):
		"""
		"""
		return len( self.items ) >= csconst.COLLECTION_BAG_SIZE


	def onSell( self, collectionItems ):
		"""
		"""
		for i in collectionItems:
			item = self.get(i.uid)
			item.onSell( i )
			self.db.update( item )

	def getTotalPrice( self ):
		"""
		"""
		totalPrice = 0
		for i in self.items:
			totalPrice += self.items[i].getTotalPrice()
		
		return totalPrice

	def isEmpty( self ):
		"""
		"""
		return len( self.items ) == 0

	def onTakeDeposit( self ):
		"""
		"""
		for i in self.items.keys():
			self.remove( i )
		

class CollectionDB:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.createTable()

	def createTable( self ):
		"""
		"""
		query = """CREATE TABLE IF NOT EXISTS `custom_collectionItemTable` (
				`id`					BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_itemID` 			BIGINT(20),
				`sm_uid`	 			BIGINT(20),
				`sm_price`		 		BIGINT(20),
				`sm_collectAmount`		BIGINT(20),
				`sm_collectedAmount`	BIGINT(20),
				`sm_collectorDBID`		BIGINT(20),
				`sm_delFlag` 			BIGINT(20) NOT NULL default 0,
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, self.__createTableCB )

		query = """CREATE TABLE IF NOT EXISTS `custom_collectionTable` (
				`id`					BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_isCollecting`		TINYINT(1),
				`sm_collectorDBID`		BIGINT(20),
				UNIQUE KEY `sm_collectorDBID`  (`sm_collectorDBID`),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, self.__createTableCB )

	def clearTable( self ):
		"""
		"""
		query = "delete from custom_collectionTable"
		BigWorld.executeRawDatabaseCommand( query, self.__onClearTable )

		query = "delete from custom_collectionItemTable"
		BigWorld.executeRawDatabaseCommand( query, self.__onClearTable )

	def loadBags( self, mgr ):
		"""
		"""
		query = "select * from custom_collectionTable"
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onLoadBags, mgr ) )

	def loadItems( self, bag ):
		"""
		"""
		query = "select * from custom_collectionItemTable where sm_collectorDBID = %i"%bag.ownerDBID
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onLoadItems, bag ) )

	def new( self, collectorDBID ):
		"""
		"""
		query = "insert into custom_collectionTable ( sm_isCollecting, sm_collectorDBID ) value ( 0, %i )"%collectorDBID
		BigWorld.executeRawDatabaseCommand( query, self.__newCB )


	def delete( self, collectorDBID ):
		"""
		"""
		query = "delete from custom_collectionItemTable where sm_collectorDBID = %i"%collectorDBID
		BigWorld.executeRawDatabaseCommand( query, self.__deleteCB )



	def start( self, collectorDBID ):
		"""
		"""
		query = "update custom_collectionTable set sm_isCollecting = 1 where sm_collectorDBID = %i "%collectorDBID
		BigWorld.executeRawDatabaseCommand( query, self.__startCB )


	def stop( self, collectorDBID ):
		"""
		"""
		query = "update custom_collectionTable set sm_isCollecting = 0 where sm_collectorDBID = %i "%collectorDBID
		BigWorld.executeRawDatabaseCommand( query, self.__stopCB )


	def add( self, collectionItem ):
		"""
		"""
		paramTuple = ( collectionItem.itemID, collectionItem.uid, collectionItem.price, collectionItem.collectAmount, 0, collectionItem.collectorDBID )
		query = "insert into custom_collectionItemTable ( sm_itemID, sm_uid, sm_price, sm_collectAmount, sm_collectedAmount, sm_collectorDBID ) value ( \'%s\', %i, %i, %i, %i, %i )"%paramTuple
		BigWorld.executeRawDatabaseCommand( query, self.__addCB )


	def remove( self, uid ):
		"""
		"""
		query = "delete from custom_collectionItemTable where sm_uid = %i"%uid
		BigWorld.executeRawDatabaseCommand( query, self.__removeCB )


	def update( self, collectionItem ):
		"""
		"""
		paramTuple = ( collectionItem.price, collectionItem.collectAmount, collectionItem.collectedAmount, collectionItem.uid )
		query = "update custom_collectionItemTable set sm_price = %i, sm_collectAmount = %i, sm_collectedAmount = %i where sm_uid = %i"%paramTuple
		BigWorld.executeRawDatabaseCommand( query, self.__updateCB )


	def __createTableCB( self, result, rows, errstr ):
		"""
		生成数据库表格回调函数

		param tableName:	生成的表格名字
		type tableName:		STRING
		"""
		if errstr:

			ERROR_MSG( "Create custom_collectionTable fault! %s"%errstr  )
			return

	def __onLoadBags( self, mgr, result, rows, errstr ):
		"""
		"""
		if result is None:
			return
		for i in result:
			state 	= int(i[1])
			dbid	= int(i[2])
			bag = CollectionBag( dbid, self, False )
			mgr.onLoadBag( bag )


	def __onLoadItems( self, bag,  result, rows, errstr ):
		"""
		"""
		if result is None:
			return
		for i in result:
			item		= CollectionItem()
			item.itemID	= int(i[1])
			item.uid	= int(i[2])
			item.price	= int(i[3])
			item.collectAmount	= int(i[4])
			item.collectedAmount= int(i[5])
			item.collectorDBID	= int(i[6])
			item.delFlag		= int(i[7])

			bag.onLoadItem( item )


	def __newCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:

			ERROR_MSG( "new collect instance fault! %s"%errstr  )
			return

	def __deleteCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:

			ERROR_MSG( "delete collect instance fault! %s"%errstr  )
			return


	def __startCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:

			ERROR_MSG( "start to collect fault! %s"%errstr  )
			return

	def __stopCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:

			ERROR_MSG( "stop to collect fault! %s"%errstr  )
			return

	def __addCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:

			ERROR_MSG( "add collectionItem fault! %s"%errstr  )
			return

	def __removeCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:

			ERROR_MSG( "remove collectionItem fault! %s"%errstr  )
			return


	def __updateCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:

			ERROR_MSG( "update collectionItem fault! %s"%errstr  )
			return

	def __onClearTable( self, result, rows, errstr ):
		"""
		"""
		if errstr:

			ERROR_MSG( "clear collection table fault! %s"%errstr  )
			return


class CollectionMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体
		self.registerGlobally( "CollectionMgr", self._onRegisterManager )
		self.collectionBags = {}
		self.db = CollectionDB()

		self.loadBags()

		self.operateList 			= []		#操作列表
		self.cancelOperateTimerID	= 0			#取消操作的timerID


	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register CollectionMgr Fail!" )
			# again
			self.registerGlobally( "CollectionMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["CollectionMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("CollectionMgr Create Complete!")

	def loadBags( self ):
		"""
		"""
		self.db.loadBags( self )

	def onLoadBag( self, bag ):
		"""
		"""
		self.collectionBags[bag.ownerDBID] = bag


	def addOperate( self, func, paramDict ):
		"""
		"""
		self.operateList.append( Operate( func, paramDict ) )
		if len( self.operateList ) == 1:
			self.doOperate()



	def startCollection( self, playerDBID ):
		"""
		define method
		开始收集
		"""
		collectionBag = self.getCollectionBag( playerDBID )
		collectionBag.start()

	def stopCollection( self, playerDBID ):
		"""
		define method
		结束收集
		"""
		collectionBag = self.getCollectionBag( playerDBID )
		collectionBag.stop()

	def addCollectionItem( self, collectionItem, playerBase ):
		"""
		define method
		增加一个收集物品
		"""
		#self._addCollectionItem( collectionItem, playerBase )

		self.addOperate( self._addCollectionItem, {"item": collectionItem, "baseMB": playerBase } )


	def _addCollectionItem( self, paramDict ):
		"""
		增加一个收集物品
		"""
		collectionItem 	= paramDict["item"]
		playerBase		= paramDict["baseMB"]
		collectionBag = self.getCollectionBag( collectionItem.collectorDBID )
		if collectionBag.isFull():
			playerBase.client.onStatusMessage( csstatus.COLLECTION_ITEM_FULL, "" )
			return

		if not collectionItem.isValid():
			return

		playerBase.cell.onAddCollectionItem( collectionItem )

	def onAddCollectionItem( self, collectionItem, playerBase ):
		"""
		define method
		成功增加一个收集物品
		"""
		collectionBag = self.getCollectionBag( collectionItem.collectorDBID )
		collectionBag.add( collectionItem )
		playerBase.client.onAddCollectionItem( collectionItem )
		self.finishOperate()


	def removeCollectionItem( self, uid, playerDBID, playerBase ):
		"""
		define method
		移除一个收集物品
		"""
		self.addOperate( self._removeCollectionItem, {"uid": uid, "dbid": playerDBID, "baseMB": playerBase } )


	def _removeCollectionItem( self, paramDict ):
		"""
		移除一个收集物品
		"""
		playerDBID 	= paramDict["dbid"]
		uid			= paramDict["uid"]
		playerBase	= paramDict["baseMB"]

		collectionBag = self.getCollectionBag( playerDBID )
		item = collectionBag.get( uid )
		if item:
			playerBase.cell.onRemoveCollectionItem( item )


	def onRemoveCollectionItem( self, uid, playerDBID, playerBase ):
		"""
		define method
		成功移除一个物品
		"""
		collectionBag = self.getCollectionBag( playerDBID )
		collectionBag.remove( uid )
		playerBase.client.onRemoveCollectionItem( uid )
		self.finishOperate()

	def takeCollectedItems( self, playerDBID, playerBase ):
		"""
		define method
		取走收集到的物品
		"""
		self.addOperate( self._takeCollectedItems, {"dbid": playerDBID, "baseMB": playerBase } )


	def _takeCollectedItems( self, paramDict ):
		"""
		取走收集到的物品
		"""
		playerDBID = paramDict["dbid"]
		playerBase = paramDict["baseMB"]

		collectionBag = self.getCollectionBag( playerDBID )
		playerBase.cell.onTakeCollectedItems( collectionBag.takeItems() )


	def onTakeCollectedItems( self, playerDBID, playerBase ):
		"""
		define method
		玩家取走物品返回。
		param result:
			@type	bool
		"""
		collectionBag = self.getCollectionBag( playerDBID )
		collectionBag.onTaked()
		self.queryCollectionInfo( playerDBID, playerBase )
		self.finishOperate()


	def getCollectionBag( self, playerDBID ):
		"""
		获得角色收集包
		"""
		if not playerDBID in self.collectionBags:
			self.collectionBags[playerDBID] = CollectionBag( playerDBID, self.db )

		return self.collectionBags[playerDBID]


	def queryCollectionInfo( self, playerDBID, playerBase ):
		"""
		define method
		查询收集界面
		"""
		collectionBag = self.getCollectionBag( playerDBID )
		playerBase.client.onClearCollectionTable( playerDBID )
		for i in collectionBag.items.itervalues():
			playerBase.client.onReceiveCollectionItem( playerDBID, i )

	def updateCollectionItem( self, collectionItem, playerBase ):
		"""
		define method
		更新收购物品信息
		#不允许收购到的物品更新任何信息。
		"""
		self.addOperate( self._updateCollectionItem, {"collectionItem": collectionItem, "baseMB": playerBase } )

	def _updateCollectionItem( self, paramDict ):
		"""
		define method
		更新收购物品信息
		"""
		collectionItem 	= paramDict["collectionItem"]
		playerBase		= paramDict["baseMB"]
		
		
		collectionBag = self.getCollectionBag( collectionItem.collectorDBID )
		srcCollectionItem = collectionBag.get( collectionItem.uid )
		if collectionBag:
			if srcCollectionItem is not None:
				playerBase.cell.onUpdateCollectionItem( srcCollectionItem,  collectionItem )


	def onUpdateCollectionItem( self, collectionItem, playerBase ):
		"""
		define method
		"""
		collectionBag = self.getCollectionBag( collectionItem.collectorDBID )
		if collectionBag.update( collectionItem ):
			playerBase.client.onUpdateCollectionItem( collectionBag.get( collectionItem.uid ) )
		self.finishOperate()

	def sellCollectionItems( self, collectionItems, collectorDBID, playerBase ):
		"""
		define method
		出售替售物品
		"""
		if not collectorDBID in self.collectionBags:
			return

		self.addOperate( self._sellCollectionItems, {"items": collectionItems, "dbid":collectorDBID, "baseMB": playerBase } )


	def _sellCollectionItems( self, paramDict ):
		"""
		出售替售物品
		"""
		collectionItems = paramDict["items"]
		collectorDBID	= paramDict["dbid"]
		playerBase		= paramDict["baseMB"]

		collectionBag = self.getCollectionBag( collectorDBID )

		items = collectionBag.check( collectionItems )

		if len( items ) == 0:
			self.queryCollectionInfo( collectorDBID, playerBase )
			playerBase.client.onStatusMessage( csstatus.COLLECTION_ITEM_INFO_CHANGED, "" )
			return
		playerBase.cell.onSellCollectionItems( collectionItems, collectorDBID )



	def onSellCollectionItems( self,  collectionItems, collectorDBID, playerBase ):
		"""
		define method
		成功出售替售物品
		"""
		collectionBag = self.getCollectionBag( collectorDBID )
		collectionBag.onSell( collectionItems )
		self.queryCollectionInfo( collectorDBID, playerBase )
		self.finishOperate()


	def clear( self ):
		"""
		清空
		"""
		self.collectionBags = {}
		self.db.clearTable()

	def takeCollectionDeposit( self, collectorDBID, playerBase ):
		"""
		define method
		取回收购押金
		备注：替售NPC销毁后，玩家可以通过这个接口取回收购预付的押金
		"""
		self.addOperate( self._takeCollectionDeposit, {"dbid":collectorDBID, "baseMB": playerBase } )

	def _takeCollectionDeposit( self, paramDict ):
		"""
		"""
		playerBase 		= paramDict["baseMB"]
		collectorDBID	= paramDict["dbid"]
		
		bag = self.getCollectionBag(collectorDBID)
		if bag:
			money = bag.getTotalPrice()
			playerBase.cell.onTakeCollectionDeposit( money )

	def onTakeCollectionDeposit( self, collectorDBID ):
		"""
		define method
		"""
		if collectorDBID in self.collectionBags:
			self.collectionBags[collectorDBID].onTakeDeposit()


	def queryCollectionDeposit( self, playerBaseMB, playerDBID ):
		"""
		define method
		"""
		if playerDBID in self.collectionBags:
			bag = self.getCollectionBag( playerDBID )
			if not bag.isEmpty():
				playerBaseMB.cell.onNoticeCollectionOver()


	def doOperate( self ):
		"""
		执行操作
		"""
		if len( self.operateList ) == 0:
			return
		self.lastOperate = self.operateList[0]
		self.operateList[0].do()
		self.cancelOperateTimerID = self.addTimer( MAX_OPERATE_ITEM, 0.0, OPERATE_CANCEL )

	def cancelOperate( self ):
		"""
		取消操作
		"""
		if len( self.operateList ) > 0:
			self.operateList.pop(0)
			self.doOperate()

	def finishOperate( self ):
		"""
		完成操作
		"""
		self.operateList.pop(0)
		self.doOperate()


	def onTimer( self, timerID, cbID ):
		"""
		"""
		if cbID == OPERATE_CANCEL:
			if self.cancelOperateTimerID == timerID:
				self.cancelOperate()


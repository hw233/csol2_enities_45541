# -*- coding: gb18030 -*-


import BigWorld
from Function import Functor
from bwdebug import *
import cPickle
import items
import csconst
import PetEpitome
import Math
import csstatus

CREATE_TISHOU_NPC_CBID	= 123445
CONTROL_SPEED_CBID		= 125458


TISHOU_TIME			= 24 * 3600


g_items = items.instance()

class TiShouMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体
		self.registerGlobally( "TiShouMgr", self._onRegisterManager )
		self.tishouUnit = {}				#保存管理器和各个替售NPC 的关联
		self.tempRoleItems 	= {}			#临时存储玩家物品数据
		self.tempRolePets 	= {}			#临时存储玩家宠物数据
		self.canOperate		= True

		self.addTimer( 60, 0.0, CREATE_TISHOU_NPC_CBID )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register TiShouMgr Fail!" )
			# again
			self.registerGlobally( "TiShouMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["TiShouMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("TiShouMgr Create Complete!")

	#---------------------------------- 接口 ---------------------------------------------------------
	def addTSItem( self, item, price, itemType, level, quality, metier, playerDBID, shopName, ownerName, npcID, roleProcess ):
		"""
		define method
		增加一个替售物品
		"""
		tempDict = item.addToDict()
		del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
		itemData = BigWorld.escape_string( cPickle.dumps( tempDict, 2 ) )
		shopName = BigWorld.escape_string( shopName )
		ownerName = BigWorld.escape_string( ownerName )

		query = "REPLACE INTO custom_TiShouItemTable ( sm_itemUID, sm_tishouItem, sm_price, sm_itemType, sm_level, sm_quality, sm_metier, sm_roleDBID, sm_roleName, sm_shopName, sm_itemName, sm_roleProcess, sm_tsState )Value( %d, \'%s\',%d , %d, %d, %d, \'%s\', %d, \'%s\', \'%s\', \'%s\', %d, %d )"% ( item.uid, itemData, price, itemType, level, quality, metier, playerDBID, ownerName, shopName, item.name(), roleProcess, 0  )
		#query = "insert into custom_TiShouItemTable ( sm_itemUID, sm_tishouItem, sm_price, sm_itemType, sm_level, sm_quality, sm_metier, sm_roleDBID, sm_roleName, sm_shopName, sm_itemName, sm_roleProcess, sm_tsState )Value ( %d, \'%s\',%d , %d, %d, %d, %d, %d, \'%s\', \'%s\', \'%s\', %d, %d )"% ( item.uid, itemData, price, itemType, level, quality, metier, playerDBID, ownerName, shopName, item.name(), roleProcess, 0  )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__addTSItemCB, item.uid, playerDBID ) )

		for i in self.tishouUnit:
			if i.id == npcID:
				if "item" in self.tishouUnit[i]:
					self.tishouUnit[i]["item"].append( item.uid )
				else:
					self.tishouUnit[i]["item"] = [item.uid]

	def removeTSItem( self, uid  ):
		"""
		define method
		移除一个替售物品
		"""
		query = "delete from custom_TiShouItemTable where sm_itemUID=%i;" % uid
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__removeTSItemCB, uid ) )


	def updateTSRecordMoney( self, ownerDBID, money ):
		"""
		define method
		更新玩家卖掉物品得到的金钱。
		"""
		query = "update custom_TiShouRecordTable set sm_tishouMoney = %d where sm_roleDBID = %i"%( money, ownerDBID )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onAddTSMoney, ownerDBID, money ) )
		
		if money != 0:
			BigWorld.lookUpBaseByDBID( "Role", ownerDBID, self.__updateRoleTiShouMoneyFlag )



	def updateTSItemPrice( self, uid, price, playerDBID ):
		"""
		define method
		更新替售物品的价格
		"""
		query = "update custom_TiShouItemTable set sm_price = %i where sm_roleDBID = %i and sm_itemUID = %i"%( price, playerDBID, uid )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onUpdateTSItemPrice, price, playerDBID, uid ) )


	def addTSPet( self, epitome, price, level, era, gender, matier, breed, ownerDBID, shopName, ownerName, npcID, roleProcess ):
		"""
		define method
		增加一个替售宠物
		"""
		petDict =  epitome.getDictFromObj( epitome )
		petData = BigWorld.escape_string( cPickle.dumps( petDict, 2 ) )

		shopName = BigWorld.escape_string( shopName )
		ownerName = BigWorld.escape_string( ownerName )
		query = "REPLACE INTO custom_TiShouPetTable ( sm_petDBID, sm_tishouPet, sm_price, sm_level, sm_era, sm_gender, sm_metier, sm_breed, sm_roleDBID, sm_roleName, sm_shopName, sm_roleProcess, sm_tsState  )Value ( %d, \'%s\',%d ,%d ,%d ,%d ,%d ,%d ,%d, \'%s\', \'%s\', %d, %d )"% ( epitome.databaseID, petData, price, level, era, gender, matier, breed, ownerDBID, ownerName, shopName, roleProcess, 0 )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__addTSPetCB, epitome.databaseID, ownerDBID ) )

		for i in self.tishouUnit:
			if i.id == npcID:
				if "pet" in self.tishouUnit[i]:
					self.tishouUnit[i]["pet"].append( epitome.databaseID )
				else:
					self.tishouUnit[i]["pet"] = [epitome.databaseID]


	def removeTSPet( self, dbid, playerDBID  ):
		"""
		define method
		移除一个替售宠物
		"""
		query = "delete from custom_TiShouPetTable where sm_petDBID=%i;" % dbid
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__removeTSPetCB, dbid, playerDBID ) )


	def updateTSPetPrice( self, dbid, price, ownerDBID ):
		"""
		define method
		更新替售宠物的价格
		"""
		query = "update custom_TiShouPetTable set sm_price = %i where sm_roleDBID = %i and sm_petDBID = %d"%( price, ownerDBID, dbid )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onUpdateTSPetPrice, price, ownerDBID, dbid ) )


	def addNewTiShou( self, roleDBID, roleName, shopName, startTime, npcClassName, mapName, position ):
		"""
		define method
		增加一条新的寄售信息
		"""
		query = "select sm_roleDBID from custom_TiShouRecordTable where sm_roleDBID = %i"%roleDBID
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onAddNewTiShou, roleDBID, roleName, shopName, startTime, npcClassName, mapName, position ) )
		


	def queryShopInfo( self, playerBase, page, params ):
		"""
		define method
		查找符合条件的玩家的商铺
		"""
		keyWord = params.get( csconst.TISHOU_SHOP_INFO, "" )
		minPos = page * csconst.TISHOU_SHOP_INFO_QUERY_PAGE_SIZE
		if keyWord == "":
			query = "select * from custom_TiShouTable limit %i,%i"%( minPos, csconst.TISHOU_SHOP_INFO_QUERY_PAGE_SIZE )
		else:
			param = '%' + keyWord + '%'
			query = "select * from custom_TiShouTable where sm_roleName like \'%s\' limit %i,%i"%( param, minPos, csconst.TISHOU_SHOP_INFO_QUERY_PAGE_SIZE )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onQueryShopInfo, playerBase ))


	def queryItemInfo( self, playerBase, page, params ):
		"""
		define method
		查找符合条件的物品
		"""
		lowerLevel = params.get( csconst.TISHOU_ITEM_LOWERLEVEL, 0 )
		upperLevel = params.get( csconst.TISHOU_ITEM_UPPERLEVEL, 150 )
		print lowerLevel, upperLevel
		if lowerLevel > upperLevel:
			return

		typeLimit = params.get( csconst.TISHOU_ITEM_TYPELIMIT, -1 )
		typeLimitStr = ""
		if typeLimit != -1:
			typeLimitStr = "and sm_itemType = %i"%typeLimit

		qaLimit = params.get( csconst.TISHOU_ITEM_QALIMIT, -1 )
		qaLimitStr = ""
		if qaLimit != -1:
			qaLimitStr = "and sm_quality = %i"%qaLimit

		metierLimit = params.get( csconst.TISHOU_ITEM_METIER, "" )
		metierLimitStr = ""
		if metierLimit != "":
			metierLimitStr = "and sm_metier like \'%s\'"%('%' + metierLimit + '%')


		keyWord = params.get( csconst.TISHOU_ITEM_NAME, "" )

		ownerLimit = params.get( csconst.TISHOU_OWNER_NAME, "" )
		ownerStr = ""
		if ownerLimit != "":
			ownerStr = "and sm_roleName = \'%s\'"%ownerLimit

		minPos = page * csconst.TISHOU_ITEM_INFO_QUERY_PAGE_SIZE
		if keyWord == "":
			query = "select * from custom_TiShouItemTable where sm_delFlag = 0 and sm_tsState = 1 and sm_level >= %d and sm_level <= %d %s %s %s %s limit %i,%i"%( lowerLevel, upperLevel, ownerStr, typeLimitStr, qaLimitStr, metierLimitStr,  minPos, csconst.TISHOU_ITEM_INFO_QUERY_PAGE_SIZE )
			print query
		else:
			param = '%' + keyWord + '%'
			query = "select * from custom_TiShouItemTable where sm_delFlag = 0 and sm_tsState = 1 and sm_itemName like \'%s\' and sm_level >= %d and sm_level <= %d %s %s %s %s limit %i,%i"%( param, lowerLevel, upperLevel,ownerStr, typeLimitStr, qaLimitStr, metierLimitStr,  minPos, csconst.TISHOU_ITEM_INFO_QUERY_PAGE_SIZE )
			print query
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onQueryItemInfo, playerBase ))

	def queryPetInfo( self, playerBase, page, params ):
		"""
		define method
		查找符合条件的宠物
		TISHOU_PET_LOWERLEVEL					= "petLLevel"		# 宠物等级下限
		TISHOU_PET_UPPERLEVEL					= "petULevel"		# 宠物等级上限
		TISHOU_PET_ERALIMIT						= "eraLimit"		# 第几代宠物
		TISHOU_PET_GENDERLIMIT					= "genderLimit"		# 宠物性别
		TISHOU_PET_METIERLIMIT					= "metierLimit"		# 宠物职业
		TISHOU_PET_BREEDLIMIT					= "breedLimit"		# 宠物繁殖与否
		"""

		lowerLevel = params.get( csconst.TISHOU_PET_LOWERLEVEL, 0 )
		upperLevel = params.get( csconst.TISHOU_PET_UPPERLEVEL, 150 )

		if lowerLevel > upperLevel:
			return

		eraLimit = params.get( csconst.TISHOU_PET_ERALIMIT, -1 )
		eraLimitStr = ""
		if eraLimit != -1:
			eraLimitStr = "and sm_era = %i"%eraLimit

		genderLimit = params.get( csconst.TISHOU_PET_GENDERLIMIT, -1 )
		genderLimitStr = ""
		if genderLimit != -1:
			genderLimitStr = "and sm_gender = %i"%genderLimit

		metierLimit = params.get( csconst.TISHOU_PET_METIERLIMIT, -1 )
		metierLimitStr = ""
		if metierLimit != -1:
			metierLimitStr = "and sm_metier = %i"%metierLimit

		breedLimit = params.get( csconst.TISHOU_PET_BREEDLIMIT, -1 )
		breedLimitStr = ""
		if breedLimit != -1:
			breedLimitStr = "and sm_breed = %i"%breedLimit

		ownerLimit = params.get( csconst.TISHOU_OWNER_NAME, "" )
		ownerStr = ""
		if ownerLimit != "":
			ownerStr = "and sm_roleName = \'%s\'"%ownerLimit

		minPos = page * csconst.TISHOU_PET_INFO_QUERY_PAGE_SIZE

		query = "select * from custom_TiShouPetTable where  sm_delFlag = 0 and sm_tsState = 1 and sm_level >= %d and sm_level <= %d %s %s %s %s %s limit %i,%i"%( lowerLevel, upperLevel, ownerStr, eraLimitStr, genderLimitStr, metierLimitStr, breedLimitStr, minPos, csconst.TISHOU_PET_INFO_QUERY_PAGE_SIZE )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onQueryPetInfo, playerBase ))

	def addTiShouUnit( self, npcBaseMB, ownerDBID ):
		"""
		define method
		"""
		self.tishouUnit[npcBaseMB] = {"ownerDBID":ownerDBID}
		
		query = "select sm_tishouMoney from custom_TiShouRecordTable where sm_roleDBID =%i"%ownerDBID
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onAddTiShouUnit, npcBaseMB ) )
		
		

	def buyTSItemFromTishouMgr( self, playerBaseMB, ownerDBID, uid, itemID , count, price ):
		"""
		define method
		"""
		npcMailbox = None
		for i in self.tishouUnit:
			if "item" in self.tishouUnit[i]:
				if uid in self.tishouUnit[i]["item"]:
					if self.tishouUnit[i]["ownerDBID"] == ownerDBID:
						playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_ITEM_NOT_BUY_SELF_ITEM, "" )
						return
					npcMailbox = i
					break
		if npcMailbox:
			playerBaseMB.cell.buyTSItem( uid, npcMailbox, itemID , count, price )

	def buyTSPetFromTishouMgr( self, playerBaseMB, ownerDBID, dbid, price ):
		"""
		define method
		"""
		npcMailbox = None
		for i in self.tishouUnit:
			if "pet" in self.tishouUnit[i]:
				if dbid in self.tishouUnit[i]["pet"]:
					if self.tishouUnit[i]["ownerDBID"] == ownerDBID:
						playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_PET_NOT_BUY_SELF_PET, ""  )
						return
					npcMailbox = i
					break
		if npcMailbox:
			playerBaseMB.cell.buyTSPet( dbid, npcMailbox, price )

	def removeUnit( self, id ):
		"""
		define method
		"""
		for i in self.tishouUnit:
			if i.id == id:
				ownerDBID = self.tishouUnit[i]["ownerDBID"]
				self.stopTS( ownerDBID )
				query = "delete from custom_TiShouTable where sm_roleDBID = %i " %ownerDBID
				BigWorld.executeRawDatabaseCommand( query, self.__onDelTiShouUnit )
				del self.tishouUnit[i]
				BigWorld.lookUpBaseByDBID( "Role", ownerDBID, self.__onTiShouEnd )
				break



	def queryTiShouData( self, npcBaseMB, ownerDBID ):
		"""
		define method
		"""
		query = "select * from custom_TiShouItemTable where  sm_delFlag = 0 and sm_roleDBID = %i " % ownerDBID
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onQueryTiShouItemData, npcBaseMB ) )

		query = "select * from custom_TiShouPetTable where  sm_delFlag = 0 and sm_roleDBID = %i " % ownerDBID
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onQueryTiShouPetData, npcBaseMB ) )


	def setTSItemDelFlag( self, uid, playerDBID, roleProcess ):
		"""
		define method
		设置寄售物品删除标志
		"""
		query = "update custom_TiShouItemTable set sm_roleProcess = %i, sm_delFlag = %i where sm_roleDBID = %i and sm_itemUID = %d"%( roleProcess, 1, playerDBID, uid )
		BigWorld.executeRawDatabaseCommand( query, self.__onSetTSItemDelFlag )


	def setTSPetDelFlag( self, dbid, playerDBID, roleProcess ):
		"""
		define method
		设置寄售物品删除标志
		"""
		query = "update custom_TiShouPetTable set sm_roleProcess = %i, sm_delFlag = %i where sm_roleDBID = %i and sm_petDBID = %d"%( roleProcess, 1, playerDBID, dbid )
		BigWorld.executeRawDatabaseCommand( query, self.__onSetTSPetDelFlag )



	def startTS( self, roleDBID ):
		"""
		开始寄售
		"""
		query = "update custom_TiShouItemTable set sm_tsState = %i where sm_roleDBID = %i "%( 1, roleDBID )
		BigWorld.executeRawDatabaseCommand( query, self.__onStartTS )
		query = "update custom_TiShouPetTable set sm_tsState = %i where sm_roleDBID = %i "%( 1, roleDBID )
		BigWorld.executeRawDatabaseCommand( query, self.__onStartTS )
		query = "update custom_TiShouTable set sm_tsState = %i where sm_roleDBID = %i "%( 1, roleDBID )
		BigWorld.executeRawDatabaseCommand( query, self.__onStartTS )

	def stopTS( self, roleDBID ):
		"""
		结束寄售
		"""
		query = "update custom_TiShouItemTable set sm_tsState = %i where sm_roleDBID = %i "%( 0, roleDBID )
		BigWorld.executeRawDatabaseCommand( query, self.__onStopTS )
		query = "update custom_TiShouPetTable set sm_tsState = %i where sm_roleDBID = %i "%( 0, roleDBID )
		BigWorld.executeRawDatabaseCommand( query, self.__onStopTS )
		query = "update custom_TiShouTable set sm_tsState = %i where sm_roleDBID = %i "%( 0, roleDBID )
		BigWorld.executeRawDatabaseCommand( query, self.__onStopTS )

	def takeTSMoneyFromTiShouMgr( self, mailbox, roleName, roleDBID ):
		"""
		define method
		"""
		if not self.speedCheck():
			return
		query = "select sm_tishouMoney from custom_TiShouRecordTable where sm_roleDBID =%i "%roleDBID
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onTakeTSMoneyFromTiShouMgr, mailbox ) )

	def takeTSItemFromTiShouMgr( self, mailbox, roleName, roleDBID ):
		"""
		define method
		玩家要求取走所有替售物品
		"""
		if not self.speedCheck():
			return
		for i in self.tishouUnit:
			if roleDBID == self.tishouUnit[i]["ownerDBID"]:
				mailbox.client.onStatusMessage( csstatus.TI_SHOU_ITEM_NPC_VALID, ""  )
				return
		query = "select * from custom_TiShouItemTable where  sm_delFlag = 0 and sm_tsState = 0 and sm_roleDBID = %i " % roleDBID
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onTakeTSItemFromTiShouMgr, mailbox ) )


	def roleHadTakeTishouItems( self, roleDBID, roleProcess ):
		"""
		define method
		玩家成功取走了所有替售物品
		"""
		query = "update custom_TiShouItemTable set sm_roleProcess = %i, sm_delFlag = %i where sm_roleDBID = %i"%( roleProcess, 1, roleDBID )
		BigWorld.executeRawDatabaseCommand( query, self.__onRoleHadTakeTishouItems )

	def takeTSPetFromTiShouMgr( self, mailbox, roleName, roleDBID ):
		"""
		define method
		玩家要求取走所有替售宠物
		"""
		if not self.speedCheck():
			return
		for i in self.tishouUnit:
			if roleDBID == self.tishouUnit[i]["ownerDBID"]:
				mailbox.client.onStatusMessage( csstatus.TI_SHOU_PET_NPC_VALID, ""  )
				return
		query = "select * from custom_TiShouPetTable where  sm_delFlag = 0 and sm_tsState = 0 and sm_roleDBID = %i " % roleDBID
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onTakeTSPetFromTiShouMgr, mailbox ) )


	def roleHadTakeTishouPets( self, roleDBID, roleProcess ):
		"""
		define method
		玩家成功取走了所有替售物品
		"""
		query = "update custom_TiShouPetTable set sm_roleProcess = %i, sm_delFlag = %i where sm_roleDBID = %i"%( roleProcess, 1, roleDBID )
		BigWorld.executeRawDatabaseCommand( query, self.__onRoleHadTakeTishouPets )

	def queryRoleTSFlag( self, playerBaseMB, playerDBID ):
		"""
		define method
		角色上线，查询替售标识
		"""
		for i in self.tishouUnit:
			if playerDBID == self.tishouUnit[i]["ownerDBID"]:
				playerBaseMB.cell.addTSFlag()
				return

	def playerCometoTiShouNpc( self,  playerBaseMB, playerDBID, way ):
		"""
		define method
		角色飞向替售NPC
		"""
		for i in self.tishouUnit:
			if playerDBID == self.tishouUnit[i]["ownerDBID"]:
				i.cell.takeOwnerToMe( playerBaseMB, way )
				return
		


	def speedCheck( self ):
		"""
		"""
		if self.canOperate:
			self.addTimer( 0.1, 0.0, CONTROL_SPEED_CBID )
			self.canOperate = False
			return True
		return False

	def updateShopName( self, shopName ):
		"""
		define method
		"""
		return
		#query = "update custom_TiShouTable set sm_shopName = \'%s\' where sm_roleName = \'%s\' "%( shopName, roleName )
		#BigWorld.executeRawDatabaseCommand( query, self.__onUpdateShopName )

	def onTiShouMoneyTaked( self, roleDBID ):
		"""
		define method
		玩家领取替售金钱后，回来确认
		"""
		self.updateTSRecordMoney( roleDBID, 0 )
		for i in self.tishouUnit:
			if roleDBID == self.tishouUnit[i]["ownerDBID"]:
				i.takeTiShouMoneyAway()
				return



	def queryTiShouInfo( self, playerBaseMB, roleDBID  ):
		"""
		上线查询替售金钱
		"""
		query = "select sm_tishouMoney from custom_TiShouRecordTable where sm_roleDBID =%i"%roleDBID
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onQueryTiShouInfo, playerBaseMB ) )

	def changeTiShouNPCModel( self, playerDBID, modelName ):
		"""
		define method
		更新替售NPC模型
		"""
		query = "update custom_TiShouTable set sm_npcClassName =\'%s\' where sm_roleDBID =%i"%( modelName, playerDBID )
		BigWorld.executeRawDatabaseCommand( query, self.__onChangeTiShouNPCModel )


	#---------------------------------- 私有方法 ---------------------------------------------------------
	def _createTiShouNPC( self ):
		"""
		"""
		query = "select * from custom_TiShouTable"
		BigWorld.executeRawDatabaseCommand( query, self.__onCreateTiShouNPC )


	#---------------------------------- 回调方法 ---------------------------------------------------------
	def __removeTSItemCB( self, uid, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: delete Item failed! Item uid: %i"%( uid ) )
			return
		return

	def __addTSItemCB( self, uid, playerDBID, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: add Item failed! playerDBID: %i, Item uid: %d"%( playerDBID, uid ) )
			return
		return

	def __onAddTSMoney( self, ownerDBID, price, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: update record failed! playerDBID: %i, money: %i"%( ownerDBID, price ) )
			return

	def __onUpdateTSItemPrice( self, price, playerDBID, uid, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: update item(uid:%d) price failed! playerDBID: %i, price: %i"%( uid, playerDBID, price ) )
			return

	def __addTSPetCB( self, dbid, ownerDBID, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: add pet failed! playerDBID: %i, Pet dbid: %d"%( ownerDBID, dbid ) )
			return
		return


	def __removeTSPetCB( self, dbid, playerDBID, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: delete TiShou Pet failed! playerDBID: %I, Pet dbid: %i"%( playerDBID, dbid ) )
			return
		return


	def __onUpdateTSPetPrice( self, price, playerDBID, dbid, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: update TiShou Pet(dbid:%d) price failed! playerDBID: %i, price: %i"%( dbid, playerDBID, price ) )
			return

	def __onAddNewTiShou( self, roleDBID, roleName, shopName, startTime, npcClassName, mapName, position, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: query new tishou Info failed! playerDBID is %s"%( roleDBID ) )
			return
		roleName = BigWorld.escape_string( roleName )
		shopName = BigWorld.escape_string( shopName )
		if len(result) == 0:
			query = "insert ignore into custom_TiShouRecordTable ( sm_roleName, sm_roleDBID, sm_tishouMoney )Value ( \'%s\',%i, %d )"% ( roleName, roleDBID,  0 )
			BigWorld.executeRawDatabaseCommand( query, Functor( self.__onInsertNewTiShou, roleDBID ))
		
		query = "insert ignore into custom_TiShouTable ( sm_roleDBID, sm_roleName, sm_shopName, sm_startTime, sm_npcClassName, sm_mapName, sm_position, sm_tsState )Value ( %d, \'%s\', \'%s\',%d,\'%s\',\'%s\',\'%s\', 0 )"% ( roleDBID, roleName, shopName, startTime, npcClassName, mapName, position)
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onInsertNewTiShou, roleDBID ))

	def __onInsertNewTiShou( self, playerDBID, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: insert new tishou Info failed! playerDBID is %s"%( playerDBID ) )
			return
	

	def __onQueryShopInfo( self, playerBase, result, dummy, errstr):
		"""
		表格格式：
			`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
			`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
			`sm_npcClassName`	text,
			`sm_tsState` 		BIGINT(20),
			`sm_startTime`		BIGINT(20),
			`sm_roleName`		text,
			`sm_shopName`	 	text,
			`sm_mapName`	 	text,
			`sm_position`	 	text,
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: query shop info failed! " )
			return
		for iList in result:
			startTime = int( iList[4] )
			if time.time() - int( startTime ) > TISHOU_TIME:
				return
			roleDBID 	= int(iList[1])
			roleName = iList[5]
			shopName = iList[6]
			playerBase.client.onReceiveQueryShopInfo( roleDBID, roleName, shopName )


	def __onQueryItemInfo( self, playerBase, result, dummy, errstr):
		"""
		表格格式：
			`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
			`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
			`sm_itemUID` 		BIGINT(20),
			`sm_tishouItem` 	blob,
			`sm_price`		 	BIGINT(20),
			`sm_itemType`		BIGINT(20),
			`sm_level`			BIGINT(20),
			`sm_quality`		BIGINT(20),
			`sm_metier`			BIGINT(20),
			`sm_roleName`		text,
			`sm_shopName`	 	text,
			`sm_itemName`	 	text,
			`sm_roleProcess` 	BIGINT(20),
			`sm_delFlag` 		BIGINT(20) NOT NULL default 0,
			`sm_tsState` 		BIGINT(20),
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: query item info failed!")
			return
		for iList in result:
			print iList
			roleDBID 	= int(iList[1])
			itemUID		= long(iList[2])
			itemDict 	= cPickle.loads( iList[3] )
			item 		= g_items.createFromDict( itemDict )
			item.uid	= itemUID
			price		= int(iList[4])
			roleName 	= iList[9]
			shopName 	= iList[10]
			playerBase.client.onReceiveQueryItemInfo( roleDBID, itemUID, item, price, roleName, shopName )


	def __onQueryPetInfo( self, playerBase, result, dummy, errstr):
		"""
		表格格式：
		`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
		`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
		`sm_petDBID` 		BIGINT(20),
		`sm_tishouPet` 		blob,
		`sm_price`		 	BIGINT(20),
		`sm_level`		 	BIGINT(20),
		`sm_era`		 	BIGINT(20),
		`sm_gender`		 	BIGINT(20),
		`sm_metier`		 	BIGINT(20),
		`sm_breed`		 	BIGINT(20),
		`sm_roleName`		text,
		`sm_shopName`	 	text,
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: query pet info failed!" )
			return
		for iList in result:
			roleDBID 	= int(iList[1])
			dbid		= int(iList[2])
			#petDict =  epitome.getDictFromObj( epitome )
			#petData = BigWorld.escape_string( cPickle.dumps( petDict, 2 ) )
			petDict		= cPickle.loads(iList[3])
			pet			= PetEpitome.PetEpitome().createObjFromDict( petDict )
			pet.updateAttr( "databaseID", dbid )
			price		= int(iList[4])
			roleName 	= iList[10]
			shopName 	= iList[11]
			playerBase.client.onReceiveQueryPetInfo( roleDBID, dbid, pet, price, roleName, shopName )

	def __onCreateTiShouNPC( self, result, dummy, errstr):
		"""
		`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
		`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
		`sm_npcClassName`	text,
		`sm_tsState` 		BIGINT(20),
		`sm_startTime`		BIGINT(20),
		`sm_roleName`		text,
		`sm_shopName`	 	text,
		`sm_mapName`	 	text,
		`sm_position`	 	text,
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: create npc failed!" )
			return
		for iList in result:
			roleDBID	 = int( iList[1] )
			modelNumber  = iList[2]
			tishouState	 = iList[3]
			startTime	 = iList[4]
			roleName	 = iList[5]
			shopName	 = iList[6]
			spaceName	 = iList[7]
			position	 = Math.Vector3( eval( iList[8] ) )

			if time.time() - int( startTime ) > TISHOU_TIME:
				self.stopTS( roleDBID  )
				query = "delete from custom_TiShouTable where sm_roleDBID = %i " %( roleDBID )
				BigWorld.executeRawDatabaseCommand( query, self.__onDelTiShouUnit )
				continue

			BigWorld.globalData["SpaceManager"].createNPCObjectFormBase( spaceName, csconst.TISHOU_NPC_CLASSNAME, position, (0, 0, 0), { "ownerDBID": roleDBID, "ownerName":roleName, "shopName": shopName, "destroyTime" : int( int( startTime ) + TISHOU_TIME ), "tsState" :int(tishouState), "modelNumber" : modelNumber, "initByMgr" : True  } )

	def __onQueryTiShouItemData( self, npcBaseMB, result, dummy, errstr):
		"""
		`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
		`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
		`sm_itemUID` 		BIGINT(20),
		`sm_tishouItem` 	blob,
		`sm_price`		 	BIGINT(20),
		`sm_itemType`		BIGINT(20),
		`sm_level`			BIGINT(20),
		`sm_quality`		BIGINT(20),
		`sm_metier`			BIGINT(20),
		`sm_roleName`		text,
		`sm_shopName`	 	text,
		`sm_itemName`	 	text,
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: npc query item failed!" )
			return
		myNpcBaseMB = None
		for mailbox in self.tishouUnit:
			if mailbox.id == npcBaseMB.id:
				myNpcBaseMB = mailbox
				break
		self.tishouUnit[myNpcBaseMB]["item"] = []

		for iList in result:
			roleDBID 	= int(iList[1])
			itemUID		= long(iList[2])
			itemDict 	= cPickle.loads( iList[3] )
			item 		= g_items.createFromDict( itemDict )
			item.uid	= itemUID
			price		= int(iList[4])
			itemType	= int(iList[5])
			level		= int(iList[6])
			quality		= int(iList[7])
			metier		= iList[8]
			roleName 	= iList[9]
			shopName 	= iList[10]

			self.tishouUnit[myNpcBaseMB]["item"].append( itemUID )


			npcBaseMB.initTSItem( item, price )



	def __onQueryTiShouPetData( self, npcBaseMB, result, dummy, errstr):
		"""
		`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
		`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
		`sm_petDBID` 		BIGINT(20),
		`sm_tishouPet` 		blob,
		`sm_price`		 	BIGINT(20),
		`sm_level`		 	BIGINT(20),
		`sm_era`		 	BIGINT(20),
		`sm_gender`		 	BIGINT(20),
		`sm_metier`		 	BIGINT(20),
		`sm_breed`		 	BIGINT(20),
		`sm_roleName`		text,
		`sm_shopName`	 	text,
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  npc query pet failed!" )
			return

		myNpcBaseMB = None
		for mailbox in self.tishouUnit:
			if mailbox.id == npcBaseMB.id:
				myNpcBaseMB = mailbox
				break
		self.tishouUnit[myNpcBaseMB]["pet"] = []

		for iList in result:
			roleDBID 	= int(iList[1])
			petDBID		= long(iList[2])
			petDict 	= cPickle.loads( iList[3] )
			pet 		= PetEpitome.PetEpitome().createObjFromDict( petDict )
			pet.updateAttr( "databaseID", petDBID )
			price		= int(iList[4])
			self.tishouUnit[myNpcBaseMB]["pet"].append( petDBID )
			npcBaseMB.initTSPet( pet, price, roleDBID )


	def __onSetTSItemDelFlag( self, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  set item DelFlag failed!" )
			return

	def __onSetTSPetDelFlag( self, result, dummy, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  set pet DelFlag failed!" )
			return


	def __onStartTS( self, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  start tishou failed!" )
			return

	def __onStopTS( self, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  stop tishou failed!" )
			return

	def __onTakeTSMoneyFromTiShouMgr( self,  mailbox, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  take money from tishoumgr failed!" )
			return
		if len( result ) == 0:
			mailbox.client.onStatusMessage( csstatus.TI_SHOU_NO_SELLED_MONEY, ""  )
			return
		money = int( result[0][0]  )
		if money == 0:
			mailbox.client.onStatusMessage( csstatus.TI_SHOU_NO_SELLED_MONEY, ""  )
			return
		mailbox.cell.addTSMoney( money )

	def __onQueryTiShouInfo( self,  mailbox, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  query tishou money failed!" )
			return
		if len( result ) == 0:
			return
		money = int( result[0][0]  )
		if money == 0:
			return
		mailbox.client.onStatusMessage( csstatus.TI_SHOU_HAS_SELLED_MONEY, ""  )


	def __onTakeTSItemFromTiShouMgr(self, mailbox, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  take item from tishoumgr failed!" )
			return
		if len( result ) == 0:
			mailbox.client.onStatusMessage( csstatus.TI_SHOU_ITEM_NOT_LEAVE, ""  )
			return
		items = []
		for iList in result:
			itemUID		= long(iList[2])
			itemDict 	= cPickle.loads( iList[3] )
			item 		= g_items.createFromDict( itemDict )
			item.uid	= itemUID
			items.append( item )
		mailbox.cell.testTakeTishouItems( items )


	def __onTakeTSPetFromTiShouMgr( self, mailbox, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  take pet from tishoumgr failed!" )
			return
		if len( result ) == 0:
			mailbox.client.onStatusMessage( csstatus.TI_SHOU_PET_NOT_LEAVE, ""  )
			return
		pets = []
		for iList in result:
			petDBID		= long(iList[2])
			petDict 	= cPickle.loads( iList[3] )
			pet 		= PetEpitome.PetEpitome().createObjFromDict( petDict )
			pet.updateAttr( "databaseID", petDBID )
			pets.append( pet )
		mailbox.cell.testTakeTishouPets( pets )

	def __onRoleHadTakeTishouItems( self, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  take items from tishoumgr failed!" )
			return

	def __onRoleHadTakeTishouPets( self, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  take pets from tishoumgr failed!" )
			return

	def __onDelTiShouUnit( self, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  del tishou unit failed!" )
			return

	def __onUpdateShopName( self, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  update tishou shopName failed!" )
			return


	def __onTiShouEnd( self, playerBase ):
		"""
		"""
		if playerBase == True or playerBase == False:
			pass
		else:
			playerBase.client.onStatusMessage( csstatus.TI_SHOU_OVER_NOTICE, ""  )

	def __onAddTiShouUnit( self, npcMB, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  add tishou unit failed!" )
			return
		if len( result ) > 0:
			npcMB.initTiShouMoney( int( result[0][0] ) )

	def __updateRoleTiShouMoneyFlag( self, callResult ):
		"""
		更新角色拥有替售金钱的标志
		"""
		if not isinstance( callResult, bool ):		# isinstance函数见python手册
			callResult.client.onStatusMessage( csstatus.TI_SHOU_HAS_SELLED_MONEY, ""  )


	def __onChangeTiShouNPCModel( self, result, dummy, errstr):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou:  update tishou npc model failed!" )
			return
		

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if cbID == CREATE_TISHOU_NPC_CBID:
			self._createTiShouNPC()

		if cbID == CONTROL_SPEED_CBID:
			self.canOperate = True
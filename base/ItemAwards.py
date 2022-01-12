# -*- coding: utf_8 -*-

import BigWorld
from bwdebug import *
from Function import Functor

class ItemAwards:
	"""
	物品奖励领取
	"""
	def __init__( self ):
		self.operationList = {}			# 处理中的物品数据列表
		self.isWorking = False			# 是否正在领取物品

	def readyWork( self, callBack ):
		if self.isWorking:
			callBack( [], 2 )
			return False
		self.isWorking = True
		return True

	def queryItemByAccount( self, account, callBack, playerName, databaseID ):
		"""
		跟据玩家账号获取所有物品
		"""
		if self.readyWork(callBack):
			sql = "select id,account,playerName,orderForm,itemId,amount,endTime,transactionID,remark from custom_ItemAwards where `account`='%s' and `endTime` >= UNIX_TIMESTAMP()" % account
			INFO_MSG( "%s(%s): %s"%( playerName, databaseID, sql ) )
			BigWorld.executeRawDatabaseCommand( sql, Functor( self.onQueryItem, callBack) )

	def queryItemByPlayerName( self, account, playerName, callBack, databaseID ):
		"""
		跟据玩家名称获取所有物品
		"""
		if self.readyWork(callBack):
			sql = "select id,account,playerName,orderForm,itemId,amount,endTime,transactionID,remark from custom_ItemAwards where `account`='%s' and `playerName`='%s' and `endTime` >= UNIX_TIMESTAMP()"%(account, playerName)
			INFO_MSG( "%s(%s): %s"%( playerName, databaseID, sql ) )
			BigWorld.executeRawDatabaseCommand( sql, Functor( self.onQueryItem, callBack) )

	def queryItemByOrder( self, account, order, callBack, playerName, databaseID ):
		"""
		跟据物品订单号获取所有物品
		"""
		if self.readyWork(callBack):
			sql = "select id,account,playerName,orderForm,itemId,amount,endTime,transactionID,remark from custom_ItemAwards where `account`='%s' and `orderform`='%s' and `endTime` >= UNIX_TIMESTAMP()"%(account, order)
			INFO_MSG( "%s(%s): %s"%( playerName, databaseID, sql ) )
			BigWorld.executeRawDatabaseCommand( sql, Functor( self.onQueryItem,  callBack) )
			
	def queryItemByANO( self, account, playerName, order, callBack, databaseID ):
		"""
		通过订单号、玩家账户、名字获取玩家的物品奖励
		"""
		if self.readyWork(callBack):
			sql = "select id,account,playerName,orderForm,itemId,amount,endTime,transactionID,remark from custom_ItemAwards where `orderform`='%s' and `account`='%s' and `playerName`='%s' and `endTime` >= UNIX_TIMESTAMP()"%(order, account, playerName)
			INFO_MSG( "%s(%s): %s"%( playerName, databaseID, sql ) )
			BigWorld.executeRawDatabaseCommand( sql, Functor( self.onQueryItem, callBack) )

	def onQueryItem( self, callBack, results, row, errstr):
		"""
		数据库返回了相应的数据
		"""
		ItemList = []	# 记录要发送的物品ID
		if errstr:
			ERROR_MSG( "get custom_ItemAwards table datas fault! %s" % errstr  )
			self.isWorking = False
			callBack( ItemList, 1)
			return
		if not results:
			self.isWorking = False
			callBack( ItemList, 1)
			return
		for result in results:
			id = result[0]
			if not self.operationList.has_key( id):
				self.operationList[id] = result[1:]
				ItemList.append( ( result[4], result[5]) )
		callBack( ItemList)

	def awardsSuccess( self, playerName, databaseID ):
		"""
		领取物品成功
		"""
		dbids = self.operationList.keys()
		dbidsTemp = []
		for dbid in dbids:
			dbidsTemp.append( "`id` = %s" % dbid )
		syntax = " or ".join( dbidsTemp )		#一次全部删除

		sql  = "DELETE FROM `custom_ItemAwards` WHERE %s" % syntax
		INFO_MSG( "%s(%s): %s"%( playerName, databaseID, sql ) )
		BigWorld.executeRawDatabaseCommand( sql, self._onAwardsSuccess )


	def _onAwardsSuccess( self, results, rows, errstr ):
		"""
		处理完毕后写日志和清理数据
		`id` bigint(20) NOT NULL AUTO_INCREMENT,
		`account` varchar(255) DEFAULT NULL,
		`playerName` varchar(255) DEFAULT NULL,
		`orderform` varchar(255) DEFAULT NULL,
		`itemId` varchar(255) DEFAULT NULL,
		`amount`  int unsigned DEFAULT 0,
		`endTime` int unsigned DEFAULT 0,
		"""
		if errstr:
			ERROR_MSG( "delete custom_ItemAwards table datas fault! %s" % errstr  )
			return
		
		for itemData in self.operationList.values():
			INFO_MSG( "awards success item:", itemData[0], itemData[1], itemData[2], itemData[3], itemData[4], itemData[6], itemData[7] )
			
		self.operationList = {}			# 处理中的物品数据列表
		self.isWorking = False			# 是否正在领取物品


	def awardsFailed( self ):
		"""
		领取失败
		"""
		self.operationList = {}			# 处理中的物品数据列表
		self.isWorking = False			# 是否正在领取物品
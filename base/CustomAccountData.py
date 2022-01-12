# -*- coding: gb18030 -*-
# $Id: CustomAccountData.py  hd

import BigWorld
from bwdebug import *
from Function import Functor

# 用户自定义的账号数据加载模块

class CustomAccountData:
	def __init__( self, accountName, accountDBID ):
		"""
		"""
		self.__acountDBID = accountDBID
		self.__accountName = accountName
		self.__data = {}

	def load( self, callback ):
		"""
		加载自定义数据
		"""
		sql = """(select `key`,`value` from `custom_AccountData`  where `parentID` = %s)
				union all ( select "gmtimelimit", `gmtimelimit` from bigworldLogOnMapping where `logOnName` =  "%s" )""" % ( self.__acountDBID, BigWorld.escape_string( self.__accountName ) )
		BigWorld.executeRawDatabaseCommand( sql, Functor( self.onGetData, callback) ) # 每一次登陆都去重新取出数据，以便动态更新

	def onGetData( self, callback, results, rows, errstr ):
		"""
		获取了数据库返回的数据
		"""
		if errstr:
			ERROR_MSG( "get custom_AccountData table datas fault! %s" % errstr  )
			return
		if results:
			for result in results:
				if not self.__data.has_key(result[0]):
					self.__data[result[0]] = result[1]
				else:
					ERROR_MSG( "account %s : key %s has aready exist!", self.__accountName, result[0] )
			callback()

	def query( self, key):
		"""
		返回指定的值
		"""
		if self.__data.has_key(key):
			return self.__data[key]
		else:
			return None

	def set( self, key, value):
		"""
		设置和修改账号公共数据
		"""
		isInsert = key not in self.__data
		self.__data[key] = value
		if isInsert:
			self.insertToDB( key, value )
		else:
			self.updateToDB( key, value )


	def updateToDB( self, key, value ):
		"""
		更新帐号公共数据
		"""

		query = "Update custom_AccountData set `value` = \'%s\' where parentID = %i and `key` = \'%s\';" % ( value, self.__acountDBID, key )
		BigWorld.executeRawDatabaseCommand( query, self.onUpdateToDB )
	
	
	def onUpdateToDB( self, result, dummy, errstr):
		"""
		更新帐号公共数据回调
		"""
		if errstr:
			ERROR_MSG( "account %s : update data wrong! error is %s.", self.__accountName, errstr )



	def insertToDB( self, key, value ):
		"""
		插入帐号公共数据
		"""
		query = "Insert into custom_AccountData ( `key`, `value`, parentID ) value ( \'%s\', \'%s\', %i);" % ( key, value, self.__acountDBID )
		BigWorld.executeRawDatabaseCommand( query, self.onInsertToDB )
	
	
	def onInsertToDB( self, result, dummy, errstr):
		"""
		插入帐号公共数据回调
		"""
		if errstr:
			ERROR_MSG( "account %s : insert data wrong! error is %s.", self.__accountName, errstr )